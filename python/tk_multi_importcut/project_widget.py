# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import tempfile

# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
from sgtk.platform.qt import QtCore, QtGui
from .downloader import DownloadRunner
from .logger import get_logger

from .ui.project_card import Ui_ProjectCard

from .constants import _COLORS, _STATUS_COLORS


class ProjectCard(QtGui.QFrame):
    """
    Widget displaying a Shotgun Project
    """
    # Emitted when cut changes for the attached Project should be displayed
    show_project = QtCore.Signal(dict)
    # Emitted when this card wants to be selected
    highlight_selected = QtCore.Signal(QtGui.QWidget)

    def __init__(self, parent, sg_project):
        """
        Instantiate a new ProjectCard for the given Shotgun Project
        :param parent: A parent QWidget
        :param sg_project: A Shotgun project, as a dictionary, to display
        """
        super(ProjectCard, self).__init__(parent)
        self._thumbnail_requested = False
        self._sg_project = sg_project
        self._logger = get_logger()

        self.ui = Ui_ProjectCard()
        self.ui.setupUi(self)
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
        self.ui.select_button.setVisible(False)
        self.ui.select_button.clicked.connect(self.show_selected)
        self.set_thumbnail(":/tk_multi_importcut/sg_%s_thumbnail.png" % (
            self._sg_project["type"].lower()
        ))

    @property
    def sg_project(self):
        return self._sg_project

    @property
    def project_name(self):
        """
        Return the name of the attached project
        """
        # Deal with name field not being consistent in SG
        return self._sg_project.get(
            "code",
            self._sg_project.get(
                "name",
                self._sg_project.get("title", "")
            )
        )

    @property
    def project_status(self):
        """
        Return the status of the attached project
        """
        # Deal with status field not being consistent in SG
        return self._sg_project.get(
            "sg_status_list",
            self._sg_project.get("sg_status")
        )

    @property
    def project_description(self):
        """
        Return the description of the attached project
        """
        # Deal with status field not being consistent in SG
        return self._sg_project.get(
            "description",
            self._sg_project.get("sg_description")
        )

    @QtCore.Slot()
    def select(self):
        """
        Set this card UI to selected mode
        """
        self.setProperty("selected", True)
        self.style().unpolish(self)
        self.style().polish(self)
        self.ui.select_button.setVisible(True)

    @QtCore.Slot()
    def unselect(self):
        """
        Set this card UI to unselected mode
        """
        self.setProperty("selected", False)
        self.style().unpolish(self)
        self.style().polish(self)
        self.ui.select_button.setVisible(False)
        self.setStyleSheet("")

    @QtCore.Slot()
    def show_selected(self):
        """
        Gently ask to show cut summary for the attached Shotgun project
        """
        self.highlight_selected.emit(self)
        self.show_project.emit(self._sg_project)
        self.ui.select_button.setVisible(False)

    @QtCore.Slot(str)
    def new_thumbnail(self, path):
        """
        Called when a new thumbnail is available for this card
        """
        self._logger.debug("Loading thumbnail %s for %s" % (path, self.project_name))
        self.set_thumbnail(path)

    def mouseDoubleClickEvent(self, event):
        """
        Handle double clicks : show cut changes for the attached project
        """
        self.show_selected()

    def mousePressEvent(self, event):
        """
        Handle single click events : select this card
        """
        self.highlight_selected.emit(self)

    def enterEvent(self, event):
        """
        Display a "chevron" button when the mouse enter the widget
        """
        self.ui.select_button.setVisible(True)

    def leaveEvent(self, event):
        """
        Hide the "chevron" button when the mouse leave the widget
        """
        self.ui.select_button.setVisible(False)

    def showEvent(self, event):
        """
        Request an async thumbnail download on first expose, if a thumbnail is
        avalaible in SG.
        """
        if self._thumbnail_requested:
            event.ignore()
            return
        self._thumbnail_requested = True
        if self._sg_project and self._sg_project["image"]:
            self._logger.debug("Requesting %s for %s" %
                               (self._sg_project["image"], self.project_name))
            _, path = tempfile.mkstemp()
            downloader = DownloadRunner(
                sg_attachment=self._sg_project["image"],
                path=path,
            )
            downloader.file_downloaded.connect(self.new_thumbnail)
            QtCore.QThreadPool.globalInstance().start(downloader)

        event.ignore()

    def set_thumbnail(self, thumb_path):
        """
        Build a pixmap from the given file path and use it as icon, resizing it to
        fit into the widget icon size

        :param thumb_path: Full path to an image to use as thumbnail
        """
        size = self.ui.icon_label.size()
        ratio = size.width() / float(size.height())
        pixmap = QtGui.QPixmap(thumb_path)
        qimage = QtGui.QImage()
        # print QtGui.QImageReader.supportedImageFormats()
        if pixmap.isNull():
            self._logger.debug("Null pixmap %s %d %d for %s" % (
                thumb_path,
                pixmap.size().width(), pixmap.size().height(),
                self.project_name))
            return
        psize = pixmap.size()
        pratio = psize.width() / float(psize.height())
        if pratio > ratio:
            self.ui.icon_label.setPixmap(
                pixmap.scaledToWidth(size.width(), mode=QtCore.Qt.SmoothTransformation)
            )
        else:
            self.ui.icon_label.setPixmap(
                pixmap.scaledToHeight(size.height(), mode=QtCore.Qt.SmoothTransformation)
            )
