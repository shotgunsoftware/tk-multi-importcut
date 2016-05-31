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

import sgtk
from .constants import _ABSOLUTE_MODE


class UserSettings(object):
    """
    Class for retrieving and managing User Settings.
    """

    # Define default settings.
    _defaults = {"update_shot_statuses": True,
                 "use_smart_fields": False,
                 "email_groups": [],
                 "omit_status": "omt",
                 "reinstate_status": "Previous Status",
                 "reinstate_shot_if_status_is": ["omt", "hld"],
                 "default_frame_rate": "24",
                 "timecode_to_frame_mapping": _ABSOLUTE_MODE,
                 "timecode_mapping": "00:00:00:00",
                 "frame_mapping": "1000",
                 "default_head_in": "1001",
                 "default_head_duration": "8",
                 "default_tail_duration": "8",
                 "preload_entity_type": None}

    # If any of these keys in the _defaults dict are changed, a restart of the
    # app is required.
    _restart_keys = ["update_shot_statuses",
                     "use_smart_fields",
                     "omit_status",
                     "timecode_mapping",
                     "reinstate_shot_if_status_is",
                     "timecode_to_frame_mapping",
                     "default_frame_rate",
                     "frame_mapping",
                     "default_head_in",
                     "default_head_duration",
                     "default_tail_duration"]

    def __init__(self):
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
        for setting in self._defaults:
            settings[setting] = self._disk.retrieve(setting)
        return settings

    def get(self, setting):
        """
        Returns the value for a specified setting.

        :param setting: String, the name of the setting to return.
        :returns: The value associated with the setting.
        """
        return self._settings[setting]

    def restart_check(self, settings):
        """
        Determines if a restart of the app is needed given a dict of settings.

        :param settings: A dict of settings to check against self._restart_keys.
        :returns: Bool, True if restart is needed, False otherwise.
        """
        restart_needed = False
        for setting in settings:
            if settings[setting] != self._settings[setting] and setting in self._restart_keys:
                print setting
                print settings[setting]
                print "is not the same as:"
                print self._defaults[setting]
                restart_needed = True
        return restart_needed

    def save(self, settings):
        """
        Saves incoming dict of settings to disk.

        :param settings: A dict of settings to store to disk.
        """
        for setting in settings:
            self._disk.store(setting, settings[setting])
        self._retrieve()

    def reset(self):
        """
        Restores all settings to their default values.
        """
        for setting in self._defaults:
            self._disk.store(setting, self._defaults[setting])
        self._retrieve()

    def update(self):
        """
        Sets user settings to their default value if they have None value.
        """
        for setting in self._defaults:
            if self._settings[setting] is None:
                self._disk.store(setting, self._defaults[setting])
        self._retrieve()

    def clear(self):
        """
        Sets all settings to None.
        """
        for setting in self._defaults:
            self._disk.store(setting, None)
        self._retrieve()
