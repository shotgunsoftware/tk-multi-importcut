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

from .ui.settings_dialog import Ui_settings_dialog
from .cut_diff import CutDiff
from .user_settings import UserSettings
# Different frame mapping modes
from .constants import _ABSOLUTE_MODE, _AUTOMATIC_MODE, _RELATIVE_MODE
# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
from sgtk.platform.qt import QtCore, QtGui
from .logger import get_logger

edl = sgtk.platform.import_framework("tk-framework-editorial", "edl")

# Various messages or templates used in the UI or as error messages
_ABSOLUTE_INSTRUCTIONS = "In Absolute mode, the app will map the timecode \
values from the EDL directly as frames based on the frame rate. For example, \
at 24fps 00:00:01:00 = frame 24."

_AUTOMATIC_INSTRUCTIONS = "In Automatic mode, the app will map the timecode \
values from the EDL to the Head In value from the Shot in Shotgun. If that \
field is empty, the Default Head In value set below for New Shots will be used."

_RELATIVE_INSTRUCTIONS = "In Relative mode, the app will map the timecode \
values from the EDL to frames based on a specific timecode/frame relationship."

_BAD_GROUP_MSG = "\"%s\" does not match a valid Group in Shotgun. Please enter \
another Group or create \"%s\" in Shotgun to proceed."

_BAD_STATUS_MSG = "The following statuses for reinstating Shots do not match \
valid statuses in Shotgun:\n\n%s\n\nPlease enter another status to proceed."

_BAD_TIMECODE_MSG = "\"%s\" is not a valid timecode value. The Timecode Mapping \
must match the pattern hh:mm:ss:ff and contain valid timecode."

_BAD_SMART_FIELDS_MSG = "The Smart Cut fields do not appear to be enabled. \
Please check your Shotgun site."

_CHANGED_SETTINGS_MSG = "Applying these Settings updates will require an app \
restart. All Import Cut progress will be lost."

_CORRUPT_SETTINGS_MSG = "Corrupt user settings have been reset to default, \
restart Import Cut: %s"


class SettingsError(ValueError):
    """
    Helper class for raising Settings exceptions.
    """
    def __init__(self, *args, **kwargs):
        """
        Instantiate a new SettingsError.

        Optional "details" can be provided in the parameters dictionary.

        :param args: Usual Exception parameters list
        :param kwargs: Usual Exception parameters dictionary with the added
                       'details' key
        """
        self._details = None
        if "details" in kwargs:
            # If we have some details, remove them from parameters sent to the
            # base class
            self._details = kwargs.pop("details")
        super(SettingsError, self).__init__(*args, **kwargs)

    @property
    def details(self):
        """
        Return details for this exception, if any
        :returns: None or some arbitrary data
        """
        return self._details


