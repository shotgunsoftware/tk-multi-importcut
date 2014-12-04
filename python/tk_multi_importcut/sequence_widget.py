# Copyright (c) 2014 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import tempfile

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
        self.set_thumbnail(":/tk_multi_importcut/sg_sequence_thumbnail.png")
#        from random import randint
#        self.set_thumbnail( [
#            "/Users/steph/devs/sg/sgtk/apps/tk-multi-importcut/resources/no_thumbnail.png",
#            "/Users/steph/Pictures/microsoftazurelogo.png",
#            "/Users/steph/Pictures/IMG_4720.jpg"
#        ][randint(0, 2)])

    @QtCore.Slot()
    def select(self):
        self.setProperty("selected", True)
        self.ui.select_button.setVisible(True)
        self.setStyleSheet(_STYLES["selected"])

    @QtCore.Slot()
    def unselect(self):
        self.setProperty("selected", False)
        self.ui.select_button.setVisible(False)
        self.setStyleSheet("")

    @QtCore.Slot()
    def show_selected(self):
        self.highlight_selected.emit(self)
        self.ui.select_button.setVisible(False)
        self.show_sequence.emit(self._sg_sequence)

    @QtCore.Slot(str)
    def new_thumbnail(self, path):
        self.set_thumbnail(path)

    def mouseDoubleClickEvent(self, event):
        self.show_selected()

    def mousePressEvent(self, event):
        self.highlight_selected.emit(self)

    def enterEvent(self, event):
        self.ui.select_button.setVisible(True)

    def leaveEvent(self, event):
        self.ui.select_button.setVisible(False)
    
    def set_thumbnail(self, thumb_path):
        size = self.ui.icon_label.size()
        ratio = size.width() / float(size.height())
        pixmap = QtGui.QPixmap(thumb_path)
        if pixmap.isNull():
            return
        psize = pixmap.size()
        pratio = psize.width() / float(psize.height())
        if pratio > ratio:
            self.ui.icon_label.setPixmap(
                pixmap.scaledToWidth(size.width(), mode=QtCore.Qt.SmoothTransformation)
            )
        else:
            self.ui.icon_label.setPixmap(
                pixmap.scaledToHeight(size.height(), mode=QtCore.Qt.SmoothTransformation)
            )

