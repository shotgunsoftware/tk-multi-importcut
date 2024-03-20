# Copyright (c) 2021 Autodesk, Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the ShotGrid Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the ShotGrid Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk, Inc.

from .ui.project_card import Ui_ProjectCard

from .constants import _COLORS, _STATUS_COLORS
from .card_widget import CardWidget


class ProjectCard(CardWidget):
    """
    Widget displaying a Flow Production Tracking Project
    """

    def __init__(self, parent, sg_project):
        """
        Instantiate a new ProjectCard for the given Flow Production Tracking
        Project

        :param parent: A parent QWidget
        :param sg_project: A Flow Production Tracking project, as a dictionary, to display
        """
        super(ProjectCard, self).__init__(parent, sg_project, Ui_ProjectCard)
        self.ui.title_label.setText("%s" % self.project_name)
        if self.sg_project["_display_status"]:
            self.ui.status_label.setText(
                "<font color=%s>%s</font>"
                % (
                    _STATUS_COLORS.get(self.project_status, _COLORS["lgrey"]),
                    self.sg_project["_display_status"]["name"].upper(),
                )
            )
        else:
            self.ui.status_label.setText(self.project_status)
        self.ui.details_label.setText("%s" % (self.project_description or ""))

    @property
    def sg_project(self):
        """
        Returns the PTR Project for this card

        :returns: A Flow Production Tracking Project dictionary
        """
        return self._sg_entity

    @property
    def project_name(self):
        """
        Return the name of the attached Project

        :returns: A Project name as a string
        """
        return self.entity_name

    @property
    def project_status(self):
        """
        Return the status of the attached PTR Project

        :returns: A Flow Production Tracking Status as a string
        """
        return self.sg_project.get("sg_status")

    @property
    def project_description(self):
        """
        Return the description of the attached Project

        :returns: A Project description as a string
        """
        return self.sg_project.get("sg_description")
