# Copyright (c) 2021 Autodesk, Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the ShotGrid Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the ShotGrid Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk, Inc.

import tempfile
import os

# by importing QT from sgtk we ensure that
# the code will be compatible with both PySide and PyQt.
from sgtk.platform.qt import QtCore, QtGui
from tank_vendor import six
from .downloader import DownloadRunner
from .logger import get_logger


class CardWidget(QtGui.QFrame):
    """
    Base class for Card widgets, handles downloading and selection of thumbnails.

    Card widgets display a thumbnail and are used to select SG Entities.
    """

    # Emitted when this card is selected and something should be done
    # with the attached Entity
    chosen = QtCore.Signal(dict)
    # Emitted when this card wants to be selected, letting the view it is
    # displayed in handle the selection e.g. deselecting other cards
    highlight_selected = QtCore.Signal(QtGui.QWidget)
    # A Signal to discard pending download
    discard_download = QtCore.Signal()

    def __init__(self, parent, sg_entity, ui_builder, *args, **kwargs):
        """
        Instantiates a new Card Widget.

        :param parent: A parent widget
        :param sg_entity: A ShotGrid Entity dictionary
        :param ui_builder: A callable typically retrieved from Designer generated
                           Python files
        :param args: An arbitrary list of parameters
        :param kwargs: An arbitrary dictionary of parameters
        """
        super(CardWidget, self).__init__(parent, *args, **kwargs)
        self._thumbnail_requested = False
        self._sg_entity = sg_entity
        self._logger = get_logger()
        self.ui = ui_builder()
        self.ui.setupUi(self)
        self.select_button.setVisible(False)
        self.select_button.clicked.connect(self.choose_me)
        self.set_thumbnail(
            ":/tk_multi_importcut/sg_%s_thumbnail.png"
            % (self._sg_entity["type"].lower())
        )

    @property
    def entity_name(self):
        """
        Returns the name of the SG Entity attached to this card

        :returns: A string
        """
        # Deal with name field not being consistent in SG
        return self._sg_entity.get(
            "code", self._sg_entity.get("name", self._sg_entity.get("title", ""))
        )

    @property
    def sg_entity(self):
        """
        Returns the SG Entity attached to this card

        :returns: A SG Entity dictionary
        """
        return self._sg_entity

    @property
    def thumbnail_url(self):
        """
        Returns the thumbnail url for the SG Entity attached to this card

        :returns: A url string or None
        """
        if self._sg_entity and self._sg_entity.get("image"):
            return self._sg_entity["image"]
        return None

    @property
    def select_button(self):
        """
        Returns the 'chevron' button used to select this card.

        Could be overridden in deriving classes if the expected UI structure is
        not respected and the select button is named differently.

        :returns: A button widget
        """
        return self.ui.select_button

    @QtCore.Slot()
    def select(self):
        """
        Sets this card UI 'selected' property to True
        """
        self.setProperty("selected", True)
        self.style().unpolish(self)
        self.style().polish(self)
        self.select_button.setVisible(True)

    @QtCore.Slot()
    def unselect(self):
        """
        Sets this card UI 'selected' property to False
        """
        self.setProperty("selected", False)
        self.style().unpolish(self)
        self.style().polish(self)
        self.select_button.setVisible(False)
        self.setStyleSheet("")

    @QtCore.Slot()
    def choose_me(self):
        """
        Notifies listeners that this card was chosen
        """
        self.highlight_selected.emit(self)
        self.chosen.emit(self._sg_entity)
        self.select_button.setVisible(False)

    @QtCore.Slot(six.text_type)
    def new_thumbnail(self, u_path):
        """
        Called when a new thumbnail is available for this card, replace the
        current thumbnail with the new one.

        :param u_path: Full path to a thumbnail file, as a unicode string
        """
        path = six.ensure_str(u_path)
        self._logger.debug("Loading thumbnail %s for %s." % (path, self.entity_name))
        self.set_thumbnail(path)

    def mouseDoubleClickEvent(self, event):
        """
        Handles double clicks : choose this card

        :param event: A QEvent
        """
        self.choose_me()

    def mousePressEvent(self, event):
        """
        Handles single click events : select this card

        :param event: A QEvent
        """
        self.highlight_selected.emit(self)

    def enterEvent(self, event):
        """
        Displays a "chevron" button when the mouse enters the widget

        :param event: A QEvent
        """
        self.select_button.setVisible(True)

    def leaveEvent(self, event):
        """
        Hides the "chevron" button when the mouse leaves the widget

        :param event: A QEvent
        """
        self.select_button.setVisible(False)

    def showEvent(self, event):
        """
        Request an async thumbnail download on first expose, if a thumbnail is
        available in SG.

        :param event: A QEvent
        """
        if self._thumbnail_requested:
            event.ignore()
            return
        self._thumbnail_requested = True
        if self.thumbnail_url:
            self._logger.debug(
                "Requesting %s for %s" % (self.thumbnail_url, self.entity_name)
            )
            f, path = tempfile.mkstemp()
            os.close(f)
            downloader = DownloadRunner(sg_attachment=self.thumbnail_url, path=path,)
            downloader.file_downloaded.connect(self.new_thumbnail)
            self.discard_download.connect(downloader.abort)
            downloader.queue()

        event.ignore()

    def closeEvent(self, event):
        """
        Discards downloads when the widget is removed

        :param event: A QEvent
        """
        self.discard_download.emit()
        event.accept()

    def set_thumbnail(self, thumb_path):
        """
        Build a pixmap from the given file path and use it as icon, resizing it to
        fit into the widget icon size

        :param thumb_path: Full path to an image to use as thumbnail
        """
        size = self.ui.icon_label.size()
        ratio = size.width() / float(size.height())
        pixmap = QtGui.QPixmap(thumb_path)
        if pixmap.isNull():
            self._logger.debug(
                "Null pixmap %s %d %d for %s"
                % (
                    thumb_path,
                    pixmap.size().width(),
                    pixmap.size().height(),
                    self.entity_name,
                )
            )
            return
        psize = pixmap.size()
        pratio = psize.width() / float(psize.height())
        if pratio > ratio:
            self.ui.icon_label.setPixmap(
                pixmap.scaledToWidth(size.width(), mode=QtCore.Qt.SmoothTransformation)
            )
        else:
            self.ui.icon_label.setPixmap(
                pixmap.scaledToHeight(
                    size.height(), mode=QtCore.Qt.SmoothTransformation
                )
            )
