# Copyright (c) 2015 Shotgun Software Inc.
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

import sgtk

from sgtk.platform.qt import QtCore, QtGui
settings = sgtk.platform.import_framework("tk-framework-shotgunutils", "settings")

from .ui.submit_dialog import Ui_submit_dialog
from .cut_diff import _DIFF_TYPES
class SubmitDialog(QtGui.QDialog):
    """
    Submit dialog, offering a summary and a couple of options to the user
    """
    submit = QtCore.Signal(str, dict, dict, str, bool)
    def __init__(self, parent=None, title=None, summary=None):
        """
        Instantiate a new dialog
        :param parent: a QWidget
        :param title: a string, used a imported Cut name
        :param summary: a CutSummary instance
        """
        super(SubmitDialog, self).__init__(parent)
        self.ui = Ui_submit_dialog()
        self.ui.setupUi(self)
        self._app = sgtk.platform.current_bundle()
        # Create a settings manager where we can pull and push prefs later
        self._user_settings = settings.UserSettings(self._app)
        # Retrieve user settings and set UI values
        update_shot_fields = self._user_settings.retrieve("update_shot_fields", True)
        self.ui.update_shot_fields_checkbox.setChecked(update_shot_fields)

        buttons = self.ui.import_cut_button_box.buttons()
        submit_button = buttons[0]
        submit_button.setText("Import Cut")
        self.ui.title_text.setText(title or "")
        if not summary:
            # Just in case ...
            raise ValueError("Can't import a cut without a summary")
        self.ui.from_label.setText(self._app.context.user["name"] if self._app.context.user else "")
        self.ui.to_text.setText(self._app.get_setting("report_to_group") or "")
        self.ui.total_shots_label.setText("%s" % len(summary))
        self.ui.cut_changes_label.setText("%s" % summary.count_for_type(_DIFF_TYPES.CUT_CHANGE))
        self.ui.new_shots_label.setText("%s" % summary.count_for_type(_DIFF_TYPES.NEW))
        self.ui.rescans_label.setText("%s" % summary.rescans_count)
        self.ui.omitted_label.setText("%s" % summary.count_for_type(_DIFF_TYPES.OMITTED))
        self.ui.reinstated_label.setText("%s" % summary.count_for_type(_DIFF_TYPES.REINSTATED))
        self.ui.repeated_label.setText("%s" % summary.repeated_count)
        no_link_count=summary.count_for_type(_DIFF_TYPES.NO_LINK)
        if no_link_count:
            self.ui.no_link_label.setText("%s" % no_link_count)
        else:
            self.ui.no_link_label.hide()
            self.ui.no_link_title_label.hide()
        self.ui.import_cut_button_box.rejected.connect(self.close_dialog)
        self.ui.import_cut_button_box.accepted.connect(self.submit_cut)

    @QtCore.Slot()
    def submit_cut(self):
        """
        Submit the cut import and close the dialog
        """
        self._save_settings()
        update_shot_fields = self.ui.update_shot_fields_checkbox.isChecked()
        title = self.ui.title_text.text()
        to = self.ui.to_text.text()
        sg = self._app.shotgun
        sg_group = sg.find_one("Group", [["code", "is", to]], ["code"])
        if not sg_group:
            QtGui.QMessageBox.warning(
                self,
                "Unknown Shotgun Group",
                "Couldn't retrieve a group named %s in Shotgun" % to,
                buttons=QtGui.QMessageBox.Ok
            )
            return
        description = self.ui.description_text.toPlainText()
        user = self._app.context.user or {}
        self.submit.emit(title, user, sg_group, description, update_shot_fields)
        self.close_dialog()

    @QtCore.Slot()
    def close_dialog(self):
        """
        Close the dialog on submit or cancel
        """
        self.close()

    def _save_settings(self):
        """
        Save user settings from current UI values
        """
        # Save the settings
        update_shot_fields = self.ui.update_shot_fields_checkbox.isChecked()
        self._user_settings.store("update_shot_fields", update_shot_fields)
