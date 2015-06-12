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
        - Add fields to CutItem entities
        """
        app = self.parent
        sg = app.shotgun
        app.log_debug("Checking needed entities and fields are available")
        sg_cut_item_entity = app.get_setting("sg_cut_item_entity")
        # Is the entity enabled ?
        schema = None
        try:
            schema = sg.schema_field_read(sg_cut_item_entity)
        except:
            pass
        if not schema:
            raise ValueError(
                "Entity %s is not enabled, please enable it or change your settings" % (
                    sg_cut_item_entity
                )
            )
        fields = {
            "sg_Cut_Order" : { "type" : "number"},
            "sg_Timecode_Cut_In" : { "type" : "text"},
            "sg_Timecode_Cut_Out" : { "type" : "text"},
            "sg_Timecode_EDL_In" : { "type" : "text"},
            "sg_Timecode_EDL_Out" : { "type" : "text"},
            "sg_Head_In" : { "type" : "number"},
            "sg_Tail_Out" : { "type" : "number"},
            "sg_Cut_In" : { "type" : "number"},
            "sg_Cut_Out" : { "type" : "number"},
            "sg_Cut_Duration" : { "type" : "number"},
            "sg_Cut" : { "type" : "entity", "properties" : { "valid_types" : ["Cut"]}},
            "sg_Link" : { "type" : "entity", "properties" : { "valid_types" : ["Shot"]}},
            "sg_Version" : { "type" : "entity", "properties" : { "valid_types" : ["Version"]}},
            "sg_FPS" : { "type" : "number", },
        }
        for field_name, field in fields.iteritems():
            if field_name.lower() not in schema:
                app.log_info("Creating field %s for entity %s" % (field_name, sg_cut_item_entity))
                # Forge a display name that should give use the sg_xxxx field name we want ...
                display_name = ' '.join( field_name.split('_')[1:]) # strip the sg_ part
                properties = field.get("properties")
                res = sg.schema_field_create(
                    sg_cut_item_entity, field["type"], display_name, properties
                )
                # Check that we got the field name we expected
                if res != field_name.lower():
                    raise RuntimeError("Wanted to create a field named %s, and created %s instead" % (
                        field_name,res)
                    )
        # Make sure shots have the reinstate status in their status list
        reinstate_status = app.get_setting("reinstate_status")
        schema = sg.schema_field_read("Shot", "sg_status_list")
        valid_values = schema["sg_status_list"]["properties"]["valid_values"]["value"]
        if reinstate_status not in valid_values:
            app.log_info("Enabling %s status for shots" % reinstate_status)
            status = sg.find_one("Status", [["code", "is", reinstate_status]])
            if not status:
                sg.create("Status", {
                    "code" : reinstate_status,
                    "name" : reinstate_status.capitalize(),
                    "icon": {"type": "Icon", "id": 1, "name": "Active"},
                    "bg_color": "202,225,202",
                    })
            valid_values.append(reinstate_status)
            properties = { "valid_values" : valid_values}
            sg.schema_field_update("Shot", "sg_status_list", properties)

        # Make sure we have a sg_status_list field on Cut
        field_name = "sg_status_list"
        schema = sg.schema_field_read("Cut")
        if field_name.lower() not in schema:
            display_name = ' '.join( field_name.split('_')[1:]) # strip the sg_ part
            statuses = ["apr", "fin", "new", "omt", "hld", "rdy",]
            existing_statuses = sg.find("Status", [["code", "in", statuses]], ["code"])
            if len(statuses) != len(existing_statuses):
                for status in statuses:
                    if status not in [ x["code"] for x in existing_statuses]:
                        app.log_info("Enabling %s status for Cuts" % status)
                        sg.create("Status", {
                            "code" : status,
                            "name" : status.capitalize(),
                            "icon": {"type": "Icon", "id": 1, "name": "Active"},
                            "bg_color": "202,225,202",
                            })
            properties = {
                "valid_values" : statuses,
                "default_value" : "new",
            }
            res = sg.schema_field_create(
                "Cut", "status_list", display_name, properties
            )
            # Check that we got the field name we expected
            if res != field_name.lower():
                raise RuntimeError("Wanted to create a field named %s, and created %s instead" % (
                    field_name, res)
                )
            sg.schema_field_update("Cut", field_name, {
                "name" : "Status",
            })

        app.log_debug("SG site correctly setup !")

#        # Add a "Deliveries" field to Version
#        field_name = app.get_setting('versions_deliveries_field')
#        if not field_name:
#            raise ValueError("Couldn't get the Version deliveries field name")
#        if not field_name.startswith("sg_"):
#            raise ValueError("Field names must start with 'sg_', got %s" % field_name)
#        # Create needed fields
#        schema = sg.schema_field_read("Version")
#        if field_name not in schema:
#            app.log_info("Creating Deliveries field for Version")
#            properties = { 'valid_types' : ['Delivery']}
#            # Forge a display name that should give use the sg_xxxx field name we want ...
#            display_name = ' '.join( field_name.split('_')[1:]) # strip the sg_ part
#            res = sg.schema_field_create("Version", "multi_entity", display_name, properties)
#            # Check that we got the field name we expected
#            if res != field_name:
#                raise RuntimeError("Wanted to create a field name %s, and created %s instead" % (field_name,res))
#            # Now give it a nice display name
#            sg.schema_field_update("Version", field_name, {'name' : 'Deliveries'})
#        else:
#            valid_types = schema[field_name]['properties']['valid_types']['value']
#            if "Delivery" not in valid_types:
#                properties = { 'valid_types' : ['Delivery']}
#                raise ValueError("'Delivery' is not accepted by field '%s', valid types are :%s" % (field_name, valid_types))
#
#        # Add a PIX id field for a couple of entities
#        field_name = app.get_setting('pix_id_field')
#        if not field_name:
#            raise ValueError("Couldn't get the Version PIX id field name")
#        if not field_name.startswith("sg_"):
#            raise ValueError("Field names must start with 'sg_', got %s" % field_name)
#
#        for entity_name in ["Version", "Playlist", "Project"]:
#            schema = sg.schema_field_read(entity_name)
#            if field_name not in schema:
#                app.log_info("Creating PIX id field for %s" % entity_name)
#                # Forge a display name that should give use the sg_xxxx field name we want ...
#                display_name = ' '.join( field_name.split('_')[1:]) # strip the sg_ part
#                res = sg.schema_field_create(entity_name, "number", display_name)
#                # Check that we got the field name we expected
#                if res != field_name:
#                    raise RuntimeError("Wanted to create a field name %s for %s, and created %s instead" % (field_name, entity_name, res))
#                # Now give it a nice display name
#                sg.schema_field_update(entity_name, field_name, {'name' : 'PIX Id'})
#            else:
#                type = schema[field_name]['data_type']['value']
#                if type != "number":
#                    raise ValueError("Field '%s' for %s has a wrong type %s, should be %s" % (field_name, entity_name, type, "number"))
#
#        # Make sure deliveries have a "PIX" type
#        schema = sg.schema_field_read("Delivery", "sg_delivery_type")
#        valid_values = schema['sg_delivery_type']['properties']['valid_values']['value']
#        if "PIX" not in valid_values:
#            app.log_info("Adding PIX delivery type")
#            valid_values.append("PIX")
#            properties = { 'valid_values' : valid_values}
#            sg.schema_field_update("Delivery", "sg_delivery_type", properties)
#
#        # Make sure deliveries have a "err" ( errored ) in their status list
#        schema = sg.schema_field_read("Delivery", "sg_status_list")
#        valid_values = schema['sg_status_list']['properties']['valid_values']['value']
#        if "err" not in valid_values:
#            app.log_info("Adding 'err' status to deliveries")
#            status = sg.find_one("Status", [['code', 'is', "err"]])
#            if not status:
#                sg.create("Status", {
#                    'code' : "err",
#                    'name' : "Errored",
#                    'icon': {'type': 'Icon', 'id': 17, 'name': 'icon_alert'},
#                    'bg_color': '248,100,2',
#                    })
#            valid_values.append("err")
#            properties = { 'valid_values' : valid_values}
#            sg.schema_field_update("Delivery", "sg_status_list", properties)
