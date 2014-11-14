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

from .ui.sequence_card import Ui_SequenceCard
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
class SequenceCard(QtGui.QFrame):
    selected = QtCore.Signal(dict)
    def __init__(self, parent, sg_sequence):
        super(SequenceCard, self).__init__(parent)
        self._sg_sequence = sg_sequence
        self.ui = Ui_SequenceCard()
        self.ui.setupUi(self)
        self.ui.title_label.setText("<big><b>%s</b></big>" % sg_sequence["code"])
        self.ui.status_label.setText(sg_sequence["sg_status_list"])
        self.ui.details_label.setText("<small>%s</small>" % sg_sequence["description"])
        self.ui.select_button.setVisible(False)
        self.ui.select_button.clicked.connect(self.select)

    @QtCore.Slot()
    def select(self):
        self.selected.emit(self._sg_sequence)

    def mouseDoubleClickEvent(self, event):
        self.select()

    def mousePressEvent(self, event):
        pass

    def enterEvent(self, event):
        self.ui.select_button.setVisible(True)
        self.setStyleSheet( _STYLES["selected"])

    def leaveEvent(self, event):
        self.ui.select_button.setVisible(False)
        self.setStyleSheet( "")
