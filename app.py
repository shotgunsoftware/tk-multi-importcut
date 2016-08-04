# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from sgtk.platform import Application


class ImportCutApp(Application):
    """
    The app entry point. This class is responsible for intializing and tearing down
    the application, handling menu registration, etc.
    """

    def init_app(self):
        """
        Called as the application is being initialized
        """

        # first, we use the special import_module command to access the app module
        # that resides inside the python folder in the app. This is where the actual UI
        # and business logic of the app is kept. By using the import_module command,
        # Toolkit's code reload mechanism will work properly.
        app_payload = self.import_module("tk_multi_importcut")

        # now register a *command*, which is normally a menu entry of some kind on a Shotgun
        # menu (but it depends on the engine). The engine will manage this command and
        # whenever the user requests the command, it will call out to the callback.

        # first, set up our callback, calling out to a method inside the app module contained
        # in the python folder of the app
        menu_callback = lambda: app_payload.dialog.show_dialog(self)

        # now register the command with the engine
        display_name = self.get_setting("display_name") or "Import Cut"
        short_name = display_name.lower().replace(" ", "_")
        settings = {
            "icon": self.icon_256,
            "short_name": short_name}

        self.engine.register_command(
            display_name,
            menu_callback,
            settings)

        if self.engine.name == "tk-shell":
            settings = {
                "icon": self.icon_256,
                "short_name": "%s_with_args" % short_name}

            self.engine.register_command(
                "%s_with_args" % display_name,
                self.load_edl_for_entity,
                settings)

    def load_edl_for_entity(self, edl_file_path, sg_entity, frame_rate):
        """
        Allow import cut to run with pre-selected EDL file path and SG
        entity, and to change the frame rate for the EDL file

        :param edl_file_path: Full path to an EDL file
        :param sg_entity: An SG entity dictionary as a string, e.g.
                          '{"code" : "001", "id" : 19, "type" : "Sequence"}'
        :param frame_rate: The frame rate for the EDL file
        """
        app_payload = self.import_module("tk_multi_importcut")
        app_payload.dialog.load_edl_for_entity(self, edl_file_path, sg_entity, frame_rate)
