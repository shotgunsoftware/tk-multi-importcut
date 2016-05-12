# Copyright (c) 2016 Shotgun Software Inc.
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
from .cut_diff import CutDiff
# Different frame mapping modes
from .constants import _ABSOLUTE_MODE, _AUTOMATIC_MODE, _RELATIVE_MODE
from sgtk.platform.qt import QtCore, QtGui
from .logger import get_logger

edl = sgtk.platform.import_framework("tk-framework-editorial", "edl")

_ABSOLUTE_INSTRUCTIONS = "In Absolute mode, the app will map the timecode \
values from the EDL directly as frames based on the frame rate. For example, \
at 24fps 00:00:01:00 = frame 24."

_AUTOMATIC_INSTRUCTIONS = "In Automatic mode, the app will map the timecode \
values from the EDL to the Head In value from the Shot in Shotgun. If that \
field is empty, the Default Head In value set below for New Shots will be used."

_RELATIVE_INSTRUCTIONS = "In Relative mode, the app will map the timecode \
values from the EDL to frames based on a specific timecode/frame relationship."

_BAD_GROUP_MSG = '"%s" does not match a valid Group in Shotgun. Please enter \
another Group or create "%s" in Shotgun to proceed.'

_BAD_STATUS_MSG = "The following statuses for reinstating Shots do not match \
valid statuses in Shotgun:\n\n%s\n\nPlease enter another status to proceed."

_BAD_TIMECODE_MSG = '"%s" is not a valid timecode value. The Timecode Mapping \
must match the pattern ##.##.##.##. See message below for more details.'

_BAD_SMART_FIELDS_MSG = "The Smart Cut fields do not appear to be enabled. \
Please check your Shotgun site."


