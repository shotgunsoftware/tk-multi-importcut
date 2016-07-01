# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import re
import sgtk
from sgtk.platform.qt import QtCore
from .logger import get_logger
from .cut_diff import CutDiff, _DIFF_TYPES
from .cut_summary import CutSummary
from .entity_line_widget import EntityLineWidget

# Different wizard style steps in our process
from .constants import _DROP_STEP, _PROJECT_STEP, _ENTITY_TYPE_STEP, \
    _ENTITY_STEP, _CUT_STEP, _SUMMARY_STEP, _PROGRESS_STEP, _LAST_STEP
from .constants import _SHOT_FIELDS

edl = sgtk.platform.import_framework("tk-framework-editorial", "edl")

_ERROR_BAD_CUT = "%s contains CutItems with missing %s data. These timecode values are required to \
ensure an accurate comparison.\n\n Please select another Cut or update the timecode data in %s \
 to proceed."


class EdlCut(QtCore.QObject):
    """
    Worker which handles all data, our main data manager.
    
    After reading and validating an EDL file, the data manager will typically
    retrieve all SG Entites of a certain type linked to a chosen Project.
    Then, it will build a summary of cut differences against a SG Cut linked to one
    of these Entities.

    Signals are used to drive UI components running on other threads
    """
    # Emitted when a step is considered done, allowing for example to let the
    # UI knows that it can move on to next screen
    step_done            = QtCore.Signal(int)
    # Emitted when a step failed
    step_failed          = QtCore.Signal(int)

    # These signals allow the data manager to tell listeners that new data is available.
    # For example, views will create cards for the emitted data when the signals
    # are emitted
    # Emitted when a new Project was retrieved from SG
    new_sg_project       = QtCore.Signal(dict)
    # Emitted when a new Entity was retrieved from SG
    new_sg_entity        = QtCore.Signal(dict)
    # Emitted when a new Cut was retrieved from SG
    new_sg_cut           = QtCore.Signal(dict)
    # Emitted when a new CutDiff is available
    new_cut_diff         = QtCore.Signal(CutDiff)

    # Emitted when the data manager is busy doing something with an optional
    # integer when a "range" is known so a progress bar should be shown
    got_busy             = QtCore.Signal(int)
    # Emitted when the data manager is not busy anymore
    got_idle             = QtCore.Signal()
    # Emitted when the progress value changed
    progress_changed     = QtCore.Signal(int)
    # Emitted when the Cut summary totals should be recomputed, e.g. by the
    # Cut summary view
    totals_changed       = QtCore.Signal()
    # Emitted when some Cut Differences should be discarded, which can happen
    # when Shot names are edited in the summary view
    delete_cut_diff      = QtCore.Signal(CutDiff)
    # Emitted when an EDL was successfully loaded and is considered valid
    valid_edl            = QtCore.Signal(str)
    # Emitted to acknowledge we have a valid movie
    valid_movie          = QtCore.Signal(str)

    def __init__(self, frame_rate=None):
        """
        Instantiate a new empty worker, with the given explicit frame rate
        :param frame_rate: A float or None
        """
        super(EdlCut, self).__init__()

        self._edl_file_path = None
        self._mov_file_path = None
        self._edl = None
        self._sg_entity_type = None
        self._sg_shot_link_field_name = None
        self._sg_entity = None
        self._summary = None
        self._logger = get_logger()
        self._app = sgtk.platform.current_bundle()
        self._sg = self._app.shotgun
        self._ctx = self._app.context
        # we won't use context.project directly so we can change the Project if
        # we want (this is specifically for RV integration where it's possible to
        # launch without a Project context), but it's also possible to change
        # the project when context.project is available
        self._project = self._ctx.project
        self._sg_new_cut = None
        self._no_cut_for_entity = False
        # Retrieve some settings
        self._user_settings = self._app.user_settings
        # todo: this will need to be rethought if we're able to extract fps
        # from an EDL. Basically this is redundant now b/c the frame_rate coming
        # in is almost definitely set by user settings default_frame_rate
        if frame_rate is not None:
            self._frame_rate = frame_rate
        else:
            self._frame_rate = float(self._user_settings.retrieve("default_frame_rate"))
        self._update_shot_statuses = self._user_settings.retrieve("update_shot_statuses")
        self._use_smart_fields = self._user_settings.retrieve("use_smart_fields")
        self._omit_status = self._user_settings.retrieve("omit_status")
        self._reinstate_statuses = self._user_settings.retrieve("reinstate_shot_if_status_is")
        self._revision_num = 0

    @property
    def entity_name(self):
        """
        Return the name of the attached SG Entity
        :returns: A string or None
        """
        if not self._sg_entity:
            return None
        # Deal with name field not being consistent in SG
        return self._sg_entity.get(
            "code",
            self._sg_entity.get(
                "name",
                self._sg_entity.get("title", "????")
            )
        )

    @property
    def entity_type_name(self):
        """
        Return a nice name for the attached SG Entity's type
        :returns: A string or None
        """
        if not self._sg_entity:
            return None
        return sgtk.util.get_entity_type_display_name(
            sgtk.platform.current_bundle().sgtk,
            self._sg_entity["type"],
        )

    @property
    def has_valid_edl(self):
        """
        Return True if a valid EDL file was loaded
        :returns: A boolean
        """
        return bool(self._edl)

    @property
    def has_valid_movie(self):
        """
        Return True if a valid movie file was retrieved
        :returns: A boolean
        """
        return bool(self._mov_file_path)

    def process_edit(self, edit, logger):
        """
        Visitor used when parsing an EDL file

        Extract Shot / Version information from EDL edits and add lambdas
        to retrieve extracted properties

        :param edit: Current EditEvent being parsed
        :param logger: Editorial framework logger, not used
        """
        # Use our own logger rather than the framework one
        edl.process_edit(edit, self._logger)
        # Check things are right
        # Add empty properties
        edit._sg_version = None
        # Add some lambda to retrieve properties
        edit.get_shot_name = lambda: edit._shot_name
        edit.get_clip_name = lambda: edit._clip_name
        edit.get_sg_version = lambda: edit._sg_version
        # In this app, the convention is that clip names hold version names
        # which is not the case for other apps like tk-multi-importscan
        # where the version name is set with locators and clip name is used
        # for the source clip ...
        if edit._clip_name:
            edit.get_version_name = lambda: edit._clip_name.split(".")[0]  # Strip extension, if any
        else:
            edit.get_version_name = lambda: None
        if not edit._shot_name:
            # Shot name was not retrieved from standard approach
            # try to extract it from comments which don't include any
            # known keywords
            prefered_match = None
            match = None
            for comment in edit.pure_comments:
                # Match :
                # * COMMENT : shot-name_001
                # * shot-name_001
                # Most recent patterns are cached by Python so we don't need
                # to worry about compiling it ourself for performances consideration
                m = re.match(r"\*(\s*COMMENT\s*:)?\s*([a-z0-9A-Z_-]+)$", comment)
                if m:
                    if m.group(1):
                        # Priority is given to matches from line beginning with
                        # * COMMENT
                        prefered_match = m.group(2)
                    else:
                        match = m.group(2)
                if prefered_match:
                    edit._shot_name = prefered_match
                elif match:
                    edit._shot_name = match

    @QtCore.Slot(str)
    def reset(self):
        """
        Clear this worker, discarding all data
        """
        had_something = self._edl_file_path is not None
        self._edl_file_path = None
        self._mov_file_path = None
        self._edl = None
        self._sg_entity_type = None
        self._sg_shot_link_field_name = None
        self._sg_entity = None
        self._summary = None
        self._sg_new_cut = None
        if had_something:
            self._logger.info("Session discarded...")

    @QtCore.Slot(str, str)
    def process_edl_and_mov(self, edl_file_path, mov_file_path):
        """
        Process the given EDL and movie files

        :param edl_file_path: String, full path to EDL file.
        :param mov_file_path: String, full path to MOV file.
        """
        self.register_movie_path(mov_file_path)
        self.load_edl(edl_file_path)

    @QtCore.Slot(str)
    def register_movie_path(self, movie_file_path):
        """
        Register the given movie path

        :param movie_file_path: String, full path to MOV file.
        """
        self._mov_file_path = movie_file_path
        self._logger.info("Registered %s" % self._mov_file_path)
        self.valid_movie.emit(os.path.basename(self._mov_file_path))
        # If we have a valid EDL, we can move to next step
        if self.has_valid_edl:
            self.step_done.emit(_DROP_STEP)

    @QtCore.Slot(str)
    def load_edl(self, edl_file_path):
        """
        Load an EDL file.

        :param edl_file_path: A string, full path to the EDL file.
        """
        self._logger.info("Loading %s ..." % edl_file_path)
        try:
            self._edl_file_path = edl_file_path
            if self._frame_rate is not None:
                self._logger.info("Using explicit frame rate %f ..." % self._frame_rate)
                self._edl = edl.EditList(
                    file_path=edl_file_path,
                    visitor=self.process_edit,
                    fps=self._frame_rate,
                )
            else:
                self._logger.info("Using default frame rate ...")
                # Use default frame rate, whatever it is
                self._edl = edl.EditList(
                    file_path=edl_file_path,
                    visitor=self.process_edit,
                )
            self._logger.info(
                "%s loaded, %s edits" % (
                    self._edl.title, len(self._edl.edits)
                )
            )
            if not self._edl.edits:
                self._logger.warning("Couldn't find any entry in %s" % (edl_file_path))
                return
            # Can go to next step
            self.valid_edl.emit(os.path.basename(self._edl_file_path))
            if self.has_valid_movie:
                self.step_done.emit(_DROP_STEP)
        except Exception, e:
            self._edl = None
            self._edl_file_path = None
            self._logger.exception("Couldn't load %s: \n\n%s" % (edl_file_path, str(e)))

    def _bind_versions(self):
        """
        Bind SG Versions to loaded EDL edits
        """
        # Shouldn't happen, but raise an error if it does
        if not self._edl:
            raise RuntimeError("No EDL file is currently loaded")

        self._logger.info("Binding edits to %s's Versions" % self._project["name"])
        # Reset everything
        for edit in self._edl.edits:
            edit._sg_version = None

        # Consolidate loaded EDL data
        # Build a dictionary using versions names as keys
        versions_names = {}
        for edit in self._edl.edits:
            v_name = edit.get_version_name()
            if v_name:
                # SG find method is case insensitive, don't have to worry
                # about upper / lower case names match
                # but we use lowercase keys
                v_name = v_name.lower()
                if v_name not in versions_names:
                    versions_names[v_name] = [edit]
                else:
                    versions_names[v_name].append(edit)
        # Retrieve actual versions from SG
        if versions_names:
            sg_versions = self._sg.find(
                "Version", [
                    ["project", "is", self._project],
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
                        "Retrieved Version %s from Shotgun, but didn't ask for it ..." %
                        sg_version["code"]
                    )
                for edit in edits:
                    edit._sg_version = sg_version
                    # If we have a linked Version, its linked Shot takes precedence
                    # over shot names retrieved from locators, comments, etc...
                    if sg_version["entity.Shot.code"]:
                        edit._shot_name = sg_version["entity.Shot.code"]

    @QtCore.Slot(dict)
    def set_sg_project(self, sg_project):
        """
        Set the given Project as the active one

        Retrieve Versions from the Project and bind them to the edit entries

        :param sg_project: A SG Project dictionary
        """
        self._project = sg_project
        self._bind_versions()
        self.step_done.emit(_PROJECT_STEP)
        self._logger.info("Project %s activated..." % sg_project["name"])

    @QtCore.Slot(str)
    def retrieve_entities(self, entity_type):
        """
        Retrieve all Entities with the given type for the current Project

        :param entity_type: A Shotgun entity type name, e.g. "Sequence"
        """
        self._sg_entity_type = entity_type
        self._sg_shot_link_field_name = None
        # Retrieve display names and colors for statuses
        sg_statuses = self._sg.find("Status", [], ["code", "name", "icon", "bg_color"])
        status_dict = {}
        for sg_status in sg_statuses:
            if sg_status["bg_color"]:
                r, g, b = sg_status["bg_color"].split(",")
                sg_status["_bg_hex_color"] = "#%02x%02x%02x" % (int(r), int(g), int(b))
            status_dict[sg_status["code"]] = sg_status
        self._logger.info("Retrieving %ss for project %s..." % (
            entity_type, self._project["name"]))
        self.got_busy.emit(None)
        try:
            # Retrieve a "link" field on Shots which accepts our entity type
            shot_schema = self._sg.schema_field_read("Shot")
            # Prefer a sg_<entity type> field if available
            entity_type_name = sgtk.util.get_entity_type_display_name(
                sgtk.platform.current_bundle().sgtk, entity_type,
            )
            field_name = "sg_%s" % entity_type_name.lower()
            field = shot_schema.get(field_name)
            if field and field["data_type"]["value"] == "entity" and self._sg_entity_type in field["properties"]["valid_types"]["value"]:
                self._logger.debug("Using preferred shot field %s" % field_name)
                self._sg_shot_link_field_name = field_name
            else:
                # General lookup
                for field_name, field in shot_schema.iteritems():
                    if field["data_type"]["value"] == "entity":
                        if self._sg_entity_type in field["properties"]["valid_types"]["value"]:
                            self._sg_shot_link_field_name = field_name
                            break
            if not self._sg_shot_link_field_name:
                self._logger.warning("Couldn't retrieve a field accepting %s on shots" % (
                    self._sg_entity_type,
                ))
            else:
                self._logger.info("Will use field %s to link %s to shots" % (
                    self._sg_shot_link_field_name,
                    self._sg_entity_type
                ))
            if entity_type == "Project":
                sg_entities = self._sg.find("Project",
                                            [["id", "is", self._project["id"]]],
                                            ["name", "id", "sg_status", "image", "sg_description"],
                                            order=[{"field_name": "name", "direction": "asc"}]
                                            )
            else:
                sg_entities = self._sg.find(
                    entity_type,
                    [["project", "is", self._project]],
                    ["code", "name", "title", "id", "sg_status_list", "image", "description"],
                    order=[{"field_name": "code", "direction": "asc"}]
                )
            for sg_entity in sg_entities:
                # Project uses sg_status and not sg_status_list
                status = sg_entity.get("sg_status_list",
                                       sg_entity.get("sg_status", "")
                                       ) or ""
                # Register a display status if one available, with the color from SG
                if status in status_dict:
                    sg_entity["_display_status"] = status_dict[status]
                else:
                    # Project uses a list of strings, not actual statuses
                    sg_entity["_display_status"] = {
                        "name": status.title(),
                    }
                self.new_sg_entity.emit(sg_entity)
            self._logger.info("Retrieved %d %s." % (
                len(sg_entities),
                entity_type,
            ))
            self.step_done.emit(_ENTITY_TYPE_STEP)
        except Exception, e:
            self._logger.exception(str(e))
        finally:
            self.got_idle.emit()

    @QtCore.Slot()
    def retrieve_projects(self):
        """
        Retrieve all Projects for the Shotgun site
        """
        self.got_busy.emit(None)
        try:
            fields = ["name", "id", "sg_status", "image", "sg_description"]
            order = [{"field_name": "name", "direction": "asc"}]
            # todo: do we want to filter for active projects?
            sg_projects = self._sg.find(
                "Project",
                [["is_template", "is", False], ["archived", "is_not", True]],
                fields,
                order=order
            )
            self._logger.info("Retrieved %d Projects." % (len(sg_projects)))
            for sg_project in sg_projects:
                status = sg_project["sg_status"] or ""
                # Add a custom field with the status ready to be displayed
                sg_project["_display_status"] = {
                        "name": status.title(),
                }
                self.new_sg_project.emit(sg_project)
        except Exception, e:
            self._logger.exception(str(e))
        finally:
            self.got_idle.emit()

    @QtCore.Slot(dict)
    def retrieve_cuts(self, sg_entity):
        """
        Retrieve all Cuts for the given Shotgun entity
        :param sg_entity: A Shotgun entity dictionary, typically a Sequence
        """
        self._sg_entity = sg_entity
        entity_name = self._sg_entity.get(
            "code",
            self._sg_entity.get(
                "name",
                self._sg_entity.get("title", "")
            )
        )
        # Retrieve display names and colors for statuses
        sg_statuses = self._sg.find("Status", [], ["code", "name", "icon", "bg_color"])
        status_dict = {}
        for sg_status in sg_statuses:
            if sg_status["bg_color"]:
                r, g, b = sg_status["bg_color"].split(",")
                sg_status["_bg_hex_color"] = "#%02x%02x%02x" % (int(r), int(g), int(b))
            status_dict[sg_status["code"]] = sg_status
        self._logger.info("Retrieving Cuts for %s ..." % entity_name)
        self.got_busy.emit(None)
        try:
            sg_cuts = self._sg.find(
                "Cut",
                [["entity", "is", sg_entity]],
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
                    "revision_number"
                ],
                order=[{"field_name": "id", "direction": "desc"}]
            )
            # if sg_cuts is empty, set the revision number of this Cut to 1, else
            # take the highest revision number from all Cuts and increment by 1.
            max_revision = 0
            for cut in sg_cuts:
                if cut["revision_number"] > max_revision:
                    max_revision = cut["revision_number"]
            self._revision_num = max_revision + 1
            # self._logger.info(sg_cuts[len(sg_cuts) - 1]["code"])
            # If no cut, go directly to next step
            if not sg_cuts:
                self.show_cut_diff({})
                self._no_cut_for_entity = True
                return

            self._no_cut_for_entity = False
            for sg_cut in sg_cuts:
                # Register a display status if one available
                if sg_cut["sg_status_list"] in status_dict:
                    sg_cut["_display_status"] = status_dict[sg_cut["sg_status_list"]]
                else:
                    sg_cut["_display_status"] = sg_cut["sg_status_list"]
                self.new_sg_cut.emit(sg_cut)
            self._logger.info("Retrieved %d Cuts." % len(sg_cuts))
            self.step_done.emit(_ENTITY_STEP)
        except Exception, e:
            self._logger.exception(str(e))
        finally:
            self.got_idle.emit()

    @QtCore.Slot(dict)
    def show_cut_diff(self, sg_cut):
        """
        Build a cut summary for the current Shotgun entity (e.g. Sequence) and the given,
        potentially empty, Shotgun Cut.
        - Retrieve all shots linked to the Shotgun entity
        - Retrieve all cut items linked to the SG Cut, if a Cut is given
        - Reconciliate them with the current edit list previously loaded

        :param sg_cut: A Shotgun Cut dictionary retrieved from Shotgun, or an empty dictionary
        """
        self._logger.info("Retrieving cut summary for %s" % (self.entity_name))
        self.got_busy.emit(None)
        self._sg_cut = sg_cut

        # We've got an opportunity here to set the tc start/end values on
        # CutSummary, so lets do that so we can set it on the Cut record too
        tc_start = None
        tc_end = None
        if self._edl.edits:
            tc_start = self._edl.edits[0].record_in
            tc_end = self._edl.edits[-1].record_out
        self._summary = CutSummary(
            self._project,
            self._sg_entity,
            self._sg_shot_link_field_name,
            tc_start,
            tc_end,
        )
        # Connect CutSummary signals to ours as pass through, so any listener
        # on our signals will receive signals emitted by the CutSummary
        self._summary.new_cut_diff.connect(self.new_cut_diff)
        self._summary.delete_cut_diff.connect(self.delete_cut_diff)
        self._summary.totals_changed.connect(self.totals_changed)
        try:
            # Fields that we need to retrieve on Shots
            shot_fields = _SHOT_FIELDS
            if self._sg_shot_link_field_name:
                shot_fields.append(self._sg_shot_link_field_name)
            sg_cut_items = []
            sg_shots_dict = {}
            if sg_cut:
                # Retrieve all cut items linked to that cut
                sg_cut_items = self._sg.find("CutItem",
                                             [["cut", "is", sg_cut]], [
                                                "cut",
                                                "timecode_cut_item_in_text",
                                                "timecode_cut_item_out_text",
                                                "cut_order",
                                                "cut_item_in",
                                                "cut_item_out",
                                                "shot",
                                                "cut_duration",
                                                "cut_item_duration",
                                                "cut.Cut.fps",
                                                "version",
                                                "version.Version.code",
                                                "version.Version.entity",
                                                "version.Version.image",
                                                ]
                                             )
                # Consolidate versions retrieved from cut items
                # Because of a bug in the Shotgun API, we can't use two levels of
                # redirection, with "sg_version.Version.entity.Shot.code",
                # to retrieve the Shot linked to the Version, a CRUD
                # error will happen if one of the CutItem does not have version linked
                sg_cut_item_version_ids = [x["version"]["id"] for x in sg_cut_items if x["version"]]
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
                # We match fields that we would have retrieved with an sg.find("Version", ...)
                # And collect a list of shots while we loop over cut items.
                sg_known_shot_ids = set()
                for sg_cut_item in sg_cut_items:
                    reasons = []
                    if sg_cut_item["timecode_cut_item_in_text"] is None:
                        reasons.append("Timecode Cut In")
                    if sg_cut_item["timecode_cut_item_out_text"] is None:
                        reasons.append("Timecode Cut Out")
                    if reasons:
                        cut_name = sg_cut_item["cut"]["name"]
                        raise ValueError(_ERROR_BAD_CUT % (
                            cut_name, " and ".join(reasons), cut_name))
                    if sg_cut_item["shot"] and sg_cut_item["shot"]["type"] == "Shot":
                        sg_known_shot_ids.add(sg_cut_item["shot"]["id"])
                    if sg_cut_item["version"]:
                        sg_cut_item["version"]["code"] = sg_cut_item["version.Version.code"]
                        sg_cut_item["version"]["entity"] = sg_cut_item["version.Version.entity"]
                        sg_cut_item["version"]["image"] = sg_cut_item["version.Version.image"]
                        item_version = sg_cut_item_versions.get(sg_cut_item["version"]["id"])
                        if item_version:
                            sg_cut_item["version"]["entity.Shot.code"] = item_version["entity.Shot.code"]
                        else:
                            sg_cut_item["version"]["entity.Shot.code"] = None
                # Retrieve details for shots linked to the cut items
                if sg_known_shot_ids:
                    sg_shots = self._sg.find(
                        "Shot",
                        [["id", "in", list(sg_known_shot_ids)]],
                        shot_fields
                    )
                    # Build a dictionary where shot names are the keys, use the shot id
                    # if the name is not set
                    sg_shots_dict = dict(((x["code"] or str(x["id"])).lower(), x) for x in sg_shots)
            # Retrieve additional shots from the edits if needed
            more_shot_names = set()
            for edit in self._edl.edits:
                shot_name = edit.get_shot_name()
                if shot_name:
                    lower_shot_name = shot_name.lower()
                    if lower_shot_name not in sg_shots_dict:
                        more_shot_names.add(shot_name.lower())
            if more_shot_names:
                sg_more_shots = self._sg.find(
                    "Shot",
                    [["project", "is", self._project], ["code", "in", list(more_shot_names)]],
                    shot_fields,
                )
                for sg_shot in sg_more_shots:
                    shot_name = sg_shot["code"].lower()
                    sg_shots_dict[shot_name] = sg_shot
            # Duplicate the list of shots, allowing us to know easily which ones are not part
            # of this edit by removing entries when we use them. We only need a shallow copy
            # here
            leftover_shots = [x for x in sg_shots_dict.itervalues()]
            # Record the list of shots for completion purpose, we don't use the keys as
            # they are lower cased, but the original shot names
            EntityLineWidget.set_known_list(x["code"] for x in sg_shots_dict.itervalues() if x["code"])

            # Building a little dictionary for use in naming reels /
            # CutItem Name / code (whatever you want to call it).
            # Basically we add a 3 padded number to the end of any
            # reel that has a name which is duplicated, so we need an
            # iteration key and a dup key
            reel_names = {}
            for edit in self._edl.edits:
                if reel_names.get(edit.reel):
                    reel_names[edit.reel]["dup"] = True
                else:
                    reel_names[edit.reel] = {}
                    reel_names[edit.reel]["dup"] = False
                reel_names[edit.reel]["iter"] = 1

            for edit in self._edl.edits:
                if reel_names[edit.reel]["dup"] is True:
                    edit.reel_name = "%s%03d" % (
                        edit.reel,
                        reel_names[edit.reel]["iter"]
                    )
                    # Increment the iter counter for next one
                    reel_names[edit.reel]["iter"] += 1
                else:
                    edit.reel_name = edit.reel

                shot_name = edit.get_shot_name()
                if not shot_name:
                    # If we don't have a shot name, we can't match anything
                    cut_diff = self._summary.add_cut_diff(
                        None,
                        sg_shot=None,
                        edit=edit,
                        sg_cut_item=None
                    )
                else:
                    lower_shot_name = shot_name.lower()
                    self._logger.debug("Matching %s for %s" % (
                        lower_shot_name, str(edit),
                    ))
                    existing = self._summary.diffs_for_shot(shot_name)
                    # Is it a duplicate ?
                    if existing:
                        self._logger.debug("Found duplicated shot, shot %s (%s)" % (
                            shot_name, existing))
                        sg_cut_item = self.sg_cut_item_for_shot(
                            sg_cut_items,
                            existing[0].sg_shot,
                            edit.get_sg_version(),
                            edit
                        )
                        cut_diff = self._summary.add_cut_diff(
                            shot_name,
                            sg_shot=existing[0].sg_shot,
                            edit=edit,
                            sg_cut_item=sg_cut_item
                        )
                    else:
                        matching_cut_item = None
                        # Do we have a matching shot in SG ?
                        matching_shot = sg_shots_dict.get(lower_shot_name)
                        if matching_shot:
                            # yes we do
                            self._logger.debug("Found matching existing shot %s" % shot_name)
                            # Remove this entry from the leftovers
                            if matching_shot in leftover_shots:
                                leftover_shots.remove(matching_shot)
                            matching_cut_item = self.sg_cut_item_for_shot(
                                sg_cut_items,
                                matching_shot,
                                edit.get_sg_version(),
                                edit,
                            )
                        cut_diff = self._summary.add_cut_diff(
                            shot_name,
                            sg_shot=matching_shot,
                            edit=edit,
                            sg_cut_item=matching_cut_item
                        )

            # Process cut items left over
            for sg_cut_item in sg_cut_items:
                # If not compliant to what we expect, just ignore it
                if sg_cut_item["shot"] and sg_cut_item["shot"]["id"] and \
                    sg_cut_item["shot"]["type"] == "Shot":
                        shot_name = "No Link"
                        matching_shot = None
                        for sg_shot in sg_shots_dict.itervalues():
                            if sg_shot["id"] == sg_cut_item["shot"]["id"]:
                                # yes we do
                                self._logger.debug("Found matching existing shot %s" %
                                                   shot_name)
                                shot_name = sg_shot["code"]
                                matching_shot = sg_shot
                                # Remove this entry from the list
                                if sg_shot in leftover_shots:
                                    leftover_shots.remove(sg_shot)
                                break
                        cut_diff = self._summary.add_cut_diff(
                            shot_name,
                            sg_shot=matching_shot,
                            edit=None,
                            sg_cut_item=sg_cut_item
                        )

            # Now process all sg shots that are leftover
            for sg_shot in leftover_shots:
                # Don't show omitted shots which are not in this cut
                if sg_shot["sg_status_list"] not in self._reinstate_statuses:
                    # In theory we shouldn't have any leftover cut items ...
                    matching_cut_item = self.sg_cut_item_for_shot(sg_cut_items, sg_shot)
                    cut_diff = self._summary.add_cut_diff(
                        sg_shot["code"],
                        sg_shot=sg_shot,
                        edit=None,
                        sg_cut_item=matching_cut_item
                    )

            self._logger.info("Retrieved %d cut differences." % len(self._summary))
            self.step_done.emit(_CUT_STEP)
        except Exception, e:
            self._logger.exception(str(e))
        finally:
            self.got_idle.emit()

    def sg_cut_item_for_shot(self, sg_cut_items, sg_shot, sg_version=None, edit=None):
        """
        Return a cut item for the given shot from the given cut items list retrieved from Shotgun

        The sg_cut_items list is modified inside this method, entries being removed as
        they are chosen.

        Best matching cut item is returned, a score is computed for each entry
        from :
        - Is it linked to the right shot?
        - Is it linked to the right version?
        - Is the cut order the same?
        - Is the tc in the same?
        - Is the tc out the same?

        :param sg_cut_items: A list of CutItem instances to consider
        :param sg_shot: A SG shot dictionary
        :param sg_version: A SG version dictionary
        :param edit: An EditEvent instance or None
        :returns: A SG CutItem dictionary, or None
        """

        potential_matches = []
        for sg_cut_item in sg_cut_items:
            # Is it linked to the given shot ?
            if sg_cut_item["shot"] and sg_shot and \
                sg_cut_item["shot"]["id"] == sg_shot["id"] and \
                    sg_cut_item["shot"]["type"] == sg_shot["type"]:
                        # We can have multiple cut items for the same shot
                        # use the linked version to pick the right one, if
                        # available
                        if not sg_version:
                            # No particular version to match, score is based on
                            # on differences between cut order, tc in and out
                            # give score a bonus as we don't have an explicit mismatch
                            potential_matches.append((
                                sg_cut_item,
                                100 + self._get_cut_item_score(sg_cut_item, edit)
                                ))
                        elif sg_cut_item["version"]:
                                if sg_version["id"] == sg_cut_item["version"]["id"]:
                                    # Give a bonus to score as we matched the right
                                    # version
                                    potential_matches.append((
                                        sg_cut_item,
                                        1000 + self._get_cut_item_score(sg_cut_item, edit)
                                        ))
                                else:
                                    # Version mismatch, don't give any bonus
                                    potential_matches.append((
                                        sg_cut_item,
                                        self._get_cut_item_score(sg_cut_item, edit)
                                        ))
                        else:
                            # Will keep looking around but we keep a reference to cut item
                            # linked to the same shot
                            # give score a little bonus as we didn't have any explicit
                            # mismatch
                            potential_matches.append((
                                sg_cut_item,
                                100 + self._get_cut_item_score(sg_cut_item, edit)
                                ))
            else:
                self._logger.debug("Rejecting %s for %s" % ( sg_cut_item, edit))
        if potential_matches:
            potential_matches.sort(key=lambda x: x[1], reverse=True)
            for pm in potential_matches:
                self._logger.debug("Potential matches %s score %s" % (
                    pm[0], pm[1],
                ))
            # Return just the cut item, not including the score
            best = potential_matches[0][0]
            sg_cut_items.remove(best)  # Prevent this one to be used multiple times
            self._logger.debug("Best is %s for %s" % ( best, edit))
            return best
        return None

    def _get_cut_item_score(self, sg_cut_item, edit):
        """
        Return a matching score for the given cut item and edit, based on :
        - Is the cut order the same?
        - Is the tc in the same?
        - Is the tc out the same?

        So the best score is 3 if all matches

        :param sg_cut_item: a CutItem instance
        :param edit: An EditEvent instance
        :returns: A score, as an integer
        """
        if not edit:
            return 0
        score = 0
        # Compute the cut order difference
        diff = edit.id - sg_cut_item["cut_order"]
        if diff == 0:
            score += 1
        diff = edit.source_in - edl.Timecode(
                                    sg_cut_item["timecode_cut_item_in_text"],
                                    sg_cut_item["cut.Cut.fps"]
                                ).to_frame()
        if diff == 0:
            score += 1
        diff = edit.source_out - edl.Timecode(
                                    sg_cut_item["timecode_cut_item_out_text"],
                                    sg_cut_item["cut.Cut.fps"]
                                ).to_frame()

        if diff == 0:
            score += 1
        return score

    @QtCore.Slot(str, dict, dict, str, bool)
    def do_cut_import(self, title, sender, to, description, update_shots):
        """
        Import the cut changes in Shotgun
        - Create a new SG Cut
        - Create new SG CutItems
        - Create new SG Shots
        - Update existing SG Shots if update_shots is True
        - Create a Note in SG with a summary of changes

        :param title: A string, the new SG Cut name and a title for the Note 
                      that will be created
        :param sender: A SG user dictionary, the Note sender
        :param to: A SG Group dictionary, the recipient for the Note
        :param description: Comments as a string, used in the Note's body
        :param update_shots: A boolean, whether or not existing Shots data will
                             be updated
        """
        self._logger.info("Importing cut %s" % title)
        self.got_busy.emit(4)
        self.step_done.emit(_SUMMARY_STEP)
        try:
            self._sg_new_cut = self.create_sg_cut(title, description)
            self.update_sg_shots(update_shots)
            self.progress_changed.emit(1)
            # When testing this app it might be time consuming to create
            # all needed Versions in SG. If the following line is un-commented
            # it will create missing Versions for you, which can be handy for
            # testing
            # self._create_missing_sg_versions()
            self.progress_changed.emit(2)
            self.create_sg_cut_items(self._sg_new_cut)
            self.progress_changed.emit(3)
            self._logger.info("Creating note ...")
            self.create_note(title, sender, to, description, sg_links=[self._sg_new_cut])
            self.progress_changed.emit(4)
        except Exception, e:
            self._logger.exception(str(e))
            # Go back to summary screen
            self.step_failed.emit(_PROGRESS_STEP)
        else:
            self._logger.info("Cut %s imported" % title)
            # Can go to next step
            self.step_done.emit(_PROGRESS_STEP)
        finally:
            self.got_idle.emit()

    def create_note(self, title, sender, to, description, sg_links=None):
        """
        Create a note in Shotgun, linked to the current Shotgun entity, typically
        a Sequence and optionally linked to the list of sg_links

        :param title: A string, the Note title
        :param sender: A Shotgun user dictionary
        :param to: A Shotgun group dictionary
        :param description: Some comments which will be added to the Note
        :param sg_links: A list of Shotgun entity dictionaries to link the note to
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
        contents = "%s\n%s" % (description, body)
        data = {
            "project": self._project,
            "subject": subject,
            "content": contents,
            "note_links": [self._sg_entity] + (sg_links if sg_links else []),
            "created_by": sender or None,  # Ensure we send None if we got an empty dict
            "user": sender or None,
            "addressings_to": to,

        }
        self._app.shotgun.create("Note", data)

    def create_sg_cut(self, title, description):
        """
        Create a new Cut in Shotgun, linked to the current SG Entity

        If a movie was provided, create a new Version from it, linked to the
        new SG Cut.

        Upload the EDL file onto the new SG Cut

        :param title: A string, the new SG Cut name
        :param description: A string, a description for the Cut
        """
        # Create a new cut
        self._logger.info("Creating Cut %s ..." % title)
        # If start and end timecodes are not defined, we keep them as is,
        # so no value will be set when creating the Cut. We convert them
        # to string otherwise
        tc_start = self._summary.timecode_start
        if tc_start is not None:
            tc_start = str(tc_start)
        tc_end = self._summary.timecode_end
        if tc_end is not None:
            tc_end = str(tc_end)
        cut_payload = {
            "project"             : self._project,
            "code"                : title,
            "entity"              : self._sg_entity,
            "fps"                 : float(self._edl.fps),
            "created_by"          : self._ctx.user,
            "updated_by"          : self._ctx.user,
            "description"         : description,
            "timecode_start_text" : tc_start,
            "timecode_end_text"   : tc_end,
            "duration"            : self._summary.duration,
            "revision_number"     : self._revision_num,
        }
        # Upload base layer media file to the new Cut record if it exists.
        if self._mov_file_path:
            # Create a version.
            version_name, _ = os.path.splitext(os.path.basename(self._mov_file_path))
            sg_version = self._sg.create(
                "Version", {
                    "project"            : self._project,
                    "code"               : version_name,
                    "entity"             : self._sg_entity,
                    "created_by"         : self._ctx.user,
                    "updated_by"         : self._ctx.user,
                    "description"        : "Base media layer imported with Cut: %s" % title,
                    "sg_first_frame"     : 1,
                    "sg_movie_has_slate" : False,
                    "sg_path_to_movie"   : self._mov_file_path
                },
                ["id"])
            # Upload media to the version.
            self._logger.info("Uploading movie...")
            self.progress_changed.emit(1)
            self._sg.upload(
                sg_version["type"],
                sg_version["id"],
                self._mov_file_path,
                "sg_uploaded_movie"
            )
            # Link the Cut to the version.
            cut_payload["version"] = {"type": "Version", "id": sg_version["id"]}
        sg_cut = self._sg.create(
            "Cut",
            cut_payload,
            ["id", "code"])
        # Upload edl file to the new Cut record.
        self._sg.upload(
            sg_cut["type"], sg_cut["id"],
            self._edl_file_path, "attachments"
        )
        return sg_cut

    def _get_shot_in_out_sg_data(self, head_in, cut_in, cut_out, tail_out):
        """
        Returns a dictionary with the data to update a Shot in/out values
        in Shotgun from the given values

        :param head_in: Shot head in value to set
        :param cut_in: Shot cut in value to set
        :param cut_out: Shot cut out value to set
        :param tail_out: Shot tail out value to set
        :returns: A SG data dictionary suitable for an update
        """
        # Note: smart_head_duration shouldn't have to be set (it should be
        # calculated automatically by Shotgun). When the bug in Shotgun is fixed
        # that prevents this from happening, we should stop setting this field.
        # Also note that setting smart_head_duration triggers the calculation
        # of smart_working_duration. So there is potentially a problem with
        # multiple fields, although it's likely these two problems are related.
        # Additionally you may notice we are NOT adding a +1 to the
        # smart_head_duration. This is to get the smart fields to act the same
        # as the normal CutItem fields. When this bug with smart fields is
        # worked out, we'll likely need to add the +1 to the smart_head_duration
        # calculation (if it's needed at all at that point). Also note that
        # smart_tail_duration does not need to be set here.
        if self._use_smart_fields:
            return {
                "smart_head_in": head_in,
                "smart_cut_in": cut_in,
                "smart_cut_out": cut_out,
                "smart_tail_out": tail_out
            }
        else:
            return {
                "sg_head_in": head_in,
                "sg_cut_in": cut_in,
                "sg_cut_out": cut_out,
                "sg_tail_out": tail_out,
                "sg_cut_duration": cut_out - cut_in + 1,
                "sg_working_duration": tail_out - head_in + 1
            }

    def update_sg_shots(self, update_shots):
        """
        Update shots in Shotgun
        - Create them if needed

        If udpate_shots is true :
        - Change their status
        - Update cut in, cut out values

        :param update_shots: Whether or not Shot fields should be updated
        """
        if update_shots:
            self._logger.info("Updating shots ...")
        else:
            self._logger.info("Creating new shots ...")
        sg_batch_data = []
        if self._use_smart_fields:
            post_create = {}
        # Loop over all shots that we need to create
        for shot_name, items in self._summary.iteritems():
            # Retrieve values for the shot, and the shot itself
            (sg_shot,
             min_cut_order,
             min_head_in,
             min_cut_in,
             max_cut_out,
             max_tail_out,
             shot_diff_type) = items.get_shot_values()
            self._logger.debug("Shot values for %s are %s" % (
                shot_name,
                str((min_cut_order,
                    min_head_in,
                    min_cut_in,
                    max_cut_out,
                    max_tail_out,
                    shot_diff_type)),
            ))
            # Cut diff types should be the same for all repeated entries, except may be for
            # rescan / cut change, but we do the same thing in both cases, so it does not
            # matter, head in and tail out values can be evaluated on any repeated shot
            # entry
            # so arbitrarily use the first entry
            cut_diff = items[0]

            # Skip entries where the shot name couldn't be retrieved
            if shot_diff_type == _DIFF_TYPES.NO_LINK:
                pass
            elif shot_diff_type == _DIFF_TYPES.NEW:
                # We always create shots if needed
                self._logger.info("Will create shot %s for %s" % (
                    shot_name,
                    self.entity_name
                ))
                data = {
                    "project": self._project,
                    "code": cut_diff.name,
                    "updated_by": self._ctx.user,
                    "sg_cut_order": min_cut_order,
                }
                if self._sg_shot_link_field_name:
                    data[self._sg_shot_link_field_name] = self._sg_entity
                data.update(
                    self._get_shot_in_out_sg_data(
                        min_head_in,
                        min_cut_in,
                        max_cut_out,
                        max_tail_out,
                    )
                )
                if self._use_smart_fields:
                    post_create[data["code"]] = data
                sg_batch_data.append({
                    "request_type": "create",
                    "entity_type": "Shot",
                    "data": data
                })
            # We only update shots if asked to do so
            elif update_shots:
                if shot_diff_type == _DIFF_TYPES.OMITTED:
                    # Add code in the update so it will be returned with batch results.
                    sg_batch_data.append({
                        "request_type": "update",
                        "entity_type": "Shot",
                        "entity_id": sg_shot["id"],
                        "data": {"code": sg_shot["code"],
                                 "sg_status_list": self._omit_status if self._update_shot_statuses
                                        else sg_shot["sg_status_list"]
                                 }
                    })
                elif shot_diff_type == _DIFF_TYPES.REINSTATED:
                    reinstate_status = self._user_settings.retrieve("reinstate_status")
                    if reinstate_status == "Previous Status":
                        # Find the most recent status change event log entry where the
                        # project and linked shot code match the current project/shot
                        filters = [
                            ["project", "is", {"type": "Project", "id": self._project["id"]}],
                            ["event_type", "is", "Shotgun_Shot_Change"],
                            ["attribute_name", "is", "sg_status_list"],
                            ["entity.Shot.id", "is", sg_shot["id"]]
                        ]
                        fields = ["meta"]
                        sort = [{"field_name": "created_at", "direction": "desc"}]
                        event_log = self._sg.find_one("EventLogEntry", filters, fields, order=[
                            {"field_name": "created_at", "direction": "desc"}])
                        # Set the reinstate status value to the value previous to the
                        # event log entry
                        reinstate_status = event_log["meta"]["old_value"]
                    # Add code in the update so it will be returned with batch results.
                    data = {"code": sg_shot["code"],
                            "sg_cut_order": min_cut_order,
                            "sg_status_list": reinstate_status if self._update_shot_statuses
                            else sg_shot["sg_status_list"]
                            }
                    data.update(
                        self._get_shot_in_out_sg_data(
                            min_head_in,
                            min_cut_in,
                            max_cut_out,
                            max_tail_out,
                        )
                    )
                    # Smart fields do not behave as expected, this value must be
                    # set before other cut values to get the right effect.
                    if self._use_smart_fields:
                        sg_batch_data.append({
                            "request_type": "update",
                            "entity_type": "Shot",
                            "entity_id": sg_shot["id"],
                            "data": {"smart_head_duration": min_cut_in - min_head_in + 1}
                        })
                    sg_batch_data.append({
                        "request_type": "update",
                        "entity_type": "Shot",
                        "entity_id": sg_shot["id"],
                        "data": data
                    })
                else:  # Cut change or rescan or no change.
                    # Add code and status in the update so it will be
                    # returned with batch results.
                    data = {
                        "code": sg_shot["code"],
                        "sg_status_list": sg_shot["sg_status_list"],
                        "sg_cut_order": min_cut_order
                        }
                    data.update(
                        self._get_shot_in_out_sg_data(
                            min_head_in,
                            min_cut_in,
                            max_cut_out,
                            max_tail_out,
                        )
                    )
                    # Smart fields do not behave as expected, this value must be
                    # set before other cut values to get the right effect.
                    if self._use_smart_fields:
                        sg_batch_data.append({
                            "request_type": "update",
                            "entity_type": "Shot",
                            "entity_id": sg_shot["id"],
                            "data": {"smart_head_duration": min_cut_in - min_head_in + 1}
                        })
                    sg_batch_data.append({
                        "request_type": "update",
                        "entity_type": "Shot",
                        "entity_id": sg_shot["id"],
                        "data": data
                    })

        if sg_batch_data:
            sg_batch_data_update = []
            res = self._sg.batch(sg_batch_data)
            self._logger.info("Created/Updated %d shot(s)." % len(res))
            # Update cut_diffs with the new shots
            for sg_shot in res:
                # Skip entries without a "code" key coming from the smart fields
                # workaround
                if "code" not in sg_shot:
                    continue
                shot_code = sg_shot["code"]
                # Smart fields do not behave as expected, so we gather data from
                # the current Shot to do a deferred and staggered update; first
                # we have to set the smart_head_duration field, and after that
                # we update the other fields. This is inefficient but necessary
                # and only happens when smart fields are used on newly created Shots.
                if self._use_smart_fields and sg_shot["code"] in post_create:
                    sg_batch_data_update.append({
                        "request_type": "update",
                        "entity_type": "Shot",
                        "entity_id": sg_shot["id"],
                        "data": {
                            "smart_head_duration": (
                                post_create[shot_code]["smart_cut_in"] - post_create[shot_code]["smart_head_in"])
                            }
                    })
                    sg_batch_data_update.append({
                        "request_type": "update",
                        "entity_type": "Shot",
                        "entity_id": sg_shot["id"],
                        "data": {
                            "smart_head_in": post_create[shot_code]["smart_head_in"],
                            "smart_cut_in": post_create[shot_code]["smart_cut_in"],
                            "smart_cut_out": post_create[shot_code]["smart_cut_out"],
                            "smart_tail_out": post_create[shot_code]["smart_tail_out"]
                        }
                    })
                shot_name = shot_code.lower()
                if shot_name not in self._summary:
                    raise RuntimeError(
                        "Created/Updated shot %s, but couldn't retrieve it in our list" %
                        shot_name)
                for cut_diff in self._summary[shot_name]:
                    if cut_diff.sg_shot:
                        # Update with new values
                        cut_diff.sg_shot.update(sg_shot)
                    else:
                        cut_diff._sg_shot = sg_shot
        if sg_batch_data_update:
            # Do the deffered update of Shots for smart fields workaround.
            res = self._sg.batch(sg_batch_data_update)
            self._logger.info("Updated smart fields on %d shot(s)." % len(res))

    def _create_missing_sg_versions(self):
        """
        Create Versions in Shotgun for each Shot which needs one
        """
        # Helper to create versions in SG for testing
        # This is not part of production specs, but very handy for developers
        self._logger.info("Updating versions ...")
        sg_batch_data = []
        for shot_name, items in self._summary.iteritems():
            requested_names = []
            for cut_diff in items:
                edit = cut_diff.edit
                if edit and not edit.get_sg_version() and edit.get_version_name():
                    version_name = edit.get_version_name().lower()
                    if version_name not in requested_names:
                        sg_batch_data.append({
                            "request_type": "create",
                            "entity_type": "Version",
                            "data": {
                                "project": self._project,
                                "code": edit.get_version_name(),
                                "entity": cut_diff.sg_shot,
                                "updated_by": self._ctx.user,
                                "created_by": self._ctx.user,
                                "entity": cut_diff.sg_shot,
                            },
                            "return_fields": [
                                "entity.Shot.code",
                            ]
                        })
                        requested_names.append(version_name)
        if sg_batch_data:
            res = self._sg.batch(sg_batch_data)
            self._logger.info("Created %d new versions." % len(res))
            for shot_name, items in self._summary.iteritems():
                # Versions with same names are shared for repeated shots
                sg_versions = {}
                for cut_diff in items:
                    edit = cut_diff.edit
                    if edit and not edit.get_sg_version():
                        version_name = edit.get_version_name().lower()
                        if version_name not in sg_versions:
                            # Creation order should match
                            sg_version = res.pop(0)
                            if sg_version["code"].lower() != version_name:
                                raise RuntimeError("Version mismatch, expected %s got %s" % (
                                    version_name, sg_version["code"].lower()
                                ))
                            sg_versions[sg_version["code"].lower()] = sg_version
                        cut_diff.set_sg_version(sg_versions[version_name])

    def create_sg_cut_items(self, sg_cut):
        """
        Create the CutItems in Shotgun, linked to the given cut
        :param sg_cut: A SG Cut dictionary
        """
        # Loop through all edits and create CutItems for them
        self._logger.info("Creating Cut Items...")
        sg_batch_data = []
        for shot_name, items in self._summary.iteritems():
            for cut_diff in items:
                edit = cut_diff.edit
                if edit:
                    # note: since we're calculating these values from timecode which is
                    # inclusive, we have to make it exclusive when going to frames
                    edit_in = edit.record_in.to_frame() - self._summary.edit_offset + 1
                    edit_out = edit.record_out.to_frame() - self._summary.edit_offset
                    sg_batch_data.append({
                        "request_type": "create",
                        "entity_type": "CutItem",
                        "data": {
                            "project": self._project,
                            "code": edit.reel_name,
                            "cut": sg_cut,
                            "description": ", ".join(cut_diff.reasons),
                            "cut_order": edit.id,
                            "timecode_cut_item_in_text": str(edit.source_in),
                            "timecode_cut_item_out_text": str(edit.source_out),
                            "timecode_edit_in_text": str(edit.record_in),
                            "timecode_edit_out_text": str(edit.record_out),
                            "cut_item_in": cut_diff.new_cut_in,
                            "cut_item_out": cut_diff.new_cut_out,
                            "edit_in": edit_in,
                            "edit_out": edit_out,
                            "cut_item_duration": cut_diff.new_cut_out - cut_diff.new_cut_in + 1,
                            "shot": cut_diff.sg_shot,
                            "version": cut_diff.sg_version,
                            "created_by": self._ctx.user,
                            "updated_by": self._ctx.user,
                        }
                    })
        if sg_batch_data:
            self._sg.batch(sg_batch_data)
