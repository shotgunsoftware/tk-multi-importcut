# Copyright (c) 2014 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.


from sgtk.platform.qt import QtCore

class CutDiff(QtCore.QObject):

    def __init__(self, sg_shot, sg_version, edit):
        super(CutDiff, self).__init__()
        self._sg_shot = sg_shot
        self._sg_version = sg_version
        self._edit = edit