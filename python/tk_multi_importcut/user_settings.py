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
    A User setting, with a default value and the step it affects.

    If the value for the setting is changed and the current step is bigger or
    equal to the affected step, a reset will be needed.
    """
    def __init__(self, default, affects=_LAST_STEP):
        """
        Instantiate a new UserSetting with the given default value, and affecting
        the given step.

        :param default: Arbitrary default value for this setting
        :param affects: (optional) first wizard step being affected by changes
        """
        super(UserSetting, self).__init__()
        self._default = default
        self._affects = affects

class UserSettings(object):
    """
    Class for retrieving and managing User Settings.
    """
    # Our settings definition, with their default value and the step they affect,
    # if any
    __settings_def = {
        "update_shot_statuses"          : UserSetting(True),
        "use_smart_fields"              : UserSetting(False,            _SUMMARY_STEP),
        "email_groups"                  : UserSetting([]),
        "omit_status"                   : UserSetting("omt"),
        "reinstate_status"              : UserSetting("Previous Status"),
        "reinstate_shot_if_status_is"   : UserSetting(["omt", "hld"],   _SUMMARY_STEP),
        "default_frame_rate"            : UserSetting("24",             _DROP_STEP),
        "timecode_to_frame_mapping"     : UserSetting(_ABSOLUTE_MODE,   _SUMMARY_STEP),
        "timecode_mapping"              : UserSetting("00:00:00:00",    _SUMMARY_STEP),
        "frame_mapping"                 : UserSetting("1000",           _SUMMARY_STEP),
        "default_head_in"               : UserSetting("1001",           _SUMMARY_STEP),
        "default_head_duration"         : UserSetting("8",              _SUMMARY_STEP),
        "default_tail_duration"         : UserSetting("8",              _SUMMARY_STEP),
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
        Determines if a restart of the app is needed given a dict of settings.

        :param settings: A dict of settings to check against self.__settings_def.
        :returns: True if restart is needed, False otherwise.
        """
        for setting in settings:
            if (settings[setting] != self._settings[setting] and
                step >= self.__settings_def[setting]._affects):
                return True
        return False

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
