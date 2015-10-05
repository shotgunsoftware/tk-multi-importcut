# Copyright (c) 2015 Shotgun Software Inc.
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
from .cut_summary import CutSummary

# Our data handler
from .edl_cut import EdlCut

edl = sgtk.platform.import_framework("tk-framework-editorial", "edl")


class Processor(QtCore.QThread):
    """
    Processing thread. A EdlCut instance is created at runtime, and is the owner
    of all the data.
    """
    # Pass through signals which will be redirected to
    # the worker instance created in the running thread, so signals
    # will be processed in the running thread.
    # Typical signals chain is as follow
    # | UI | <-> | Processor | <-> | EdlCut | <-> | CutSummary |
    #
    #
    new_edl                 = QtCore.Signal(str)
    reset                   = QtCore.Signal()
    set_busy                = QtCore.Signal(bool)
    step_done               = QtCore.Signal(int)
    step_failed             = QtCore.Signal(int)
    new_sg_entity           = QtCore.Signal(dict)
    new_sg_cut              = QtCore.Signal(dict)
    retrieve_entities       = QtCore.Signal(str)
    retrieve_cuts           = QtCore.Signal(dict)
    show_cut_diff           = QtCore.Signal(dict)
    new_cut_diff            = QtCore.Signal(CutDiff)
    got_busy                = QtCore.Signal(int)
    got_idle                = QtCore.Signal()
    progress_changed        = QtCore.Signal(int)
    import_cut              = QtCore.Signal(str,dict,dict, str, bool)
    totals_changed          = QtCore.Signal()
    delete_cut_diff         = QtCore.Signal(CutDiff)

    def __init__(self):
        """
        Instantiate a new Processor
        """
        super(Processor, self).__init__()
        self._logger = get_logger()
        self._edl_cut = None
        edl.EditList.set_logger(self._logger.getChild("(editorial)"))

    @property
    def title(self):
        """
        Return a title, retrieved from the loaded EDL, if any
        """
        if self._edl_cut and self._edl_cut._edl:
            return self._edl_cut._edl.title
        return None

    @property
    def edl_file_path(self):
        """
        Return the full file path of the EDL file being imported
        """
        if self._edl_cut:
            return self._edl_cut._edl_file_path
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
        :returns: A Shotgun entity dictionary or None
        """
        if self._edl_cut and self._edl_cut._sg_entity:
            return self._edl_cut._sg_entity
        return None

    @property
    def entity_name(self):
        """
        Return the name of entity which was picked, if any
        :returns: A string or None
        """
        if not self._edl_cut:
            return None
        return self._edl_cut.entity_name

    @property
    def entity_type_name(self):
        """
        Return the nice name of entity's type which was picked, if any
        :returns: A string or None
        """

        if not self._edl_cut:
            return None
        return self._edl_cut.entity_type_name
    
    @property
    def sg_cut(self):
        """
        Return the current Shotgun Cut we are displaying cut
        changes for.
        :returns: A Cut dictionary or None if no Cut are yet available in SG
        """
        if self._edl_cut and self._edl_cut._sg_cut:
            return self._edl_cut._sg_cut
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
    def no_cut_for_entity(self):
        return self._edl_cut._no_cut_for_entity

    @property
    def project_import(self):
        return self._edl_cut._project_import

    def run(self):
        """
        Run the processor
        - Create a EdlCut worker instance
        - Connect this processor signals to worker's ones
        - Then wait for events to process
        """
        # Create a worker
        self._edl_cut = EdlCut()
        # Connect signals from the worker to ours as a gateway, so anything
        # connected to the Processor signals will be connected to the worker
        # Orders we receive
        self.new_edl.connect(self._edl_cut.load_edl)
        self.reset.connect(self._edl_cut.reset)
        self.retrieve_entities.connect(self._edl_cut.retrieve_entities)
        self.retrieve_cuts.connect(self._edl_cut.retrieve_cuts)
        self.show_cut_diff.connect(self._edl_cut.show_cut_diff)
        self.import_cut.connect(self._edl_cut.do_cut_import)
        # Results / orders we send
        self._edl_cut.step_done.connect(self.step_done)
        self._edl_cut.step_failed.connect(self.step_failed)
        self._edl_cut.new_sg_entity.connect(self.new_sg_entity)
        self._edl_cut.new_sg_cut.connect(self.new_sg_cut)
        self._edl_cut.new_cut_diff.connect(self.new_cut_diff)
        self._edl_cut.delete_cut_diff.connect(self.delete_cut_diff)
        self._edl_cut.got_busy.connect(self.got_busy)
        self._edl_cut.got_idle.connect(self.got_idle)
        self._edl_cut.progress_changed.connect(self.progress_changed)
        self._edl_cut.totals_changed.connect(self.totals_changed)
        self.exec_()
