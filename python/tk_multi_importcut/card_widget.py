# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import tempfile
import os
# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
from sgtk.platform.qt import QtCore, QtGui
from .downloader import DownloadRunner
from .logger import get_logger

class CardWidget(QtGui.QFrame):
    """
    Base class for Card widgets, dealing with thumbnail downloads and
    selection.

    Card widgets allow to select SG entities and display a thumbnail.
    """
    # Emitted when this card is selected and something should be done
    # with the entity it is holding
    chosen = QtCore.Signal(dict)
    # Emitted when this card wants to be selected
    highlight_selected = QtCore.Signal(QtGui.QWidget)
    # A Signal to discard pending download
    discard_download = QtCore.Signal()

    def __init__(self, parent, sg_entity, ui_builder, *args, **kargs):
        """
        Instantiate a new Card Widget

        :param parent: A parent widget
        :param sg_entity: A Shotgun Entity dictionary
        :param ui_builder: A callable typically retrieved from Designer generated
                           Python files
        :param args: Arbitrary list of parameters
        :param kargs: Arbitrary dictionary of parameters
        """
        super(CardWidget, self).__init__(parent, *args, **kargs)
        self._thumbnail_requested = False
        self._sg_entity = sg_entity
        self._logger = get_logger()
        self.ui = ui_builder()
        self.ui.setupUi(self)
        self.select_button.setVisible(False)
        self.select_button.clicked.connect(self.choose_me)
        self.set_thumbnail(":/tk_multi_importcut/sg_%s_thumbnail.png" % (
            self._sg_entity["type"].lower()
        ))

    @property
    def entity_name(self):
        """
        Return the name of the SG entity attached to this card

        :returns: A string
        """
        # Deal with name field not being consistent in SG
        return self._sg_entity.get(
            "code",
            self._sg_entity.get(
                "name",
                self._sg_entity.get("title", "")
            )
        )

    @property
    def sg_entity(self):
        """
        Returns the SG entity attached to this card

        :returns: A SG entity dictionary
        """
        return self._sg_entity

    @property
    def thumbnail_url(self):
        """
        Returns the thumbnail url for the SG entity attached to this card

        :returns: A url or None
        """
        if self._sg_entity and self._sg_entity.get("image"):
            return self._sg_entity["image"]
        return None

    @property
    def select_button(self):
        """
        Return the chevron button used to select this card.

        Could be overidden in deriving classes if the expected UI structure is
        not followed and the select button was named differently.

        :returns: A button widget
        """
        return self.ui.select_button

    @QtCore.Slot()
    def select(self):
        """
        Set this card UI to selected mode
        """
        self.setProperty("selected", True)
        self.style().unpolish(self)
        self.style().polish(self)
        self.select_button.setVisible(True)

    @QtCore.Slot()
    def unselect(self):
        """
        Set this card UI to unselected mode
        """
        self.setProperty("selected", False)
        self.style().unpolish(self)
        self.style().polish(self)
        self.select_button.setVisible(False)
        self.setStyleSheet("")

    @QtCore.Slot()
    def choose_me(self):
        """
        Notify listeners that this card was chosen
        """
        self.highlight_selected.emit(self)
        self.chosen.emit(self._sg_entity)
        self.select_button.setVisible(False)

    @QtCore.Slot(str)
    def new_thumbnail(self, path):
        """
        Called when a new thumbnail is available for this card

        :param path: Full path to a thumbnail file
        """
        self._logger.debug("Loading thumbnail %s for %s" % (path, self.entity_name))
        self.set_thumbnail(path)

    def mouseDoubleClickEvent(self, event):
        """
        Handle double clicks : choose this card

        :param event: A QEvent
        """
        self.choose_me()

    def mousePressEvent(self, event):
        """
        Handle single click events : select this card

        :param event: A QEvent
        """
        self.highlight_selected.emit(self)

    def enterEvent(self, event):
        """
        Display a "chevron" button when the mouse enter the widget

        :param event: A QEvent
        """
        self.select_button.setVisible(True)

    def leaveEvent(self, event):
        """
        Hide the "chevron" button when the mouse leave the widget

        :param event: A QEvent
        """
        self.select_button.setVisible(False)

    def showEvent(self, event):
        """
        Request an async thumbnail download on first expose, if a thumbnail is
        avalaible in SG.

        :param event: A QEvent
        """
        if self._thumbnail_requested:
            event.ignore()
            return
        self._thumbnail_requested = True
        if self.thumbnail_url:
            self._logger.debug("Requesting %s for %s" %
                               (self.thumbnail_url, self.entity_name))
            f, path = tempfile.mkstemp()
            os.close(f)
            downloader = DownloadRunner(
                sg_attachment=self.thumbnail_url,
                path=path,
            )
            downloader.file_downloaded.connect(self.new_thumbnail)
            self.discard_download.connect(downloader.abort)
            downloader.queue()

        event.ignore()

    def closeEvent(self, evt):
        """
        Discard downloads when the widget is removed
        """
        self.discard_download.emit()
        evt.accept()

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
        if pixmap.isNull():
            self._logger.debug("Null pixmap %s %d %d for %s" % (
                thumb_path,
                pixmap.size().width(), pixmap.size().height(),
                self.entity_name))
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

