# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import re
import sgtk

# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
from sgtk.platform.qt import QtCore, QtGui

from .ui.submit_dialog import Ui_submit_dialog
from .cut_diff import _DIFF_TYPES
from logger import get_logger


class SubmitDialog(QtGui.QDialog):
    """
    Submit dialog, offering a summary and a couple of options to the user
    """

    submit = QtCore.Signal(str, dict, dict, str, bool)

    def __init__(self, parent=None, title=None, summary=None):
        """
        Instantiate a new dialog
        :param parent: (optional) QWidget
        :param title: (optional) string, used as imported Cut name
        :param summary: (optional) CutSummary instance
        """
        super(SubmitDialog, self).__init__(parent)
        self.ui = Ui_submit_dialog()
        self.ui.setupUi(self)
        self._app = sgtk.platform.current_bundle()
        self._sg = self._app.shotgun
        self._logger = get_logger()
        # Create a settings manager where we can pull and push prefs later
        self._user_settings = self._app.user_settings
        # Retrieve user settings and set UI values
        update_shot_fields = self._user_settings.retrieve("update_shot_fields", True)
        self.ui.update_shot_fields_checkbox.setChecked(update_shot_fields)
        self.ui.title_text.setText(title or "")
        if not summary:
            # Just in case ...
            raise ValueError("Can't import a cut without a summary")
        self.ui.from_label.setText(
            self._app.context.user["name"] if self._app.context.user else ""
        )
        email_groups = ", ".join(self._user_settings.retrieve("email_groups"))
        self.ui.to_text.setText(email_groups)
        self.ui.total_shots_label.setText("%s" % summary.total_count)
        self.ui.cut_changes_label.setText(
            "%s" % summary.count_for_type(_DIFF_TYPES.CUT_CHANGE)
        )
        self.ui.new_shots_label.setText("%s" % summary.count_for_type(_DIFF_TYPES.NEW))
        self.ui.rescans_label.setText("%s" % summary.rescans_count)
        self.ui.omitted_label.setText(
            "%s" % summary.count_for_type(_DIFF_TYPES.OMITTED)
        )
        self.ui.reinstated_label.setText(
            "%s" % summary.count_for_type(_DIFF_TYPES.REINSTATED)
        )
        self.ui.repeated_label.setText("%s" % summary.repeated_count)
        no_link_count = summary.count_for_type(_DIFF_TYPES.NO_LINK)
        if no_link_count:
            self.ui.no_link_label.setText("%s" % no_link_count)
        else:
            self.ui.no_link_label.hide()
            self.ui.no_link_title_label.hide()
        self.ui.cancel_button.clicked.connect(self.close_dialog)
        self.ui.import_cut_button.clicked.connect(self.submit_cut)

    @QtCore.Slot()
    def submit_cut(self):
        """
        Submit the cut import and close the dialog
        """
        self._save_settings()
        update_shot_fields = self.ui.update_shot_fields_checkbox.isChecked()
        title = self.ui.title_text.text().encode("utf-8")
        # Break the to_text unicode string into a list of Shotgun Group names
        to_text_list = re.sub(",\s+", ",", self.ui.to_text.text(), flags=re.UNICODE)
        email_groups = to_text_list.encode("utf-8").split(",")
        # If there are no groups specified, remove the empty string from email_groups.
        if email_groups == [""]:
            email_groups = []
        existing_email_groups = self._sg.find("Group", [], ["code"])
        email_group_entities = []
        for email_group in email_groups:
            found = False
            for existing_email_group in existing_email_groups:
                self._logger.debug(
                    'Comparing "%s" (%s) to "%s"'
                    % (email_group, type(email_group), existing_email_group["code"])
                )
                if email_group == existing_email_group["code"]:
                    found = True
                    email_group_entities.append(existing_email_group)
            if not found:
                msg_box = QtGui.QMessageBox(
                    parent=self, icon=QtGui.QMessageBox.Critical
                )
                msg_box.setIconPixmap(
                    QtGui.QPixmap(":/tk_multi_importcut/error_64px.png")
                )
                msg_box.setText("Unknown Shotgun Group")
                msg_box.setInformativeText(
                    'Couldn\'t retrieve a group named "%s" in Shotgun.' % email_group
                )
                msg_box.setStandardButtons(QtGui.QMessageBox.Ok)
                msg_box.show()
                msg_box.raise_()
                msg_box.activateWindow()
                return
        # store user settings back into email_groups preference.
        self._user_settings.store("email_groups", email_groups)
        description = self.ui.description_text.toPlainText().encode("utf-8")
        user = self._app.context.user or {}
        self.submit.emit(
            title, user, email_group_entities, description, update_shot_fields
        )
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
