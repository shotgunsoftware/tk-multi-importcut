# Copyright (c) 2014 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.
import sgtk
from sgtk.platform.qt import QtCore
from .logger import get_logger
from .cut_diff import CutDiff, _DIFF_TYPES
from .cut_summary import CutSummary
import re
edl = sgtk.platform.import_framework("tk-framework-editorial", "edl")

_NOTE_FORMAT = """
*Total:* %s
*Cut Changes:* %s
*New:* %s
*Omitted:* %s
*Reinstated:* %s
*Repeated:* %s
*Need Rescan:* %s
*Description:*
%s
"""

class Processor(QtCore.QThread):
    """
    Processing thread. A worker instance is created at runtime, and is the owner
    of all the data.
    """
    # Pass through signals which will be redirected to
    # the worker instance created in the running thread, so signals
    # will be processed in the running thread
    new_edl                 = QtCore.Signal(str)
    reset                   = QtCore.Signal()
    set_busy                = QtCore.Signal(bool)
    step_done               = QtCore.Signal(int)
    new_sg_sequence         = QtCore.Signal(dict)
    new_sg_cut              = QtCore.Signal(dict)
    retrieve_sequences      = QtCore.Signal()
    retrieve_cuts           = QtCore.Signal(dict)
    show_cut_diff           = QtCore.Signal(dict)
    new_cut_diff            = QtCore.Signal(CutDiff)
    got_busy                = QtCore.Signal(int)
    got_idle                = QtCore.Signal()
    progress_changed        = QtCore.Signal(int)
    import_cut              = QtCore.Signal(str,dict,dict, str)

    def __init__(self):
        """
        Instantiate a new Processor
        """
        super(Processor, self).__init__()
        self._logger = get_logger()
        self._edl_cut = None

    @property
    def title(self):
        """
        Return a title, retrieved from the loaded EDL, if any
        """
        if self._edl_cut and self._edl_cut._edl:
            return self._edl_cut._edl.title
        return None

    @property
    def summary(self):
        """
        Return the current CutSummary instance
        """
        if self._edl_cut and self._edl_cut._summary:
            return self._edl_cut._summary
        return None

    @property
    def sg_entity(self):
        """
        Return the current Shotgun entity ( Sequence ) we are displaying cut 
        changes for
        """
        if self._edl_cut and self._edl_cut._sg_entity:
            return self._edl_cut._sg_entity
        return None
    @property
    def sg_new_cut(self):
        """
        Return the cut created in Shotgun
        """
        if self._edl_cut:
            return self._edl_cut._sg_new_cut
        return None
    @property
    def sg_new_cut_url(self):
        sg_new_cut = self.sg_new_cut
        if not sg_new_cut:
            return None
        return "%s/detail/%s/%s" % (
            self._edl_cut._app.shotgun.base_url,
            sg_new_cut["type"],
            sg_new_cut["id"],
        )

    @property
    def no_cut_for_sequence(self):
        return self._edl_cut._no_cut_for_sequence

    def run(self):
        """
        Run the processor
        - Create a EdlCut worker instance
        - Connect this processor signals to worker's ones
        - Then wait for events to process
        """
        self._edl_cut = EdlCut()
        # Orders we receive
        self.new_edl.connect(self._edl_cut.load_edl)
        self.reset.connect(self._edl_cut.reset)
        self.retrieve_sequences.connect(self._edl_cut.retrieve_sequences)
        self.retrieve_cuts.connect(self._edl_cut.retrieve_cuts)
        self.show_cut_diff.connect(self._edl_cut.show_cut_diff)
        self.import_cut.connect(self._edl_cut.do_cut_import)
        # Results we send
        self._edl_cut.step_done.connect(self.step_done)
        self._edl_cut.new_sg_sequence.connect(self.new_sg_sequence)
        self._edl_cut.new_sg_cut.connect(self.new_sg_cut)
        self._edl_cut.new_cut_diff.connect(self.new_cut_diff)
        self._edl_cut.got_busy.connect(self.got_busy)
        self._edl_cut.got_idle.connect(self.got_idle)
        self._edl_cut.progress_changed.connect(self.progress_changed)
        self.exec_()

