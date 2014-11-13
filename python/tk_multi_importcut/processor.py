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

    def __init__(self):
        super(Processor, self).__init__()
        self._logger = get_logger()
    new_edl = QtCore.Signal(str)

    def run(self):
        self._edl_cut = EdlCut()
        self.new_edl.connect(self._edl_cut.load_edl)
        self.exec_()

class EdlCut(QtCore.QObject):
    def __init__(self):
        super(EdlCut, self).__init__()
        self._edl = None
        self._logger = get_logger()

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
        except Exception, e:
            self._edl = None
            self._logger.error("Couldn't load %s : %s" % (path, str(e)))
