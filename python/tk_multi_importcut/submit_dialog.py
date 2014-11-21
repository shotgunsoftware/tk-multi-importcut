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

from .ui.submit_dialog import Ui_submit_dialog

class SubmitDialog(QtGui.QDialog):
    submit = QtCore.Signal(str,str,str, str)
    def __init__(self, parent=None):
        super(SubmitDialog, self).__init__(parent)
        self.ui = Ui_submit_dialog()
        self.ui.setupUi(self)

        buttons = self.ui.import_cut_button_box.buttons()
        submit_button = buttons[0]
        submit_button.setText("Import Cut")
        self.ui.import_cut_button_box.rejected.connect(self.close_dialog)
        self.ui.import_cut_button_box.accepted.connect(self.submit_cut)

    @QtCore.Slot()
    def submit_cut(self):
        self.submit.emit("title", "from", "to", "description")
        self.close_dialog()

    @QtCore.Slot()
    def close_dialog(self):
        self.close()