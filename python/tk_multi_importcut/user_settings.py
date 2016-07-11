# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk
from .constants import _ABSOLUTE_MODE
from .constants import _DROP_STEP, _SUMMARY_STEP, _LAST_STEP


class UserSetting(object):
    """
    A User setting, with a default value and the wizard steps it affects.

    If the value for the setting is changed and the current step is bigger or
    equal to one of the affected steps, a reset will be needed.
    """
    def __init__(self, default, affects=None):
        """
        Instantiate a new UserSetting with the given default value, and affecting
        the given wizard step.

        :param default: Arbitrary default value for this setting
        :param affects: (optional) list of wizard steps being affected by changes
        """
        super(UserSetting, self).__init__()
        self._default = default
        self._affects = affects or []

class UserSettings(object):
    """
    Class for retrieving and managing User Settings.
    """
    # Our settings definition, with their default value and the steps they affect,
    # if any
    __settings_def = {
        "update_shot_statuses"          : UserSetting(True),
        "use_smart_fields"              : UserSetting(False,            [_SUMMARY_STEP]),
        "email_groups"                  : UserSetting([]),
        "omit_status"                   : UserSetting("omt"),
        "reinstate_status"              : UserSetting("Previous Status"),
        "reinstate_shot_if_status_is"   : UserSetting(["omt", "hld"],   [_SUMMARY_STEP]),
        "default_frame_rate"            : UserSetting("24",             [_DROP_STEP, _SUMMARY_STEP]),
        "timecode_to_frame_mapping"     : UserSetting(_ABSOLUTE_MODE,   [_SUMMARY_STEP]),
        "timecode_mapping"              : UserSetting("00:00:00:00",    [_SUMMARY_STEP]),
        "frame_mapping"                 : UserSetting("1000",           [_SUMMARY_STEP]),
        "default_head_in"               : UserSetting("1001",           [_SUMMARY_STEP]),
        "default_head_duration"         : UserSetting("8",              [_SUMMARY_STEP]),
        "default_tail_duration"         : UserSetting("8",              [_SUMMARY_STEP]),
        "preload_entity_type"           : UserSetting(None)
    }

    def __init__(self):
        # Base class init
        super(UserSettings, self).__init__()
        # Provide access to the user settings fw module.
        self._disk = sgtk.platform.current_bundle().user_settings
        # Retrieve our settings from disk.
        self._settings = self._retrieve()

    @property
    def all(self):
        """
        Convenience method providing access to all settings.

        :returns: a dict of settings.
        """
        return self._settings

    def _retrieve(self):
        """
        Returns a dict of settings stored to disk by the User Settings fw module.

        :returns: dict of settings.
        """
        settings = {}
        for setting in self.__settings_def:
            settings[setting] = self._disk.retrieve(setting)
        return settings

    def get(self, setting):
        """
        Returns the value for a specified setting.

        :param setting: String, the name of the setting to return.
        :returns: The value associated with the setting.
        """
        return self._settings[setting]

    def reset_needed(self, settings, step):
        """
        Determines if resets are needed for some wizard steps, given a dictionary of
        settings values.

        Compare the values stored in the given dictionary to the current ones. If
        they changed, check which wizard step they affect, if any.

        :param settings: A dictionary of settings to check against current values.
        :param step: The current wizard step.
        :returns: A possibly empty sorted list of steps for which a reset is needed.
        """
        # Use a set to ensure uniqueness
        affected = set()
        for setting in settings:
            if settings[setting] != self._settings[setting]:
                for affected_step in self.__settings_def[setting]._affects:
                    if step >= affected_step:
                        affected.add(affected_step)
        # Return a sorted list
        return sorted(list(affected))

    def save(self, settings):
        """
        Saves incoming dict of settings to disk.

        :param settings: A dict of settings to store to disk.
        """
        for setting in settings:
            self._disk.store(setting, settings[setting])
        self._settings = self._retrieve()

    def reset(self):
        """
        Restores all settings to their default values and saves to disk.
        """
        for setting in self.__settings_def:
            self._disk.store(setting, self.__settings_def[setting]._default)
        self._settings = self._retrieve()

    def update(self):
        """
        Sets user settings to their default values if they have None values, and saves to disk.
        """
        for setting in self.__settings_def:
            if self._settings[setting] is None:
                self._disk.store(setting, self.__settings_def[setting]._default)
        self._settings = self._retrieve()

    def clear(self):
        """
        Sets all settings to None and saves to disk.
        """
        for setting in self.__settings_def:
            self._disk.store(setting, None)
        self._settings = self._retrieve()
