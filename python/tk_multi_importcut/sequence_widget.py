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

class SequenceCard(QtGui.QFrame):
    selected = QtCore.Signal(dict)
    def __init__(self, parent, sg_sequence):
        super(SequenceCard, self).__init__(parent)
        self.ui = Ui_SequenceCard()
        self.ui.setupUi(self)
        self.ui.title_label.setText("<big><b>%s</b></big>" % sg_sequence["code"])
        self.ui.status_label.setText(sg_sequence["sg_status_list"])
        self.ui.details_label.setText("<small>%s</small>" % sg_sequence["description"])

    def mouseDoubleClickEvent(self, event):
        print "Double click"
        self.selected.emit({ "type" : "Sequence", "id" : 1023})

    def mousePressEvent(self, event):
        print "Single click"
        print self.property("selected")
        self.setProperty("selected", True);
