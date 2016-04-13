# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk
import tempfile
import os

from sgtk.platform.qt import QtCore, QtGui
from .logger import get_logger
from .downloader import DownloadRunner
from operator import attrgetter
from .ui.entity_type_card import Ui_entity_type_frame


class EntityTypeCard(QtGui.QFrame):
    """
    A card for a given entity type
    """
    # Emitted when cuts linked to the given entity type should be displayed
    show_entities = QtCore.Signal(str)

    # Emitted when this card wants to be selected
    highlight_selected = QtCore.Signal(QtGui.QWidget)

    def __init__(self, entity_type, parent=None):
        super(EntityTypeCard, self).__init__(parent)
        self.ui = Ui_entity_type_frame()
        self.ui.setupUi(self)
        self._logger = get_logger()

        self._entity_type = entity_type
        self._entity_type_name = sgtk.util.get_entity_type_display_name(
            sgtk.platform.current_bundle().sgtk,
            self._entity_type,
        )
        self.ui.title_label.setText(self._entity_type_name)
        self.set_thumbnail(
            ":/tk_multi_importcut/sg_%s_thumbnail.png" % entity_type.lower()
        )
        if self._entity_type == "Project":
            # Retrieve the icon for current project
            app = sgtk.platform.current_bundle()
            sg_project = app.shotgun.find_one(
                "Project",
                [["id", "is", app.context.project["id"]]],
                ["image"]
            )
            if sg_project and sg_project["image"]:
                self._logger.debug("Requesting %s" % (sg_project["image"]))
            f, path = tempfile.mkstemp()
            os.close(f)
            downloader = DownloadRunner(
                sg_attachment=sg_project["image"],
                path=path,
            )
            downloader.file_downloaded.connect(self.new_thumbnail)
            QtCore.QThreadPool.globalInstance().start(downloader)

    @property
    def entity_type(self):
        return self._entity_type

    @property
    def entity_type_name(self):
        return self._entity_type_name

    @QtCore.Slot()
    def show_selected(self):
        """
        Gently ask to show cuts linked to a given entity type
        """
        self.highlight_selected.emit(self)
        self.show_entities.emit(self._entity_type)

    @QtCore.Slot()
    def select(self):
        """
        Set this card UI to selected mode
        """
        self.setProperty("selected", True)
        self.style().unpolish(self)
        self.style().polish(self)

    @QtCore.Slot()
    def unselect(self):
        """
        Set this card UI to unselected mode
        """
        self.setProperty("selected", False)
        self.style().unpolish(self)
        self.style().polish(self)

    @QtCore.Slot(str)
    def new_thumbnail(self, path):
        """
        Called when a new thumbnail is available for this card
        """
        self._logger.debug("Loading thumbnail %s for %s" % (path, self.entity_type))
        self.set_thumbnail(path, resize_to_fit=True)

    def mousePressEvent(self, event):
        """
        Handle single click events : select this card
        """
        self.highlight_selected.emit(self)

    def mouseDoubleClickEvent(self, event):
        """
        Handle double clicks : show cut changes for the attached sequence
        """
        self.show_selected()

    def set_thumbnail(self, thumb_path, resize_to_fit=False):
        """
        Build a pixmap from the given file path and use it as icon, resizingit to
        fit into the widget icon size

        :param thumb_path: Full path to an image to use as thumbnail
        :param resize_to_fit: Whether or not the pixmap should be resized to fit
        """
        size = self.ui.icon_label.size()
        ratio = size.width() / float(size.height())
        pixmap = QtGui.QPixmap(thumb_path)
        if pixmap.isNull():
            return
        if not resize_to_fit:
            # Let Qt do its thing
            self.ui.icon_label.setScaledContents(True)
            self.ui.icon_label.setPixmap(pixmap)
        else:
            # Explicit resize done by us
            self.ui.icon_label.setScaledContents(False)
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


class EntityTypesView(QtCore.QObject):
    """
    Entity types view page handler
    """
    # Emitted when a entity type is chosen for next step
    entity_type_chosen = QtCore.Signal(str)
    # Emitted when a different entity type is selected
    selection_changed = QtCore.Signal(str)

    # Emitted when the info message changed
    new_info_message = QtCore.Signal(str)

    def __init__(self, layout):
        super(EntityTypesView, self).__init__()
        self._layout = layout
        self._selected_entity_type = None
        self._entity_type_cards = []
        self._logger = get_logger()
        # A one line message which can be displayed when the view is visible
        self._info_message = ""

        # Retrieve all entity types which are accepted by Cut.sg_sequence field
        # in Shotgun
        cut_link_field = "entity"
        sg = sgtk.platform.current_bundle().shotgun
        schema = sg.schema_field_read("Cut", cut_link_field)
        entity_types = schema[cut_link_field]["properties"]["valid_types"]["value"]
        # Create all cards
        for entity_type in entity_types:
            self._entity_type_cards.append(EntityTypeCard(entity_type))
            self._entity_type_cards[-1].highlight_selected.connect(self.entity_type_selected)
            self._entity_type_cards[-1].show_entities.connect(self.entity_type_chosen)
        # And insert them sorted by their nice name
        for entity_card in sorted(self._entity_type_cards, key=attrgetter("entity_type_name")):
            self._layout.addWidget(entity_card)

    @property
    def info_message(self):
        return self._info_message

    @QtCore.Slot(QtGui.QWidget)
    def entity_type_selected(self, card):
        """
        Called when a entity type card is selected, ensure only one is selected at
        a time
        """
        if self._selected_entity_type:
            self._selected_entity_type.unselect()
            self._logger.debug("Unselected %s" % self._selected_entity_type)
        self._selected_entity_type = card
        self._selected_entity_type.select()
        self.selection_changed.emit(card.entity_type)
        self._logger.debug("Selected %s" % self._selected_entity_type)

    def count(self):
        """
        Return the number of entity types which can be used
        """
        return len(self._entity_type_cards)

    def select_and_skip(self):
        """
        If there is a single entry automatically select it and return True if
        the app can go to next step.
        :returns: True if this screen can be skipped, False otherwise
        """
        if len(self._entity_type_cards) == 1:
            self.entity_type_selected(self._entity_type_cards[0])
            self.entity_type_chosen.emit(self._entity_type_cards[0].entity_type)
            return True
        return False
