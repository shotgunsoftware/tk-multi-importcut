# Copyright (c) 2015 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

from sgtk.platform.qt import QtCore, QtGui
from .logger import get_logger

from .sequence_widget import SequenceCard

from .ui.entity_type_card import Ui_entity_type_frame

class EntityTypeCard(QtGui.QFrame):
    def __init__(self, entity_type, parent=None):
        super(EntityTypeCard, self).__init__(parent)
        self.ui = Ui_entity_type_frame()
        self.ui.setupUi(self)
        self.ui.title_label.setText(entity_type)

class EntityTypesView(QtCore.QObject):
    """
    Sequences view page handler
    """
    # Emitted when a sequence is chosen for next step
    entity_type_chosen = QtCore.Signal(dict)
    # Emitted when a different sequence is selected
    selection_changed=QtCore.Signal(dict)

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
        self._entity_type_cards.append(EntityTypeCard("Project"))
        self._layout.addWidget(self._entity_type_cards[0])

    @property
    def info_message(self):
        return self._info_message
