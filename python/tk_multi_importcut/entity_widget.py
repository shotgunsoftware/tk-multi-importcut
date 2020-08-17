# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from .ui.entity_card import Ui_EntityCard
from .constants import _COLORS, _STATUS_COLORS
from .card_widget import CardWidget


class EntityCard(CardWidget):
    """
    A Card Widget displaying a general Shotgun Entity
    """

    def __init__(self, parent, sg_entity):
        """
        Instantiate a new EntityCard for the given Shotgun Entity

        :param parent: A parent QWidget
        :param sg_entity: A Shotgun entity, as a dictionary, to display
        """
        super(EntityCard, self).__init__(parent, sg_entity, Ui_EntityCard)

        self.ui.title_label.setText("%s" % self.entity_name)
        if self._sg_entity["_display_status"]:
            self.ui.status_label.setText(
                "<font color=%s>%s</font>"
                % (
                    _STATUS_COLORS.get(self.entity_status, _COLORS["lgrey"]),
                    self._sg_entity["_display_status"]["name"].upper(),
                )
            )
        else:
            self.ui.status_label.setText(self.entity_status)
        self.ui.details_label.setText("%s" % (self.entity_description or ""))

    @property
    def entity_status(self):
        """
        Return the status of the attached entity

        :returns: A Shotgun status
        """
        # Some entity types (like Project) have a non-standard status
        # field name
        return self._sg_entity.get("sg_status_list", self._sg_entity.get("sg_status"))

    @property
    def entity_description(self):
        """
        Return the description of the attached entity

        :returns: a string
        """
        # Some entity types (like Project) have a non-standard description
        # field name
        return self._sg_entity.get("description", self._sg_entity.get("sg_description"))
