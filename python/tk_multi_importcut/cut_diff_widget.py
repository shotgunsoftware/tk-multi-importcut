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
from sgtk.platform.qt import QtCore, QtGui

from .ui.cut_diff_card import Ui_CutDiffCard
from .cut_diff import CutDiff
# Some standard colors
# Used in Sgtk apps
_COLORS = {
    "sg_blue" : "#2C93E2",
    "sg_red"  : "#FC6246",
    "mid_blue"  : "#1B82D1",
}


_STYLES = {
    "selected" : "border-color: %s" % _COLORS["sg_blue"],
}
class CutDiffCard(QtGui.QFrame):
    def __init__(self, parent, cut_diff):
        super(CutDiffCard, self).__init__(parent)
        self._cut_diff = cut_diff
        self.ui = Ui_CutDiffCard()
        self.ui.setupUi(self)
        self.ui.shot_name_label.setText("<big><b>%s</b></big>" % self._cut_diff._sg_shot["code"])