class EdlCut(QtCore.QObject):
    """
    Worker which handles all data
    """
    step_done = QtCore.Signal(int)
    new_sg_sequence = QtCore.Signal(dict)
    new_sg_cut = QtCore.Signal(dict)
    new_cut_diff = QtCore.Signal(CutDiff)
    got_busy = QtCore.Signal(int)
    got_idle = QtCore.Signal()
    progress_changed = QtCore.Signal(int)

    def __init__(self):
        """
        Instantiate a new empty worker
        """
        super(EdlCut, self).__init__()
        self._edl = None
        self._sg_entity = None
        self._summary = None
        self._logger = get_logger()
        self._app = sgtk.platform.current_bundle()
        self._sg = self._app.shotgun
        self._ctx = self._app.context
        self._use_smart_fields = self._app.get_setting("use_smart_fields") or False
        self._sg_new_cut = None
        self._no_cut_for_sequence = False

    def process_edit(self, edit, logger):
        """
        Visitor used when parsing an EDL file
        
        :param edit: Current EditEvent being parsed
        :param logger: Editorial framework logger, not used
        """
        # Use our own logger rather than the framework one
        edl.process_edit(edit, self._logger)
        # Check things are right
        # Add empty properties
        edit._sg_version = None
        # Add some lambda to retrieve properties
        edit.get_shot_name = lambda : edit._shot_name
        edit.get_clip_name = lambda : edit._clip_name
        edit.get_sg_version = lambda : edit._sg_version
        # In this app, the convention is that clip names hold version names
        # which is not the case for other apps like tk-multi-importscan
        # where the version name is set with locators and clip name is used
        # for the source clip ...
        if edit._clip_name:
            edit.get_version_name = lambda : edit._clip_name.split(".")[0] # Strip extension, if any
        else:
            edit.get_version_name = lambda : None
        if not edit._shot_name:
            # Shot name was not retrieved from standard approach
            # try to extract it from comments which don't include any
            # known keywords
            prefered_match=None
            match=None
            for comment in edit.pure_comments:
                # Match :
                # * COMMENT : shot-name_001
                # * shot-name_001
                # Most recent patterns are cached by Python so we don't need
                # to worry about compiling it ourself for performances consideration
                m=re.match(r"\*(\s*COMMENT\s*:)?\s*([a-z0-9A-Z_-]+)$", comment)
                if m:
                    if m.group(1):
                        # Priority is given to matches from line beginning with
                        # * COMMENT
                        prefered_match=m.group(2)
                    else:
                        match=m.group(2)
                if prefered_match:
                    edit._shot_name=prefered_match
                elif match:
                    edit._shot_name=match
        if not edit.get_shot_name() and not edit.get_version_name():
            raise RuntimeError("Couldn't extract a shot name nor a version name, one of them is required")

    @QtCore.Slot(str)
    def reset(self):
        """
        Clear this worker, discarding all data
        """
        self._edl = None
        self._sg_entity = None
        self._summary = None
        self._sg_new_cut = None
        self._logger.info("Session discarded...")

    @QtCore.Slot(str)
    def load_edl(self, path):
        """
        Load an EDL file
        
        :param path: Full path to the EDL file
        """
        self._logger.info("Loading %s ..." % path)
        try:
            self._edl = edl.EditList(
                file_path=path,
                visitor=self.process_edit,
            )
            self._logger.info(
                "%s loaded, %s edits" % (
                    self._edl.title, len(self._edl.edits)
                )
            )
            if not self._edl.edits:
                self._logger.warning("Couldn't find any entry in %s" % (path))
                return
            # Consolidate what we loaded
            # Build a dictionary using versions names as keys
            versions_names = {}
            for edit in self._edl.edits:
                v_name = edit.get_version_name()
                if v_name:
                    # SG find method is case insensitive, don't have to worry
                    # about upper / lower case names match
                    # but we use lowerkeys keys
                    v_name = v_name.lower()
                    if v_name not in versions_names:
                        versions_names[v_name] = [edit]
                    else:
                        versions_names[v_name].append(edit)
            # Retrieve actual versions from SG
            if versions_names:
                sg_versions = self._sg.find(
                    "Version", [
                        ["project", "is", self._ctx.project],
                        ["code", "in", versions_names.keys()],
                    ],
                    ["code", "entity", "entity.Shot.code", "image"]
                )
                # And update edits with the SG versions retrieved
                for sg_version in sg_versions:
                    edits = versions_names.get(sg_version["code"].lower())
                    if not edits:
                        # Unlikely ... but who knows ...
                        raise RuntimeError(
                            "Retrieved Version %s from Shotgun, but didn't ask for it ..." % sg_version["code"]
                        )
                    for edit in edits:
                        edit._sg_version = sg_version
                        if not edit.get_shot_name() and sg_version["entity.Shot.code"] :
                            edit._shot_name = sg_version["entity.Shot.code"]
            self.retrieve_sequences()
            # Can go to next step
            self.step_done.emit(0)
        except Exception, e:
            self._edl = None
            self._logger.error("Couldn't load %s : %s" % (path, str(e)))


    @QtCore.Slot(str)
    def retrieve_sequences(self):
        """
        Retrieve all sequences for the current project
        """
        # Retrieve display names and colors for statuses
        sg_statuses = self._sg.find("Status", [], ["code", "name", "icon", "bg_color"])
        status_dict = {}
        for sg_status in sg_statuses:
            if sg_status["bg_color"]:
                r, g, b = sg_status["bg_color"].split(",")
                sg_status["_bg_hex_color"] = "#%02x%02x%02x" % (int(r), int(g), int(b))
            status_dict[sg_status["code"]] = sg_status
        self._logger.info("Retrieving Sequences for project %s ..." % self._ctx.project["name"])
        self.got_busy.emit(None)
        try:
            sg_sequences = self._sg.find(
                "Sequence",
                [["project", "is", self._ctx.project]],
                [ "code", "id", "sg_status_list", "image", "description"],
                order=[{"field_name" : "code", "direction" : "asc"}]
            )
            if not sg_sequences:
                raise RuntimeWarning("Couldn't retrieve any Sequence for project %s" % self._ctx.project["name"])
            for sg_sequence in sg_sequences:
                if sg_sequence["sg_status_list"] in status_dict:
                    sg_sequence["_display_status"] = status_dict[sg_sequence["sg_status_list"]]
                else:
                    sg_sequence["_display_status"] = sg_sequence["sg_status_list"]
                self.new_sg_sequence.emit(sg_sequence)
            self._logger.info("Retrieved %d Sequences." % len(sg_sequences))
        except Exception, e :
            self._logger.exception(str(e))
        finally:
            self.got_idle.emit()

    @QtCore.Slot(dict)
    def retrieve_cuts(self, sg_entity):
        """
        Retrieve all sequences for the current project
        """
        self._sg_entity = sg_entity
        # Retrieve display names and colors for statuses
        sg_statuses = self._sg.find("Status", [], ["code", "name", "icon", "bg_color"])
        status_dict = {}
        for sg_status in sg_statuses:
            if sg_status["bg_color"]:
                r, g, b = sg_status["bg_color"].split(",")
                sg_status["_bg_hex_color"] = "#%02x%02x%02x" % (int(r), int(g), int(b))
            status_dict[sg_status["code"]] = sg_status
        self._logger.info("Retrieving Sequences for project %s ..." % self._ctx.project["name"])
        self.got_busy.emit(None)
        try:
            sg_cuts = self._sg.find(
                "Cut",
                [["sg_sequence", "is", sg_entity]],
                [
                    "code",
                    "id",
                    "sg_status_list",
                    "image",
                    "description",
                    "created_by",
                    "updated_by",
                    "updated_at",
                    "created_at",
                ],
                order=[{"field_name" : "id", "direction" : "desc"}]
            )
            # If no cut, go directly to next step
            if not sg_cuts:
                self.show_cut_diff({})
                self.step_done.emit(2)
                self._no_cut_for_sequence = True
                return

            self._no_cut_for_sequence = False
            for sg_cut in sg_cuts:
                if sg_cut["sg_status_list"] in status_dict:
                    sg_cut["_display_status"] = status_dict[sg_cut["sg_status_list"]]
                else:
                    sg_cut["_display_status"] = sg_cut["sg_status_list"]
                self.new_sg_cut.emit(sg_cut)
            self._logger.info("Retrieved %d Cuts." % len(sg_cuts))
            self.step_done.emit(1)
        except Exception, e :
            self._logger.exception(str(e))
        finally:
            self.got_idle.emit()

    @QtCore.Slot(dict)
    def show_cut_diff(self, sg_cut):
        """
        Build a cut summary for the given Shotgun entity ( Sequence )
        - Retrieve all shots linked to the Shotgun entity
        - Retrieve all cut items linked to these shots
        - Reconciliate them with the current edit list previously loaded
        
        :param sg_entity: A Shotgun entity disctionary retrieved from Shotgun, 
                          typically a Sequence
        """
        self._logger.info("Retrieving cut summary for %s" % ( self._sg_entity["code"]))
        self.got_busy.emit(None)
        self._summary = CutSummary()
        self._summary.new_cut_diff.connect(self.new_cut_diff)
        try:
            # Handle the case where we don't have any cut specified
            # Grab the latest one ...
            if not sg_cut:
                # Retrieve cuts linked to the sequence, pick up the latest or approved one
                # Later, the UI will allow selecting it
                sg_cut = self._sg.find_one(
                    "Cut",
                    [["sg_sequence", "is", self._sg_entity]],
                    [],
                    order=[{"field_name" : "id", "direction" : "desc"}]
                )
            sg_cut_items = []
            if sg_cut:
                sg_cut_item_entity = self._app.get_setting("sg_cut_item_entity")
                # Retrieve all cut items linked to that cut
                sg_cut_items = self._sg.find(sg_cut_item_entity,
                    [["sg_cut", "is", sg_cut]], [
                        "sg_cut",
                        "sg_timecode_cut_in",
                        "sg_timecode_cut_out",
                        "sg_head_in",
                        "sg_tail_out",
                        "sg_cut_order",
                        "sg_cut_in",
                        "sg_cut_out",
                        "sg_link",
                        "sg_cut_duration",
                        "sg_fps",
                        "sg_version",
                        "sg_version.Version.code",
                        "sg_version.Version.entity",
                        "sg_version.Version.image",
                    ]
                )
                # Consolidate versions retrieved from cut items
                # Because of a bug in the Shotgun API, we can't use two levels of
                # redirection, with "sg_version.Version.entity.Shot.code",
                # to retrieve the Shot linked to the Version, a CRUD
                # error will happen if one of the CutItem does not have version linked
                sg_cut_item_version_ids = [ x["sg_version"]["id"] for x in sg_cut_items if x["sg_version"]]
                sg_cut_item_versions = {}
                if sg_cut_item_version_ids:
                    sg_cut_item_versions_list = self._sg.find(
                        "Version",
                        [["id", "in", sg_cut_item_version_ids]],
                        ["entity", "entity.Shot.code"],
                    )
                    # Index results with their SG id
                    for item_version in sg_cut_item_versions_list:
                        sg_cut_item_versions[item_version["id"]] = item_version
                # We match fields that we would have retrieved with a sg.find("Version", ... )
                for sg_cut_item in sg_cut_items:
                    if sg_cut_item["sg_version"]:
                        sg_cut_item["sg_version"]["code"] = sg_cut_item["sg_version.Version.code"]
                        sg_cut_item["sg_version"]["entity"] = sg_cut_item["sg_version.Version.entity"]
                        sg_cut_item["sg_version"]["image"] = sg_cut_item["sg_version.Version.image"]
                        item_version = sg_cut_item_versions.get(sg_cut_item["sg_version"]["id"])
                        if item_version:
                            sg_cut_item["sg_version"]["entity.Shot.code"] = item_version["entity.Shot.code"]
                        else:
                            sg_cut_item["sg_version"]["entity.Shot.code"] = None
            # Retrieve shots linked to the sequence
            sg_shots = self._sg.find(
                "Shot",
                [["sg_sequence", "is", self._sg_entity]],
                [
                    "code",
                    "sg_status_list",
                    "sg_head_in",
                    "sg_tail_out",
                    "sg_cut_in",
                    "sg_cut_out",
                    "smart_head_in",
                    "smart_tail_out",
                    "smart_cut_in",
                    "smart_cut_out",
                    "sg_cut_order",
                    "image"
                ],
            )
            for edit in self._edl.edits:
                shot_name = edit.get_shot_name()
                if not shot_name:
                    cut_diff = self._summary.add_cut_diff(
                        None,
                        sg_shot=None,
                        edit=edit,
                        sg_cut_item=None
                    )
                else:
                    lower_shot_name = shot_name.lower()
                    existing = self._summary.diffs_for_shot(shot_name)
                    # Is it a duplicate ?
                    if existing:
                        self._logger.debug("Found duplicated shot shot %s (%s)" % (shot_name, existing))
                        cut_diff = self._summary.add_cut_diff(
                            shot_name,
                            sg_shot=existing[0].sg_shot,
                            edit=edit,
                            sg_cut_item=self.sg_cut_item_for_shot(
                                sg_cut_items,
                                existing[0].sg_shot,
                                edit.get_sg_version())
                        )
                    else :
                        # Do we have a matching shot in SG ?
                        matching_shot = None
                        matching_cut_item = None
                        for sg_shot in sg_shots:
                            if sg_shot["code"].lower() == lower_shot_name:
                                # yes we do
                                self._logger.debug("Found matching existing shot %s" % shot_name)
                                matching_shot = sg_shot
                                # Remove this entry from the list
                                sg_shots.remove(sg_shot)
                                break
                        # Do we have a matching cut item ?
                        if matching_shot:
                            matching_cut_item = self.sg_cut_item_for_shot(
                                sg_cut_items,
                                matching_shot,
                                edit.get_sg_version(),
                            )
                        cut_diff = self._summary.add_cut_diff(
                            shot_name,
                            sg_shot=matching_shot,
                            edit=edit,
                            sg_cut_item=matching_cut_item
                        )
            # Process now all sg shots leftover
            for sg_shot in sg_shots:
                # Don't show omitted shots which are not in this cut
                if sg_shot["sg_status_list"] != "omt":
                    matching_cut_item = self.sg_cut_item_for_shot(sg_cut_items, sg_shot)
                    cut_diff = self._summary.add_cut_diff(
                        sg_shot["code"],
                        sg_shot=sg_shot,
                        edit=None,
                        sg_cut_item=matching_cut_item
                    )
            self.step_done.emit(2)
            self._logger.info("Retrieved %d cut differences." % len(self._summary))
        except Exception, e :
            self._logger.exception(str(e))
        finally:
            self.got_idle.emit()

    def sg_cut_item_for_shot(self, sg_cut_items, sg_shot, sg_version=None):
        """
        Return a cut item for the given shot from the given list
        retrieved from Shotgun
        """
        potential_match = None
        for sg_cut_item in sg_cut_items:
            # Is it linked to the given shot ?
            if sg_cut_item["sg_link"] and sg_shot and \
                sg_cut_item["sg_link"]["id"] == sg_shot["id"] \
                and sg_cut_item["sg_link"]["type"] == sg_shot["type"]:
                    # We can have multiple cut items for the same shot
                    # use the linked version to pick the right one, if
                    # available
                    if not sg_version: # No particular version to match
                        return sg_cut_item
                    if sg_cut_item["sg_version"] and \
                        sg_version["id"] == sg_cut_item["sg_version"]["id"]: # Perfect match
                        return sg_cut_item
                    # Will keep looking around but we keep a reference to cut item
                    # linked to the same shot
                    potential_match = sg_cut_item
        return potential_match
    
    @QtCore.Slot(str, dict, dict, str)
    def do_cut_import(self, title, sender, to, description):
        """
        Import the cut changes in Shotgun
        """
        self._logger.info("Importing cut %s" % title)
        self.got_busy.emit(4)
        try:
            self._sg_new_cut = self.create_sg_cut(title)
            self.update_sg_shots()
            self.progress_changed.emit(1)
            self.update_sg_versions()
            self.progress_changed.emit(2)
            self.create_sg_cut_items(self._sg_new_cut)
            self.progress_changed.emit(3)
            self._logger.info("Creating note ...")
            self.create_note(title, sender, to, description, sg_links=[self._sg_new_cut])
            self.progress_changed.emit(4)
        except Exception, e :
            self._logger.exception(str(e))
        else:
            self._logger.info("Cut %s imported" % title)
            # Can go to next step
            self.step_done.emit(3)
        finally:
            self.got_idle.emit()

    def create_note(self, title, sender, to, description, sg_links=None):
        """
        Create a note in Shotgun, linked to the current Shotgun entity, and
        optionally linked to the list of sg_links
        
        :param title: A title for the note
        :param sender: A Shotgun user dictionary
        :param sender: A Shotgun group dictionary
        :param description: Some comments which will be added to the note
        :param sg_linkgs: A list of Shotgun entity dictionaries to link the note to
        """
        summary = self._summary
        links = ["%s/detail/%s/%s" % (
            self._app.shotgun.base_url,
            self._sg_entity["type"],
            self._sg_entity["id"],
        )]
        if sg_links:
            links += ["%s/detail/%s/%s" % (
                self._app.shotgun.base_url,
                sg_link["type"],
                sg_link["id"],
            ) for sg_link in sg_links]
        subject, body = summary.get_report(title, links)
