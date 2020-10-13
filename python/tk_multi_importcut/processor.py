# Copyright (c) 2016 Shotgun Software Inc.
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

# Our data handler
from .edl_cut import EdlCut

edl = sgtk.platform.import_framework("tk-framework-editorial", "edl")


class Processor(QtCore.QThread):
    """
    Processing thread. A EdlCut instance is created at runtime, and is the owner
    of all the data.

    The data  manager is instantiated in the run method, so its slots will be
    honored in the the running thread.

    Signals are exposed and connected to matching EdlCut's signals, as an interface
    for the caller, which does not access the data manager directly, and doesn't
    have to wait for the EdlCut creation to connect its own signals and slots.

    Similarly, some properties are exposed, so the caller does not need to access
    the EdlCut instance directly.
    """

    # Pass through signals which will be redirected to
    # the worker instance created in the running thread, so signals
    # will be processed in the running thread.
    # Typical signals chain is as follows
    # | UI | <-> | Processor | <-> | EdlCut | <-> | CutSummary |
    #
    #
    new_edl = QtCore.Signal(str)
    new_movie = QtCore.Signal(str)
    reset = QtCore.Signal()
    set_busy = QtCore.Signal(bool)
    step_done = QtCore.Signal(int)
    step_failed = QtCore.Signal(int)
    set_sg_project = QtCore.Signal(dict)
    new_sg_project = QtCore.Signal(dict)
    new_sg_entity = QtCore.Signal(dict)
    new_sg_cut = QtCore.Signal(dict)
    retrieve_projects = QtCore.Signal()
    retrieve_entities = QtCore.Signal(str)
    retrieve_cuts = QtCore.Signal(dict)
    show_cut_diff = QtCore.Signal(dict)
    new_cut_diff = QtCore.Signal(CutDiff)
    got_busy = QtCore.Signal(int)
    got_idle = QtCore.Signal()
    progress_changed = QtCore.Signal(int)
    import_cut = QtCore.Signal(str, dict, dict, str, bool)
    totals_changed = QtCore.Signal()
    delete_cut_diff = QtCore.Signal(CutDiff)
    ready = QtCore.Signal()
    valid_edl = QtCore.Signal(str, bool)
    has_transitions = QtCore.Signal()
    valid_movie = QtCore.Signal(str)
    reload_step = QtCore.Signal(int)

    def __init__(self, frame_rate=None):
        """
        Instantiate a new Processor

        :param frame_rate: A frame rate, as a float
        """
        super(Processor, self).__init__()
        self._logger = get_logger()
        self._edl_cut = None
        self._frame_rate = frame_rate
        edl.EditList.set_logger(self._logger.getChild("(editorial)"))

    @property
    def title(self):
        """
        Return a title, retrieved from the loaded EDL, if any

        :returns: A string or None
        """
        if self._edl_cut and self._edl_cut._edl:
            return self._edl_cut._edl.title
        return None

    @property
    def edl_file_path(self):
        """
        Return the full file path of the EDL file being imported

        :returns: A string or None
        """
        if self._edl_cut:
            return self._edl_cut._edl_file_path
        return None

    @property
    def summary(self):
        """
        Return the current CutSummary instance, if any

        :returns: A CutSummary instance or None
        """
        if self._edl_cut and self._edl_cut._summary:
            return self._edl_cut._summary
        return None

    @property
    def sg_project(self):
        """
        Return the current Shotgun Project we are importing the Cut into.

        This can be None if this app was started outside of a Project
        context, and a Project has not been selected yet.

        :returns: A Shotgun Project dictionary or None
        """
        if self._edl_cut and self._edl_cut._project:
            return self._edl_cut._project
        return None

    @property
    def sg_entity(self):
        """
        Return the current Shotgun Entity (e.g. Sequence) we are displaying Cut
        changes for

        :returns: A Shotgun Entity dictionary or None
        """
        if self._edl_cut and self._edl_cut._sg_entity:
            return self._edl_cut._sg_entity
        return None

    @property
    def entity_name(self):
        """
        Return the name of the Entity which was picked, if any

        :returns: A string or None
        """
        if not self._edl_cut:
            return None
        return self._edl_cut.entity_name

    @property
    def entity_type_name(self):
        """
        Return the display name of Entity's type which was picked, if any

        :returns: A string or None
        """
        if not self._edl_cut:
            return None
        return self._edl_cut.entity_type_name

    @property
    def sg_cut(self):
        """
        Return the current Shotgun Cut we are displaying Cut changes for.

        :returns: A Cut dictionary or None
        """
        if self._edl_cut and self._edl_cut._sg_cut:
            return self._edl_cut._sg_cut
        return None

    @property
    def sg_new_cut(self):
        """
        Return the new Cut created in Shotgun

        :returns: A SG Cut dictionary or None
        """
        if self._edl_cut:
            return self._edl_cut._sg_new_cut
        return None

    @property
    def sg_new_cut_url(self):
        """
        Return the SG url for the new Cut, if any

        :returns: A string or None
        """
        sg_new_cut = self.sg_new_cut
        if not sg_new_cut:
            return None
        # The value in this tree_path variable is passed along to the tree_path
        # url variable. Also we use the path(QtCore.QUrl.FullyEncoded) method of
        # QUrl to get the / characters properly passed through to the GMA. This
        # is a little touchy so we don't encode the entire url.
        tree_path = "/cuts_tree/Project/%d/Cut/%d/%d" % (
            sg_new_cut["project"]["id"],
            sg_new_cut["entity"]["id"],
            sg_new_cut["id"],
        )
        return (
            "%s/page/media_center?type=Cut&id=%d&project_id=%d&tree_path=%s&global=true&project_sel=all"
            % (
                self._edl_cut._app.shotgun.base_url,
                sg_new_cut["id"],
                sg_new_cut["project"]["id"],
                QtCore.QUrl(tree_path).path(QtCore.QUrl.FullyEncoded),
            )
        )

    @property
    def no_cut_for_entity(self):
        """
        Return True if there is no existing SG Cut for the current SG Entity,
        False otherwise

        :returns: A boolean
        """
        return self._edl_cut._no_cut_for_entity

    @property
    def has_valid_edl(self):
        """
        Return True if a valid EDL file was loaded, False otherwise

        :returns: A boolean
        """
        return self._edl_cut.had_valid_edl

    @property
    def has_valid_movie(self):
        """
        Return True if a valid movie file was retrieved, False otherwise

        :returns: A boolean
        """
        return self._edl_cut.had_valid_movie

    def run(self):
        """
        Run the processor
        - Create a EdlCut worker instance
        - Connect this processor's signals to worker ones
        - Emit ready Signal
        - Then wait for events to process
        """
        # Create a worker
        self._edl_cut = EdlCut(frame_rate=self._frame_rate)
        # Connect signals from the worker to ours as a gateway, so anything
        # connected to the Processor signals will be connected to the worker.
        # Orders we receive
        self.new_edl.connect(self._edl_cut.load_edl)
        self.new_movie.connect(self._edl_cut.register_movie_path)
        self.reset.connect(self._edl_cut.reset)
        self.retrieve_projects.connect(self._edl_cut.retrieve_projects)
        self.set_sg_project.connect(self._edl_cut.set_sg_project)
        self.retrieve_entities.connect(self._edl_cut.retrieve_entities)
        self.retrieve_cuts.connect(self._edl_cut.retrieve_cuts)
        self.show_cut_diff.connect(self._edl_cut.show_cut_diff)
        self.import_cut.connect(self._edl_cut.do_cut_import)
        self.reload_step.connect(self._edl_cut.reload_step)
        # Results / orders we send
        self._edl_cut.step_done.connect(self.step_done)
        self._edl_cut.step_failed.connect(self.step_failed)
        self._edl_cut.new_sg_project.connect(self.new_sg_project)
        self._edl_cut.new_sg_entity.connect(self.new_sg_entity)
        self._edl_cut.new_sg_cut.connect(self.new_sg_cut)
        self._edl_cut.new_cut_diff.connect(self.new_cut_diff)
        self._edl_cut.delete_cut_diff.connect(self.delete_cut_diff)
        self._edl_cut.got_busy.connect(self.got_busy)
        self._edl_cut.got_idle.connect(self.got_idle)
        self._edl_cut.progress_changed.connect(self.progress_changed)
        self._edl_cut.totals_changed.connect(self.totals_changed)
        self._edl_cut.valid_edl.connect(self.valid_edl)
        self._edl_cut.has_transitions.connect(self.has_transitions)
        self._edl_cut.valid_movie.connect(self.valid_movie)
        # Tell the outside world we are ready to process things
        self.ready.emit()
        self.exec_()
