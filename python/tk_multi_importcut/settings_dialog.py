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

import re
import sgtk

from .ui.settings_dialog import Ui_settings_dialog
# Different frame mapping modes
from .constants import _ABSOLUTE_MODE, _AUTOMATIC_MODE, _RELATIVE_MODE
from sgtk.platform.qt import QtCore, QtGui
from .logger import get_logger

_ABSOLUTE_INSTRUCTIONS = """In Absolute mode, the app will map the timecode \
values from the EDL directly as frames based on the frame rate. For example, \
at 24fps 00:00:01:00 = frame 24."""

_AUTOMATIC_INSTRUCTIONS = """In Automatic mode, the app will map the timecode \
values from the EDL to the Head In value from the Shot in Shotgun. If that \
field is empty, the Default Head In value set below for New Shots will be used."""

_RELATIVE_INSTRUCTIONS = """In Relative mode, the app will map the timecode \
values from the EDL to frames based on a specific timecode/frame relationship."""


class SettingsDialog(QtGui.QDialog):
    """
    Settings dialog, available on almost each page of the animated stacked
    widget. Gives users access to app settings via a gui interface, stores those
    settings locally per user.
    """
    submit = QtCore.Signal(str, dict, dict, str, bool)

    def __init__(self, parent=None):
        """
        Instantiate a new dialog
        :param parent: a QWidget
        """
        super(SettingsDialog, self).__init__(parent)
        self._logger = get_logger()
        self.ui = Ui_settings_dialog()
        self.ui.setupUi(self)
        self._app = sgtk.platform.current_bundle()
        self._user_settings = self._app.user_settings

        # todo: the way omit_status is handled is tmp, I'm only
        # grabbing one status in the gui, but the code wants a list
        # so remember to fix the code once the gui can supply a list

        # Retrieve user settings and set UI values
        buttons = self.ui.save_settings_button_box.buttons()
        apply_button = buttons[0]
        apply_button.setText("Apply")

        # General tab
        update_shot_statuses = self._user_settings.retrieve("update_shot_statuses")
        self._set_enabled(update_shot_statuses)

        self.ui.update_shot_statuses_checkbox.setChecked(
            update_shot_statuses)
        self.ui.use_smart_fields_checkbox.setChecked(
            self._user_settings.retrieve("use_smart_fields"))
        self.ui.update_shot_statuses_checkbox.stateChanged.connect(self._set_enabled)

        self.ui.timecode_to_frame_mapping_combo_box.currentIndexChanged.connect(self._change_text)

        shot_statuses = self._app.shotgun.schema_field_read("Shot")[
            "sg_status_list"]["properties"]["display_values"]["value"]
        for status in shot_statuses:
            status = shot_statuses[status]
            self.ui.omit_status_combo_box.addItem(status)
            self.ui.reinstate_shot_if_status_is_combo_box.addItem(status)
            self.ui.reinstate_status_combo_box.addItem(status)

        self.ui.email_group_combo_box.addItem("")
        email_groups = self._app.shotgun.find("Group", [], ["code"])
        for group in email_groups:
            self.ui.email_group_combo_box.addItem(group["code"])

        self.ui.email_group_combo_box.setCurrentIndex(
            self._user_settings.retrieve("email_group"))
        self.ui.omit_status_combo_box.setCurrentIndex(
            self._user_settings.retrieve("omit_status"))
        self.ui.reinstate_shot_if_status_is_combo_box.setCurrentIndex(
            self._user_settings.retrieve("reinstate_shot_if_status_is"))
        self.ui.reinstate_status_combo_box.setCurrentIndex(
            self._user_settings.retrieve("reinstate_status"))

        # Timecode/Frames tab
        self.ui.default_frame_rate_line_edit.setText(
            self._user_settings.retrieve("default_frame_rate"))
        self.ui.timecode_to_frame_mapping_combo_box.addItems(
            ["Absolute", "Automatic", "Relative"])
        self.ui.timecode_to_frame_mapping_combo_box.setCurrentIndex(
            self._user_settings.retrieve("timecode_to_frame_mapping"))
        self.ui.timecode_mapping_line_edit.setText(
            self._user_settings.retrieve("timecode_mapping"))
        self.ui.frame_mapping_line_edit.setText(
            self._user_settings.retrieve("frame_mapping"))
        self.ui.default_head_in_line_edit.setText(
            self._user_settings.retrieve("default_head_in"))
        self.ui.default_head_duration_line_edit.setText(
            self._user_settings.retrieve("default_head_duration"))
        self.ui.default_tail_duration_line_edit.setText(
            self._user_settings.retrieve("default_tail_duration"))

        # Cancel or Save
        self.ui.save_settings_button_box.rejected.connect(self.close_dialog)
        self.ui.save_settings_button_box.accepted.connect(self.save_settings)

    @QtCore.Slot()
    def save_settings(self):
        """
        Submit the cut import and close the dialog
        """
        self._save_settings()
        self.close_dialog()

    @QtCore.Slot()
    def close_dialog(self):
        """
        Close the dialog on submit or cancel
        """
        self.close()

    def _set_enabled(self, state):
        """
        Enables or disables widgets based on a state.

        :param state: bool, whether or not the widget is enabled
        """
        self.ui.omit_status_label.setEnabled(state)
        self.ui.reinstate_shot_if_status_is_label.setEnabled(state)
        self.ui.reinstate_status_label.setEnabled(state)
        self.ui.omit_status_combo_box.setEnabled(state)
        self.ui.reinstate_shot_if_status_is_combo_box.setEnabled(state)
        self.ui.reinstate_status_combo_box.setEnabled(state)

    def _change_text(self, state):
        """
        Sets text and enables/disables certain widgets when user chooses a
        specific timecode mapping mode

        :param state: int representing index of choices (Absolute, Automatic, Relative)
        """
        if state == _ABSOLUTE_MODE:
            self.ui.timecode_to_frame_mapping_instructions_label.setText(_ABSOLUTE_INSTRUCTIONS)
            self.ui.timecode_mapping_label.hide()
            self.ui.timecode_mapping_line_edit.hide()
            self.ui.frame_mapping_label.hide()
            self.ui.frame_mapping_line_edit.hide()
            self.ui.default_head_in_line_edit.setEnabled(False)
            self.ui.default_head_in_label.setEnabled(False)
        if state == _AUTOMATIC_MODE:
            self.ui.timecode_to_frame_mapping_instructions_label.setText(_AUTOMATIC_INSTRUCTIONS)
            self.ui.timecode_mapping_label.hide()
            self.ui.timecode_mapping_line_edit.hide()
            self.ui.frame_mapping_label.hide()
            self.ui.frame_mapping_line_edit.hide()
            self.ui.default_head_in_line_edit.setEnabled(True)
            self.ui.default_head_in_label.setEnabled(True)
        if state == _RELATIVE_MODE:
            self.ui.timecode_to_frame_mapping_instructions_label.setText(_RELATIVE_INSTRUCTIONS)
            self.ui.timecode_mapping_label.show()
            self.ui.timecode_mapping_line_edit.show()
            self.ui.frame_mapping_label.show()
            self.ui.frame_mapping_line_edit.show()
            self.ui.default_head_in_line_edit.setEnabled(False)
            self.ui.default_head_in_label.setEnabled(False)

    def _save_settings(self):
        """
        Save user settings from current UI values
        """

        error = False

        # General tab
        update_shot_statuses = self.ui.update_shot_statuses_checkbox.isChecked()
        self._user_settings.store("update_shot_statuses", update_shot_statuses)
        use_smart_fields = self.ui.use_smart_fields_checkbox.isChecked()
        self._user_settings.store("use_smart_fields", use_smart_fields)
        email_group = self.ui.email_group_combo_box.currentIndex()
        self._user_settings.store("email_group", email_group)
        omit_status = self.ui.omit_status_combo_box.currentIndex()
        self._user_settings.store("omit_status", omit_status)
        reinstate_shot_if_status_is = self.ui.reinstate_shot_if_status_is_combo_box.currentIndex()
        self._user_settings.store("reinstate_shot_if_status_is", reinstate_shot_if_status_is)
        reinstate_status = self.ui.reinstate_status_combo_box.currentIndex()
        self._user_settings.store("reinstate_status", reinstate_status)

        # Timecode/Frames tab
        default_frame_rate = self.ui.default_frame_rate_line_edit.text()
        try:
            fps = float(default_frame_rate)
            assert fps > 0, "Value must be positive."
            self._user_settings.store("default_frame_rate", default_frame_rate)
        except Exception, e:
            error = True
            self._logger.error('Could not set frame rate to "%s": %s' % (default_frame_rate, e))

        timecode_to_frame_mapping = self.ui.timecode_to_frame_mapping_combo_box.currentIndex()
        self._user_settings.store("timecode_to_frame_mapping", timecode_to_frame_mapping)

        timecode_mapping = self.ui.timecode_mapping_line_edit.text()
        if re.search("^\d{2}:\d{2}:\d{2}[:.;]\d{2}$", timecode_mapping):
            self._user_settings.store("timecode_mapping", timecode_mapping)
        else:
            error = True
            self._logger.error('Could not set timecode mapping to "%s": %s' % (
                timecode_mapping, "Did not match pattern 00:00:00:00."))

        frame_mapping = self.ui.frame_mapping_line_edit.text()
        try:
            int(frame_mapping)
            self._user_settings.store("frame_mapping", frame_mapping)
        except Exception, e:
            error = True
            self._logger.error('Could not set frame mapping to "%s": %s' % (frame_mapping, e))

        default_head_in = self.ui.default_head_in_line_edit.text()
        try:
            int(default_head_in)
            self._user_settings.store("default_head_in", default_head_in)
        except Exception, e:
            error = True
            self._logger.error('Could not set default head in to "%s": %s' % (default_head_in, e))

        default_head_duration = self.ui.default_head_duration_line_edit.text()
        try:
            dhd = int(default_head_duration)
            assert dhd >= 0, "Value can't be nagative."
            self._user_settings.store("default_head_duration", default_head_duration)
        except Exception, e:
            error = True
            self._logger.error('Could not set default head duration to "%s": %s' % (
                default_head_duration, e))

        default_tail_duration = self.ui.default_tail_duration_line_edit.text()
        try:
            dtd = int(default_tail_duration)
            assert dtd >= 0, "Value can't be negative."
            self._user_settings.store("default_tail_duration", default_tail_duration)
        except Exception, e:
            error = True
            self._logger.error('Could not set default head duration to "%s": %s' % (
                default_head_duration, e))

        if error is False:
            self._logger.info("User settings saved.")
