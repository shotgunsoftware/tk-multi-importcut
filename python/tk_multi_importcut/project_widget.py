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
from sgtk.platform.qt import QtCore, QtGui

from .ui.project_card import Ui_ProjectCard

from .constants import _COLORS, _STATUS_COLORS
from .card_widget import CardWidget

class ProjectCard(CardWidget):
    """
    Widget displaying a Shotgun Project
    """
    # Emitted when cut changes for the attached Project should be displayed
    show_project = QtCore.Signal(dict)
    # Emitted when this card wants to be selected
    highlight_selected = QtCore.Signal(QtGui.QWidget)
    # A Signal to discard pending download
    discard_download = QtCore.Signal()

    def __init__(self, parent, sg_project):
        """
        Instantiate a new ProjectCard for the given Shotgun Project
        :param parent: A parent QWidget
        :param sg_project: A Shotgun project, as a dictionary, to display
        """
        super(ProjectCard, self).__init__(parent, sg_project, Ui_ProjectCard)
        self.ui.title_label.setText("%s" % self.project_name)
        # if self._sg_project["_display_status"]:
        #     self.ui.status_label.setText(
        #         "<font color=%s>%s</font>" % (
        #             _STATUS_COLORS.get(self.project_status, _COLORS["lgrey"]),
        #             self._sg_project["_display_status"]["name"].upper(),
        #         )
        #     )
        # else:
        #     self.ui.status_label.setText(self.project_status)
        self.ui.details_label.setText("%s" % (self.project_description or ""))
        self.chosen.connect(self.show_project)

    @property
    def sg_project(self):
        """
        Returns the SG project for this card

        :returns: A Shotgun Project dictionary
        """
        return self._sg_entity

    @property
    def project_name(self):
        """
        Return the name of the attached project

        :returns: A string
        """
        return self.entity_name

    @property
    def project_status(self):
        """
        Return the status of the attached project
        :returns: A Shotgun Status
        """
        # Deal with status field not being consistent in SG
        return self.sg_project.get(
            "sg_status_list",
            self.sg_project.get("sg_status")
        )

    @property
    def project_description(self):
        """
        Return the description of the attached project
        """
        # Deal with status field not being consistent in SG
        return self.sg_project.get("sg_description")



