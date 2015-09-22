# Copyright (c) 2015 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk
from sgtk.platform.qt import QtCore, QtGui
from .logger import get_logger

from .sequence_widget import SequenceCard

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
        self._entity_type = entity_type
        self.ui.title_label.setText(entity_type)
        self.set_thumbnail(
            ":/tk_multi_importcut/sg_%s_thumbnail.png" % entity_type.lower()
        )
    @property
    def entity_type(self):
        return self._entity_type
    
    def _set_icon(self):
        """
        Set the icon for the card based on the entity type
        """
        
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
            # Fall back to default sequence icon
            pixmap = QtGui.QPixmap(":/tk_multi_importcut/sg_sequence_thumbnail.png")
        self.ui.icon_label.setPixmap(pixmap)
#        psize = pixmap.size()
#        pratio = psize.width() / float(psize.height())
#        if pratio > ratio:
#            self.ui.icon_label.setPixmap(
#                pixmap.scaledToWidth(size.width(), mode=QtCore.Qt.SmoothTransformation)
#            )
#        else:
#            self.ui.icon_label.setPixmap(
#                pixmap.scaledToHeight(size.height(), mode=QtCore.Qt.SmoothTransformation)
#            )

class EntityTypesView(QtCore.QObject):
    """
    Entity types view page handler
    """
    # Emitted when a entity type is chosen for next step
    entity_type_chosen = QtCore.Signal(str)
    # Emitted when a different entity type is selected
    selection_changed=QtCore.Signal(str)

    # Emitted when the info message changed
    new_info_message=QtCore.Signal(str)

    def __init__(self, layout):
        super(EntityTypesView, self).__init__()
        self._layout = layout
        self._selected_entity_type = None
        self._entity_type_cards = []
        self._logger = get_logger()
         # A one line message which can be displayed when the view is visible
        self._info_message=""
        
        # Always add Project to supported entity types
        self._entity_type_cards.append(EntityTypeCard("Project"))
        self._layout.addWidget(self._entity_type_cards[0])
        self._entity_type_cards[-1].highlight_selected.connect(self.entity_type_selected)
        self._entity_type_cards[-1].show_entities.connect(self.entity_type_chosen)

        # Retrieve all entity types which are accepted by Cut.sg_sequence field
        # in Shotgun
        cut_link_field = sgtk.platform.current_bundle().get_setting("cut_link_field")
        sg = sgtk.platform.current_bundle().shotgun
        schema = sg.schema_field_read("Cut", cut_link_field)
        entity_types = schema[cut_link_field]["properties"]["valid_types"]["value"]
        for entity_type in entity_types:
            # Don't add Project twice
            if entity_type != "Project":
                self._entity_type_cards.append(EntityTypeCard(entity_type))
                self._layout.addWidget(self._entity_type_cards[-1])
                self._entity_type_cards[-1].highlight_selected.connect(self.entity_type_selected)
                self._entity_type_cards[-1].show_entities.connect(self.entity_type_chosen)

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

