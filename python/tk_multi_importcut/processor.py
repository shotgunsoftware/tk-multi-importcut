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
from .cut_diff import CutDiff

edl = sgtk.platform.import_framework("tk-framework-editorial", "edl")

class Processor(QtCore.QThread):
    # Pass through signals which will be redirected to
    # instances created in the running thread, so signals
    # will be processed in the running thread
    new_edl = QtCore.Signal(str)
    reset = QtCore.Signal()
    set_busy = QtCore.Signal(bool)
    step_done = QtCore.Signal(int)
    new_sg_sequence = QtCore.Signal(dict)
    retrieve_sequences = QtCore.Signal()
    show_cut_for_sequence = QtCore.Signal(dict)
    new_cut_diff = QtCore.Signal(CutDiff)
    got_busy = QtCore.Signal()
    got_idle = QtCore.Signal()
    import_cut = QtCore.Signal(str,str,str, str)
    def __init__(self):
        super(Processor, self).__init__()
        self._logger = get_logger()
        self._edl_cut = None

    def run(self):
        self._edl_cut = EdlCut()
        # Orders
        self.new_edl.connect(self._edl_cut.load_edl)
        self.reset.connect(self._edl_cut.reset)
        self.retrieve_sequences.connect(self._edl_cut.retrieve_sequences)
        self.show_cut_for_sequence.connect(self._edl_cut.show_cut_for_sequence)
        self.import_cut.connect(self._edl_cut.do_cut_import)
        # Results
        self._edl_cut.step_done.connect(self.step_done)
        self._edl_cut.new_sg_sequence.connect(self.new_sg_sequence)
        self._edl_cut.new_cut_diff.connect(self.new_cut_diff)
        self._edl_cut.got_busy.connect(self.got_busy)
        self._edl_cut.got_idle.connect(self.got_idle)
        self.exec_()

