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
    show_sequence = QtCore.Signal(dict)
    highlight_selected = QtCore.Signal(QtGui.QWidget)
    def __init__(self, parent, sg_sequence):
        super(SequenceCard, self).__init__(parent)
        self._sg_sequence = sg_sequence
        self.ui = Ui_SequenceCard()
        self.ui.setupUi(self)
        self.ui.title_label.setText("<big><b>%s</b></big>" % sg_sequence["code"])
        self.ui.status_label.setText(sg_sequence["sg_status_list"])
        self.ui.details_label.setText("<small>%s</small>" % sg_sequence["description"])
        self.ui.select_button.setVisible(False)
        self.ui.select_button.clicked.connect(self.show_selected)

    @QtCore.Slot()
    def select(self):
        self.ui.select_button.setVisible(True)
        self.setStyleSheet(_STYLES["selected"])

    @QtCore.Slot()
    def unselect(self):
        self.ui.select_button.setVisible(False)
        self.setStyleSheet("")

    @QtCore.Slot()
    def show_selected(self):
        self.show_sequence.emit(self._sg_sequence)

    def mouseDoubleClickEvent(self, event):
        self.show_selected()

    def mousePressEvent(self, event):
        self.highlight_selected.emit(self)

    def enterEvent(self, event):
        pass
    def leaveEvent(self, event):
        pass
        #self.ui.select_button.setVisible(False)