class SettingsDialog(QtGui.QDialog):
    """
    Settings dialog, available on almost each page of the animated stacked
    widget. Gives users access to app settings via a gui interface, stores those
    settings locally per user.
    """
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
        self._shot_schema = None

        # Retrieve user settings and set UI values
        try:
            # General tab

            # Setting whether or not the shot status fields are enabled
            # and updating that if the user turns them on/off w/the checkbox.
            update_shot_statuses = self._user_settings.retrieve("update_shot_statuses")
            self._set_enabled(update_shot_statuses)
            self.ui.update_shot_statuses_checkbox.setChecked(update_shot_statuses)
            self.ui.update_shot_statuses_checkbox.stateChanged.connect(self._set_enabled)

            self.ui.use_smart_fields_checkbox.setChecked(
                self._user_settings.retrieve("use_smart_fields"))

            self.ui.timecode_to_frame_mapping_combo_box.currentIndexChanged.connect(
                self._change_text)

            # Turning the email_groups list into user editable csv text
            email_groups = ", ".join(self._user_settings.retrieve("email_groups"))
            self.ui.email_groups_line_edit.setText(email_groups)

            # We're storing status lists with their internal codes and matching
            # them by searching through current status codes to find the drop
            # down index. If the status code is missing, the index is set to 0
            # and we throw an error to warn the user. This should probably happen
            # when the app launches, not only when the settings dialog is opened.
            # The reason we warn the user is: if someone deletes a status from
            # sg that this app references, it obviously can't be used anymore, so
            # we arbitrarily choose whatever status is at 0.
            omit_status = self._user_settings.retrieve("omit_status")
            reinstate_status = self._user_settings.retrieve("reinstate_status")
            self._shot_schema = self._app.shotgun.schema_field_read("Shot")
            shot_statuses = self._shot_schema[
                "sg_status_list"]["properties"]["valid_values"]["value"]
            self.ui.omit_status_combo_box.addItem("")
            self.ui.reinstate_status_combo_box.addItem("")
            # starting with index of 1 because we already have an empty string
            # item in the omit_status and reinstate_status combo boxes
            index = 1
            found_omit_index, found_reinstate_index = [False, False]
            for status in shot_statuses:
                if omit_status == status:
                    omit_index = index
                    found_omit_index = True
                if reinstate_status == status:
                    reinstate_index = index
                    found_reinstate_index = True
                self.ui.omit_status_combo_box.addItem(status)
                self.ui.reinstate_status_combo_box.addItem(status)
                index += 1
            if found_omit_index:
                self.ui.omit_status_combo_box.setCurrentIndex(omit_index)
            else:
                self.ui.omit_status_combo_box.setCurrentIndex(0)
            self.ui.reinstate_status_combo_box.addItem("Previous Status")
            if found_reinstate_index:
                self.ui.reinstate_status_combo_box.setCurrentIndex(reinstate_index)
            elif reinstate_status == "Previous Status":
                # +1 to account for empty item at the head of the combo box list.
                self.ui.reinstate_status_combo_box.setCurrentIndex(len(shot_statuses) + 1)
            else:
                self.ui.reinstate_status_combo_box.setCurrentIndex(0)

            # Turning the reinstate status list into user editable csv text
            statuses = ", ".join(self._user_settings.retrieve("reinstate_shot_if_status_is"))
            self.ui.reinstate_shot_if_status_is_line_edit.setText(statuses)

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
            self.ui.cancel_button.clicked.connect(self.close_dialog)
            self.ui.apply_button.clicked.connect(self.save_settings)

        except Exception, e:
            # This is a bit of code for dealing with bad values (if prefs var changes type).
            # If something goes wrong, reset all settings to default next time the app is run
            self._user_settings.store("reset_settings", True)
            self._logger.error(
                    "Corrupt user settings will be reset to default, restart Import Cut: %s" % (e))

    @QtCore.Slot()
    def save_settings(self):
        """
        Save settings and close the dialog.
        """
        if self._save_settings():
            self.close_dialog()

    @QtCore.Slot()
    def close_dialog(self):
        """
        Close the dialog on save or cancel.
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
        self.ui.reinstate_shot_if_status_is_line_edit.setEnabled(state)
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

    def _pop_error(self, title, message, error=None):
        """
        Helper method to display messages during validation and optional errors.

        :param title: The message type (for example "User Input")
        :param message: Easy to read message for the user
        :param error: Error coming back from an Exception, included in "Additional Details"
        """
        msg_box = QtGui.QMessageBox(
            parent=self,
            icon=QtGui.QMessageBox.Critical
        )
        msg_box.setIconPixmap(QtGui.QPixmap(":/tk_multi_importcut/error_64px.png"))
        if error:
            msg_box.setDetailedText("%s" % error)
        msg_box.setText("%s\n\n%s" % (title, message))
        msg_box.setStandardButtons(QtGui.QMessageBox.Ok)
        msg_box.show()
        msg_box.raise_()
        msg_box.activateWindow()

    def _save_settings(self):
        """
        Validate and save user settings from current UI values.

        :returns: True if all settings can be safetly saved, and None otherwise.
        """

        # General tab

        update_shot_statuses = self.ui.update_shot_statuses_checkbox.isChecked()
        self._user_settings.store("update_shot_statuses", update_shot_statuses)

        use_smart_fields = self.ui.use_smart_fields_checkbox.isChecked()
        if use_smart_fields and not self._shot_schema.get("smart_cut_duration"):
            self._pop_error("User Input", _BAD_SMART_FIELDS_MSG)
            return
        self._user_settings.store("use_smart_fields", use_smart_fields)

        # Break the to_text string into a list of Shotgun Group names
        to_text_list = re.sub(',\s+', ',', self.ui.email_groups_line_edit.text())
        email_groups = to_text_list.split(",")
        # If there is no text, reset email_group to be an empty list
        if email_groups == [""]:
            email_groups = []
        existing_email_groups = self._app.shotgun.find("Group", [], ["code"])
        existing_email_groups_list = []
        for existing_group in existing_email_groups:
            existing_email_groups_list.append(existing_group["code"])
        for email_group in email_groups:
            if email_group not in existing_email_groups_list:
                self._pop_error("User Input", _BAD_GROUP_MSG % (email_group, email_group))
                return
        self._user_settings.store("email_groups", email_groups)

        omit_status = self.ui.omit_status_combo_box.currentText()
        if not omit_status and update_shot_statuses:
            self._pop_error("User Input", "%s" % (
                "Please select an Omit Status."))
            return
        self._user_settings.store("omit_status", omit_status)

        reinstate_status = self.ui.reinstate_status_combo_box.currentText()
        if not reinstate_status and update_shot_statuses:
            self._pop_error("User Input", "%s" % (
                "Please select a Reinstate Status"))
            return
        self._user_settings.store("reinstate_status", reinstate_status)

        statuses = self.ui.reinstate_shot_if_status_is_line_edit.text().replace(
            ", ", ",").split(",")
        existing_statuses = self._shot_schema[
            "sg_status_list"]["properties"]["valid_values"]["value"]
        bad_statuses = []
        for status in statuses:
            if status not in existing_statuses and update_shot_statuses:
                bad_statuses.append('"%s"' % status)
        if bad_statuses:
            bad_statuses = "\n".join(bad_statuses)
            self._pop_error("User Input", _BAD_STATUS_MSG % (bad_statuses))
            return
        self._user_settings.store("reinstate_shot_if_status_is", statuses)

        # Timecode/Frames tab

        default_frame_rate = self.ui.default_frame_rate_line_edit.text()
        try:
            fps = float(default_frame_rate)
            assert fps > 0, "Value must be positive."
            self._user_settings.store("default_frame_rate", default_frame_rate)
        except Exception, e:
            self._pop_error("User Input", 'Could not set frame rate to "%s."' % (
                default_frame_rate), e)
            return

        timecode_to_frame_mapping = self.ui.timecode_to_frame_mapping_combo_box.currentIndex()
        self._user_settings.store("timecode_to_frame_mapping", timecode_to_frame_mapping)

        timecode_mapping = self.ui.timecode_mapping_line_edit.text()
        try:
            # Using the timecode module to validate the timecode_mapping value
            edl.Timecode(timecode_mapping, fps=fps)
            self._user_settings.store("timecode_mapping", timecode_mapping)
        except Exception, e:
            self._pop_error("User Input", _BAD_TIMECODE_MSG % timecode_mapping, e)
            return

        frame_mapping = self.ui.frame_mapping_line_edit.text()
        try:
            int(frame_mapping)
            self._user_settings.store("frame_mapping", frame_mapping)
        except Exception, e:
            self._pop_error("User Input", 'Could not set frame mapping to "%s."' % (
                frame_mapping), e)
            return

        default_head_in = self.ui.default_head_in_line_edit.text()
        try:
            int(default_head_in)
            self._user_settings.store("default_head_in", default_head_in)
        except Exception, e:
            self._pop_error("User Input", 'Could not set default head in to "%s."' % (
                default_head_in), e)
            return

        default_head_duration = self.ui.default_head_duration_line_edit.text()
        try:
            dhd = int(default_head_duration)
            assert dhd >= 0, "Value can't be nagative."
            self._user_settings.store("default_head_duration", default_head_duration)
        except Exception, e:
            self._pop_error("User Input", 'Could not set default head duration to "%s."' % (
                default_head_duration), e)
            return

        default_tail_duration = self.ui.default_tail_duration_line_edit.text()
        try:
            dtd = int(default_tail_duration)
            assert dtd >= 0, "Value can't be negative."
            self._user_settings.store("default_tail_duration", default_tail_duration)
        except Exception, e:
            self._pop_error("User Input", 'Could not set default tail duration to "%s."' % (
                default_tail_duration), e)
            return

        CutDiff.retrieve_default_timecode_frame_mapping()

        self._logger.info("User settings saved.")
        return True