#        contents = _NOTE_FORMAT % (
#            len(summary),
#            summary.count_for_type(_DIFF_TYPES.CUT_CHANGE),
#            summary.count_for_type(_DIFF_TYPES.NEW),
#            summary.count_for_type(_DIFF_TYPES.OMITTED),
#            summary.count_for_type(_DIFF_TYPES.REINSTATED),
#            summary.repeated_count,
#            summary.rescans_count,
#            description
#        )
        contents = "%s\n%s" % (description, body)
        data = {
            "project" : self._ctx.project,
            "subject" : subject,
            "content": contents,
            "note_links": [self._sg_entity] + (sg_links if sg_links else []),
            "created_by" : sender or None, # Ensure we send None if we got an empty dict
            "user" : sender or None,
            "addressings_to" : [to],
        
        }
        self._app.shotgun.create("Note", data)


    def create_sg_cut(self, title):
        """
        Create a Cut in Shotgun, linked to the current Sequence
        """
        # Create a new cut
        self._logger.info("Creating cut %s ..." % title)
        sg_cut = self._sg.create(
            "Cut", {
                "project" : self._ctx.project,
                "code" : title,
                "sg_sequence" : self._sg_entity,
                "created_by" : self._ctx.user,
                "updated_by" : self._ctx.user,
            },
            ["id", "code"])
        return sg_cut

    def update_sg_shots(self):
        """
        Update shots in Shotgun
        - Create them if needed
        - Change their status
        - Update cut in, cut out values
        """
        self._logger.info("Updating shots ...")
        sg_batch_data = []
        reinstate_status = self._app.get_setting("reinstate_status")
        omit_statuses = self._app.get_setting("omit_statuses") or ["omt"]
        # Loop over all shots that we need to create
        for shot_name, items in self._summary.iteritems():
            # Handle shot duplicates :
            # - find earliest cut order
            # - find earliest cut in
            # - find latest cut out
            # - find a shot id ( should be the same for all entries )
            min_cut_order = None
            min_cut_in = None
            max_cut_out = None
            sg_shot = None
            for cut_diff in items:
                if sg_shot is None and cut_diff.sg_shot:
                    sg_shot = cut_diff.sg_shot
                edit = cut_diff.edit
                if edit and (min_cut_order is None or edit.id < min_cut_order):
                    min_cut_order = edit.id
                if cut_diff.new_cut_in is not None and ( min_cut_in is None or cut_diff.new_cut_in < min_cut_in):
                    min_cut_in = cut_diff.new_cut_in
                if cut_diff.new_cut_out is not None and ( max_cut_out is None or cut_diff.new_cut_out > max_cut_out):
                    max_cut_out = cut_diff.new_cut_out
            # Cut diff types should be the same for all repeated entries, except may be for
            # rescan / cut change, but we do the same thing in both cases, so it does not
            # matter, so arbitrarily use the first entry
            cut_diff = items[0]

            # Skip entries where the shot name couldn't be retrieved
            if cut_diff.diff_type == _DIFF_TYPES.NO_LINK:
                pass
            elif cut_diff.diff_type == _DIFF_TYPES.NEW:
                self._logger.info("Will create shot %s for %s" % (shot_name, self._sg_entity))
                data = {
                    "project" : self._ctx.project,
                    "code" : cut_diff.name,
                    "sg_sequence" : self._sg_entity,
                    "updated_by" : self._ctx.user,
                    "sg_cut_order" : min_cut_order,
                }
                if self._use_smart_fields:
                    data.update({
                        "smart_head_in" : cut_diff.default_head_in,
                        "smart_cut_in" : min_cut_in,
                        "smart_cut_out" : max_cut_out,
                        "smart_tail_out" : cut_diff.default_tail_out,
                    })
                else:
                    data.update({
                        "sg_head_in" : cut_diff.default_head_in,
                        "sg_cut_in" : min_cut_in,
                        "sg_cut_out" : max_cut_out,
                        "sg_tail_out" : cut_diff.default_tail_out,
                    })
                sg_batch_data.append({
                    "request_type" : "create",
                    "entity_type" : "Shot",
                    "data" : data
                })
            elif cut_diff.diff_type == _DIFF_TYPES.OMITTED:
                sg_batch_data.append({
                    "request_type" : "update",
                    "entity_type" : "Shot",
                    "entity_id" : sg_shot["id"],
                    "data" : {
                        "sg_status_list" : omit_statuses[-1], # Arbitrarily pick the last one
                        # Add code in the update so it will be returned with batch results
                        "code" : sg_shot["code"],
                    }
                })
            elif cut_diff.diff_type == _DIFF_TYPES.REINSTATED:
                data = {
                    "sg_status_list" : reinstate_status,
                    "sg_cut_order" : min_cut_order,
                    # Add code in the update so it will be returned with batch results
                    "code" : sg_shot["code"],
                }
                if self._use_smart_fields:
                    data.update({
                        "smart_cut_in" : min_cut_in,
                        "smart_cut_out" : max_cut_out,
                        "smart_tail_out" : cut_diff.new_tail_out,
                    })
                else:
                    data.update({
                        "sg_cut_in" : min_cut_in,
                        "sg_cut_out" : max_cut_out,
                    })
                sg_batch_data.append({
                    "request_type" : "update",
                    "entity_type" : "Shot",
                    "entity_id" : sg_shot["id"],
                    "data" : data
                })
            else: # Cut change or rescan or no change
                data = {
                    # Add code and status in the update so it will be returned with batch results
                    "sg_status_list" : sg_shot["sg_status_list"],
                    "sg_cut_order" : min_cut_order,
                    "code" : sg_shot["code"],
                }
                if self._use_smart_fields:
                    data.update({
                        "smart_cut_in" : min_cut_in,
                        "smart_cut_out" : max_cut_out,
                        "smart_tail_out" : cut_diff.new_tail_out,
                    })
                else:
                    data.update({
                        "sg_cut_in" : min_cut_in,
                        "sg_cut_out" : max_cut_out,
                    })
                sg_batch_data.append({
                    "request_type" : "update",
                    "entity_type" : "Shot",
                    "entity_id" : sg_shot["id"],
                    "data" : data
                })
        if sg_batch_data:
            res = self._sg.batch(sg_batch_data)
            self._logger.info("Created %d new shots." % len(res))
            # Update cut_diffs with the new shots
            for sg_shot in res:
                shot_name = sg_shot["code"].lower()
                if shot_name not in self._summary:
                    raise RuntimeError("Created shot %s, but couldn't retrieve it in our list" % shot_name)
                for cut_diff in self._summary[shot_name]:
                    if cut_diff.sg_shot:
                        # Update with new values
                        cut_diff.sg_shot.update(sg_shot)
                    else:
                        cut_diff._sg_shot = sg_shot

    def update_sg_versions(self):
        """
        Create versions in Shotgun for each shot which needs one
        """
        # Temporary helper to create versions in SG for initial
        # testing. Should be commented out before going into production
        # unless it becomes part of the specs
        self._logger.info("Updating versions ...")
        sg_batch_data = []
        for shot_name, items in self._summary.iteritems():
            for cut_diff in items:
                edit = cut_diff.edit
                if edit and not edit.get_sg_version() and edit.get_version_name():
                    sg_batch_data.append({
                        "request_type" : "create",
                        "entity_type" : "Version",
                        "data" : {
                            "project" : self._ctx.project,
                            "code" : edit.get_version_name(),
                            "entity": cut_diff.sg_shot,
                            "updated_by" : self._ctx.user,
                            "created_by" : self._ctx.user,
                            "entity" : cut_diff.sg_shot,
                        },
                        "return_fields" : [
                            "entity.Shot.code",
                        ]
                    })
        if sg_batch_data:
            res = self._sg.batch(sg_batch_data)
            self._logger.info("Created %d new versions." % len(res))
            for shot_name, items in self._summary.iteritems():
                for cut_diff in items:
                    edit = cut_diff.edit
                    if edit and not edit.get_sg_version():
                        # Creation order should match
                        cut_diff.set_sg_version(res.pop(0))

    def create_sg_cut_items(self, sg_cut):
        """
        Create the cut items in Shotgun, linked to the given cut
        """
        # Loop through all edits and create CutItems for them
        self._logger.info("Creating cut items ...")
        sg_batch_data = []
        cut_item_entity = self._app.get_setting("sg_cut_item_entity")
        for shot_name, items in self._summary.iteritems():
            for cut_diff in items:
                edit = cut_diff.edit
                if edit:
                    tc_cut_in = edit.source_in.to_frame()
                    sg_batch_data.append({
                        "request_type" : "create",
                        "entity_type" : cut_item_entity,
                        "data" : {
                            "project" : self._ctx.project,
                            "code" : edit.reel,
                            "sg_cut" : sg_cut,
                            "sg_cut_order" : edit.id,
                            "sg_timecode_cut_in" : str(edit.source_in),
                            "sg_timecode_cut_out" : str(edit.source_out),
                            "sg_timecode_edl_in" : str(edit.record_in),
                            "sg_timecode_edl_out" : str(edit.record_out),
                            "sg_cut_in" : cut_diff.new_cut_in,
                            "sg_cut_out" : cut_diff.new_cut_out,
                            "sg_head_in" : cut_diff.new_head_in,
                            "sg_tail_out" : cut_diff.new_tail_out,
                            "sg_cut_duration" : cut_diff.new_cut_out - cut_diff.new_cut_in + 1,
                            "sg_link" : cut_diff.sg_shot,
                            "sg_version" : edit.get_sg_version(),
                            "sg_fps" : self._edl.fps,
                            "created_by" : self._ctx.user,
                            "updated_by" : self._ctx.user,
                        }
                    })
        if sg_batch_data:
            self._sg.batch(sg_batch_data)