class EdlCut(QtCore.QObject):

    step_done = QtCore.Signal(int)
    new_sg_sequence = QtCore.Signal(dict)
    new_cut_diff = QtCore.Signal(CutDiff)
    got_busy = QtCore.Signal()
    got_idle = QtCore.Signal()

    def __init__(self):
        super(EdlCut, self).__init__()
        self._edl = None
        self._sg_entity = None
        self._cut_diffs = {}
        self._logger = get_logger()
        self._app = sgtk.platform.current_bundle()
        self._sg = self._app.shotgun
        self._ctx = self._app.context

    def process_edit(self, edit, logger):
        # Use our own logger rather than the framework one
        edl.process_edit(edit, self._logger)
        # Check things are right
        # Add some lambda to retrieve properties
        edit.get_shot_name = lambda : edit._shot_name
        edit.get_clip_name = lambda : edit._clip_name
        if not edit.get_shot_name() and not edit.get_clip_name():
            raise RuntimeError("Couldn't extract a shot name nor a clip name, one of them is required")

    @QtCore.Slot(str)
    def reset(self):
        self._edl = None
        self._sg_entity = None
        self._cut_diffs = {}
        self._logger.info("Session discarded...")

    @QtCore.Slot(str)
    def load_edl(self, path):
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
            # Review what we loaded
            for edit in self._edl.edits:
                if not edit.get_shot_name():
                    raise ValueError("Couldn't retrieve shot name for %s" % edit)
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
        self._logger.info("Retrieving Sequences for project %s ..." % self._ctx.project["name"])
        self.got_busy.emit()
        sg_sequences = self._sg.find(
            "Sequence",
            [["project", "is", self._ctx.project]],
            [ "code", "id", "sg_status_list", "image", "description"]
        )
        if not sg_sequences:
            self._logger.warning("Couldn't retrieve any Sequence for project %s" % self._ctx.project["name"])
            return
        for sg_sequence in sg_sequences:
            self.new_sg_sequence.emit(sg_sequence)
        self.got_idle.emit()
        self._logger.info("Retrieved %d Sequences." % len(sg_sequences))

    @QtCore.Slot(dict)
    def show_cut_for_sequence(self, sg_entity):
        self._logger.info("Retrieving cut summary for %s" % ( sg_entity))
        self.got_busy.emit()
        self._cut_diffs = {}
        try:
            # Retrieve cuts linked to the sequence, pick up the latest or approved one
            # Later, the UI will allow selecting it
            sg_cut = self._sg.find_one(
                "Cut",
                [["sg_sequence", "is", sg_entity]],
                []
            )
            sg_cut_items = []
            if sg_cut:
                sg_cut_item_entity = self._app.get_setting("sg_cut_item_entity")
                # Retrieve all cut items linked to that cut
                sg_cut_items = self._sg.find(sg_cut_item_entity,
                    [["sg_cut", "is", sg_cut]],
                    ["sg_cut"]
                )

            # Retrieve shots linked to the sequence
            sg_shots = self._sg.find(
                "Shot",
                [["sg_sequence", "is", sg_entity]],
                ["code", "sg_status_list", "sg_head_in", "sg_tail_out", "sg_cut_in", "sg_cut_out", "sg_cut_order", "image"],
            )
            for edit in self._edl.edits:
                shot_name = edit.get_shot_name()
                # Is it a duplicate ?
                if shot_name in self._cut_diffs:
                    self._logger.info("Found duplicated shot shot %s (%s)" % (shot_name, self._cut_diffs))
                    sg_shot = self._cut_diffs[sg_shot["code"]][0].sg_shot
                    cut_diff = CutDiff(sg_shot=sg_shot, sg_version=None, edit=edit)
                    self._cut_diffs[sg_shot["code"]].append(cut_diff)
                    self.new_cut_diff.emit(cut_diff)
                else :
                    # Do we have a matching shot in SG ?
                    matching_shot = None
                    for sg_shot in sg_shots:
                        if sg_shot["code"] == edit.get_shot_name():
                            # yes we do
                            self._logger.info("Found matching existing shot %s" % shot_name)
                            matching_shot = sg_shot
                            # Remove this entry from the list
                            sg_shots.remove(sg_shot)
                            break
                    cut_diff = CutDiff(shot_name, sg_shot=matching_shot, edit=edit)
                    self._cut_diffs[shot_name] = [cut_diff]
                    self.new_cut_diff.emit(cut_diff)
            # Process now all sg shots leftover
            for sg_shot in sg_shots:
                cut_diff = CutDiff(sg_shot["code"], sg_shot=sg_shot, sg_version=None, edit=None)
                self._cut_diffs[sg_shot["code"]].append(cut_diff)
                self.new_cut_diff.emit(cut_diff)
            self._logger.info("Retrieved %d cut differences." % len(self._cut_diffs))
        except Exception, e :
            self._logger.exception(str(e))
        finally:
            self.got_idle.emit()

    @QtCore.Slot(str, str, str, str)
    def do_cut_import(self, title, sender, to, description):
        self._logger.info("Importing cut %s" % title)
        self.got_busy.emit()
        try:
            self.create_sg_cut(title)
        except Exception, e :
            self._logger.exception(str(e))
        finally:
            self.got_idle.emit()
        self._logger.info("Cut %s imported" % title)

    def create_sg_cut(self, title):
        # Create a new cut
        sg_cut = self._sg.create(
            "Cut", {
                "project" : self._ctx.project,
                "code" : title,
                "sg_sequence" : self._sg_entity,
            },
            ["id", "code"])
        # Loop through all edits and create CutItems for them
        sg_batch_data = []
        cut_item_entity = self._app.get_setting("sg_cut_item_entity")
        for shot_name, items in self._cut_diffs.iteritems():
            for item in items:
                edit = item.edit
                if edit:
                    tc_cut_in = edit.source_in.to_frame()
                    sg_batch_data.append({
                        "request_type" : "create",
                        "entity_type" : cut_item_entity,
                        "data" : {
                            "project" : self._ctx.project,
                            "sg_cut" : sg_cut,
                            "sg_cut_order" : edit.id,
                            "sg_timecode_cut_in" : int(edit.source_in.to_seconds() * 1000),
                            "sg_timecode_cut_out" : int(edit.source_out.to_seconds() * 1000),
                            "sg_timecode_edl_in" : int(edit.record_in.to_seconds() * 1000),
                            "sg_timecode_edl_out" : int(edit.record_out.to_seconds() * 1000),
                            "sg_cut_in" : edit.source_in.to_frame(),
                            "sg_cut_out" : edit.source_out.to_frame(),
                            "sg_link" : item.sg_shot,
                            "sg_version" : None,
                        }
                    })
        if sg_batch_data:
            self._sg.batch(sg_batch_data)
