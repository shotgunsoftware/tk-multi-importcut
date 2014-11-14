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
        # Results
        self._edl_cut.step_done.connect(self.step_done)
        self._edl_cut.new_sg_sequence.connect(self.new_sg_sequence)
        self.exec_()

class EdlCut(QtCore.QObject):

    step_done = QtCore.Signal(int)
    new_sg_sequence = QtCore.Signal(dict)

    def __init__(self):
        super(EdlCut, self).__init__()
        self._edl = None
        self._sg_entity = None
        self._logger = get_logger()
        self._app = sgtk.platform.current_bundle()
        self._sg = self._app.shotgun
        self._ctx = self._app.context

    def process_edit(self, edit, logger):
        # Use our own logger rather than the framework one
        edl.process_edit(edit, self._logger)


    @QtCore.Slot(str)
    def reset(self):
        self._edl = None
        self._logger.info("Session discarded...")

    @QtCore.Slot(str)
    def load_edl(self, path):
        self._logger.info("Loading %s ..." % path)
        try:
            self._edl = edl.EditList(
                file_path=path,
                visitor=edl.process_edit,
            )
            self._logger.info(
                "%s loaded, %s edits" % (
                    self._edl.title, len(self._edl.edits)
                )
            )
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
        self._logger.info("Retrieved %d Sequences." % len(sg_sequences))

    @QtCore.Slot(dict)
    def show_cut_for_sequence(self, sg_entity):
        self._logger.info("Retrieving cut information for %s" % ( sg_entity))
        pass

