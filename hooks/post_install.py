# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import sys
import os

from tank import Hook

class PostInstall(Hook):
    
    def execute(self, **kwargs):
        """
        Main entry point for the hook
        """
        # Commented out for the time being
        # as when run in actual post install
        # there is no active app, so settings can't be
        # retrieved
        # self.ensure_sg_setup()
        pass

    def ensure_sg_setup(self):
        """
        Make sure that we have on the SG server what we need
        If needed :
        - Advise user to enable the CutItem entity if inactive
        """
        app = self.parent
        sg = app.shotgun
        app.log_debug("Checking if required entities are available...")
        sg_cut_item_entity = app.get_setting("sg_cut_item_entity")
        schema = None
        try:
            app.log_debug("Checking %s..." % sg_cut_item_entity)
            schema = sg.schema_field_read(sg_cut_item_entity)
        except:
            pass
        if not schema:
            raise ValueError(
                "Entity %s is not enabled, please enable it or change your settings." % (
                    sg_cut_item_entity
                )
            )