class SettingsDialog(QtGui.QDialog):
    """
    Settings dialog, available on almost each page of the animated stacked
    widget. Gives users access to app settings via a gui interface, stores those
    settings locally per user.
    """
    def __init__(self, parent=None, step=None):
        """
        Instantiate a new dialog with the given parent for the current step

        The current step is not used yet, but could be later to refine our
        'restart needed' decision on some value changes

        :param parent: a QWidget
        :param step: The current app step we are at
        """
        super(SettingsDialog, self).__init__(parent)
        self.setModal(True)
        # This is not used yet, but later we will be able to check if changes
        # made require a restart, baser on the step we are at
        self._step = step
        self._logger = get_logger()
        self.ui = Ui_settings_dialog()
        self.ui.setupUi(self)
        self.setWindowTitle("Settings")
        self._app = sgtk.platform.current_bundle()
        self._user_settings = UserSettings()
        self._shot_schema = None

        # Retrieve user settings and set UI values
        try:
            # Setting whether or not the shot status fields are enabled
            # and updating that if the user turns them on/off w/the checkbox.
            self._set_enabled(
                self._user_settings.get("update_shot_statuses"))
            self.ui.update_shot_statuses_checkbox.setChecked(
                self._user_settings.get("update_shot_statuses"))
            self.ui.update_shot_statuses_checkbox.stateChanged.connect(self._set_enabled)

            self.ui.use_smart_fields_checkbox.setChecked(
                self._user_settings.get("use_smart_fields"))
            self.ui.timecode_to_frame_mapping_combo_box.currentIndexChanged.connect(
                self._tc_mapping_mode_changed)

            # Turning the email_groups list into user editable csv text
            email_groups = ", ".join(self._user_settings.get("email_groups"))
            self.ui.email_groups_line_edit.setText(email_groups)

            # We're storing status lists with their internal codes and matching
            # them by searching through current status codes to find the drop
            # down index. If the status code is missing, the index is set to 0
            # and we throw an error to warn the user. This should probably happen
            # when the app launches, not only when the settings dialog is opened.
            # The reason we warn the user is: if someone deletes a status from
            # sg that this app references, it obviously can't be used anymore, so
            # we arbitrarily choose whatever status is at 0.
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
                if self._user_settings.get("omit_status") == status:
                    omit_index = index
                    found_omit_index = True
                if self._user_settings.get("reinstate_status") == status:
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
            elif self._user_settings.get("reinstate_status") == "Previous Status":
                # +1 to account for empty item at the head of the combo box list.
                self.ui.reinstate_status_combo_box.setCurrentIndex(len(shot_statuses) + 1)
            else:
                self.ui.reinstate_status_combo_box.setCurrentIndex(0)

            # Turning the reinstate status list into user editable csv text
            statuses = ", ".join(self._user_settings.get("reinstate_shot_if_status_is"))
            self.ui.reinstate_shot_if_status_is_line_edit.setText(statuses)

            # Timecode/Frames tab
            self.ui.default_frame_rate_line_edit.setText(
                self._user_settings.get("default_frame_rate"))
            # Add a validator to ensure only positive float values are entered
            float_validator = QtGui.QDoubleValidator(bottom=0.0, decimals=6, parent=self)
            float_validator.setNotation(QtGui.QDoubleValidator.StandardNotation)
            self.ui.default_frame_rate_line_edit.setValidator(float_validator)

            self.ui.timecode_mapping_line_edit.setText(
                self._user_settings.get("timecode_mapping"))
            # Set a timecode input mask to drive user typing
            self.ui.timecode_mapping_line_edit.setInputMask("99:99:99:99")

            self.ui.frame_mapping_line_edit.setText(
                self._user_settings.get("frame_mapping"))
            # Ensure we only get int values
            self.ui.frame_mapping_line_edit.setValidator(
                QtGui.QIntValidator(self)
            )
            # Do this only after we set timecode and frame mapping values
            # otherwise an error will be raised
            self.ui.timecode_to_frame_mapping_combo_box.addItems(
                ["Absolute", "Automatic", "Relative"])
            self.ui.timecode_to_frame_mapping_combo_box.setCurrentIndex(
                self._user_settings.get("timecode_to_frame_mapping"))

            self.ui.default_head_in_line_edit.setText(
                self._user_settings.get("default_head_in"))
            # Ensure we only get int values
            self.ui.default_head_in_line_edit.setValidator(
                QtGui.QIntValidator(self)
            )

            self.ui.default_head_duration_line_edit.setText(
                self._user_settings.get("default_head_duration"))
            # Ensure we only get int values >= 0
            self.ui.default_head_duration_line_edit.setValidator(
                QtGui.QIntValidator(bottom=0, parent=self)
            )

            self.ui.default_tail_duration_line_edit.setText(
                self._user_settings.get("default_tail_duration"))
            # Ensure we only get int values >= 0
            self.ui.default_tail_duration_line_edit.setValidator(
                QtGui.QIntValidator(bottom=0, parent=self)
            )

            # Cancel or Save
            self.ui.cancel_button.clicked.connect(self.discard_settings)
            self.ui.apply_button.clicked.connect(self.save_settings)

        except Exception, e:
            # Reset user settings if they are corrupt. This can happen if users using an older
            # version of import cut have settings saved that don't match the variable type of
            # the current settings. For example, if they have the old email_groups setting
            # that was at one point a dict and is now a list. This may happen again if these
            # settings are changed in unpredictable ways and conflict with local user settings
            # we don't have accesss to.
            self._user_settings.reset()
            self._logger.error(_CORRUPT_SETTINGS_MSG % (e))

    @QtCore.Slot()
    def save_settings(self):
        """
        Save settings and close the dialog.
        """
        try:
            if self._validate_and_save_settings():
                self.close_dialog()
        except SettingsError, se:
            # Pop up specialised error dialog.
            self._pop_error("User Input", str(se), se.details)
        except Exception, e:
            # General case.
            self._logger.exception(e)

    @QtCore.Slot()
    def discard_settings(self):
        """
        Cancel changes to settings and close the dialog.
        """
        self._logger.info("User canceled, Settings not saved.")
        self.close()

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

    @QtCore.Slot(int)
    def _tc_mapping_mode_changed(self, state):
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

    def _pop_error(self, reason, message, details=None):
        """
        Helper method to display messages during validation and optional errors.

        :param reason: The message type (for example "User Input").
        :param message: Easy to read message for the user.
        :param details: Error coming back from an Exception, included in "Show Details."
        """
        msg_box = QtGui.QMessageBox(
            parent=self,
            icon=QtGui.QMessageBox.Critical
        )
        msg_box.setIconPixmap(QtGui.QPixmap(":/tk_multi_importcut/error_64px.png"))
        if details:
            msg_box.setDetailedText("%s" % details)
        msg_box.setText("%s\n\n%s" % (reason, message))
        msg_box.setStandardButtons(QtGui.QMessageBox.Ok)
        msg_box.show()
        msg_box.raise_()
        msg_box.activateWindow()

    def _validate_timecode_mapping_input(self):
        """
        Validate timecode mapping values
        :raises: SettingErrors if some input is not valid
        """
        # We have some validators on these fields but we still need to check
        # for partially edited values, e.g. empty fields
        if not self.ui.timecode_mapping_line_edit.hasAcceptableInput():
            raise SettingsError("Timecode Mapping must be set")
        if not self.ui.frame_mapping_line_edit.hasAcceptableInput():
            raise SettingsError("Frame Mapping must be set")
        if not self.ui.default_frame_rate_line_edit.hasAcceptableInput():
            raise SettingsError("Default Frame Rate must be set")

        timecode_mapping = self.ui.timecode_mapping_line_edit.text()
        fps = float(self.ui.default_frame_rate_line_edit.text())
        try:
            # Using the timecode module to validate the timecode_mapping value with
            # the given fps, our input mask can't check for hh mm ss ff validity,
            # e.g. check that ff is not bigger than the fps
            edl.Timecode(timecode_mapping, fps=fps)
        except Exception, e:
            raise SettingsError(_BAD_TIMECODE_MSG % timecode_mapping, details=e)

    def _validate_and_save_settings(self):
        """
        Validate user settings from current UI values.

        :returns: True if all settings can be safetly saved, and None otherwise.
        """

        # General tab
        update_shot_statuses = self.ui.update_shot_statuses_checkbox.isChecked()

        use_smart_fields = self.ui.use_smart_fields_checkbox.isChecked()
        if use_smart_fields and not self._shot_schema.get("smart_cut_duration"):
            raise SettingsError(_BAD_SMART_FIELDS_MSG)

        # Break the to_text string into a list of Shotgun Group names
        # Remove spaces after a ","
        to_text_list = re.sub(",\s+", ",", self.ui.email_groups_line_edit.text())
        # And then split with ","
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
                raise SettingsError(_BAD_GROUP_MSG % (email_group, email_group))

        omit_status = self.ui.omit_status_combo_box.currentText()
        if not omit_status and update_shot_statuses:
            raise SettingsError("%s" % ("Please select an Omit Status."))

        reinstate_status = self.ui.reinstate_status_combo_box.currentText()
        if not reinstate_status and update_shot_statuses:
            raise SettingsError("%s" % ("Please select a Reinstate Status"))

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
            raise SettingsError(_BAD_STATUS_MSG % (bad_statuses))

        new_values = {
            "update_shot_statuses": update_shot_statuses,
            "use_smart_fields": use_smart_fields,
            "email_groups": email_groups,
            "omit_status": omit_status,
            "reinstate_status": reinstate_status,
            "reinstate_shot_if_status_is": statuses,
        }

        # Timecode/Frames tab
        # We have some validators or imput masks to prevent bad values to be
        # entered, but we still need to check for partially edited values, e.g.
        # an empty field
        if not self.ui.default_frame_rate_line_edit.hasAcceptableInput():
            raise SettingsError("Default Frame Rate must be set")

        default_frame_rate = self.ui.default_frame_rate_line_edit.text()
        fps = float(default_frame_rate)
        new_values["default_frame_rate"] = default_frame_rate

        timecode_to_frame_mapping = self.ui.timecode_to_frame_mapping_combo_box.currentIndex()
        new_values["timecode_to_frame_mapping"] = timecode_to_frame_mapping

        # timecode and frame mapping are only used in relative mode, and their widgets
        # are not visible otherwise, so only save them if this mode is on
        if timecode_to_frame_mapping == _RELATIVE_MODE:
            self._validate_timecode_mapping_input()
            new_values["timecode_mapping"] = self.ui.timecode_mapping_line_edit.text()
            new_values["frame_mapping"] = self.ui.frame_mapping_line_edit.text()

        if not self.ui.default_head_in_line_edit.hasAcceptableInput():
            raise SettingsError("Default Head In must be set")
        new_values["default_head_in"] = self.ui.default_head_in_line_edit.text()

        if not self.ui.default_head_duration_line_edit.hasAcceptableInput():
            raise SettingsError("Default Head Duration must be set")
        new_values["default_head_duration"] = self.ui.default_head_duration_line_edit.text()

        if not self.ui.default_tail_duration_line_edit.hasAcceptableInput():
            raise SettingsError("Default Tail Duration must be set")
        new_values["default_tail_duration"] = self.ui.default_tail_duration_line_edit.text()


        # At the moment certain settings require a refresh to be properly accounted for
        # while processing the EDL, etc. As a stop-gap, we warn the user and give them
        # the opportunity to restart the app if one of the known "non-refreshable"
        # settings has been changed (#36605).
        if (self._user_settings.restart_needed(new_values)):
            msg_box = QtGui.QMessageBox(
                parent=self,
                icon=QtGui.QMessageBox.Critical
            )
            msg_box.setIconPixmap(QtGui.QPixmap(":/tk_multi_importcut/error_64px.png"))
            msg_box.setText("%s\n\n%s" % ("Settings", _CHANGED_SETTINGS_MSG))
            cancel_button = msg_box.addButton("Cancel", QtGui.QMessageBox.YesRole)
            apply_button = msg_box.addButton("Apply and Quit", QtGui.QMessageBox.NoRole)
            apply_button.clicked.connect(lambda : self._save_settings_and_close(new_values))
            msg_box.show()
            msg_box.raise_()
            msg_box.activateWindow()
            return
        self._save_settings(new_values)
        return True

    def _save_settings_and_close(self, new_values):
        """
        Stores settings and closes the parent dialog since the App needs to be restarted.
        """
        self._save_settings(new_values)
        self.parent().close()

    def _save_settings(self, new_values):
        """
        Save user settings.
        :param new_values: A dictionary with the new values
        """
        self._logger.debug("New values %s" % new_values)
        self._user_settings.save(new_values)
        # An attempt to refresh some of the values, but it doesn't entirely work.
        CutDiff.retrieve_default_timecode_frame_mapping()
        self.close_dialog()
        self._logger.info("User settings saved.")
