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
from .cut_diff import _DIFF_TYPES
class SubmitDialog(QtGui.QDialog):
    submit = QtCore.Signal(str,str,str, str)
    def __init__(self, parent=None, title=None, summary=None):
        super(SubmitDialog, self).__init__(parent)
        self.ui = Ui_submit_dialog()
        self.ui.setupUi(self)

        buttons = self.ui.import_cut_button_box.buttons()
        submit_button = buttons[0]
        submit_button.setText("Import Cut")
        self.ui.title_text.setText(title or "")
        if not summary:
            # Just in case ...
            raise ValueError("Can't import a cut without a summary")
        
        self.ui.total_shots_label.setText("%s" % len(summary))
        #self.ui.cut_changes_label
        self.ui.new_shots_label.setText("%s" % summary.count_for_type(_DIFF_TYPES.NEW))
        #self.ui.rescans_label
        self.ui.omitted_label.setText("%s" % summary.count_for_type(_DIFF_TYPES.OMITTED))
        self.ui.reinstated_label.setText("%s" % summary.count_for_type(_DIFF_TYPES.REINSTATED))
        #self.ui.repeated_label
        self.ui.import_cut_button_box.rejected.connect(self.close_dialog)
        self.ui.import_cut_button_box.accepted.connect(self.submit_cut)

    @QtCore.Slot()
    def submit_cut(self):
        title = self.ui.title_text.text()
        to = self.ui.to_text.text()
        description = self.ui.description_text.toPlainText()
        self.submit.emit(title, "me", to, description)
        self.close_dialog()

    @QtCore.Slot()
    def close_dialog(self):
        self.close()