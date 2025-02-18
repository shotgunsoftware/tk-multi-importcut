# Copyright (c) 2021 Autodesk, Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the ShotGrid Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the ShotGrid Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk, Inc.

from sgtk.platform.qt import QtCore, QtGui
from .logger import get_logger
from .entity_widget import EntityCard

try:
    from tank_vendor import sgutils
except ImportError:
    from tank_vendor import six as sgutils


class EntitiesView(QtCore.QObject):
    """
    Entities view page handler, shows Entity cards in a grid layout
    """

    # Emitted when an Entity is chosen for next step
    entity_chosen = QtCore.Signal(dict)
    # Emitted when a different Entity is selected
    selection_changed = QtCore.Signal(dict)

    # Emitted when the info message changed
    new_info_message = QtCore.Signal(str)

    def __init__(self, sg_entity_type, grid_layout):
        """
        Instantiate a new view for the given Entity type

        :param sg_entity_type: The PTR Entities we will show
        :param grid_layout: A grid layout
        """
        super().__init__()
        self._grid_layout = grid_layout
        self._selected_entity_card = None
        self._logger = get_logger()
        self._sg_entity_type = sg_entity_type
        # A one line message which can be displayed when the view is visible
        self._info_message = ""

    @property
    def card_count(self):
        """
        Return the number of card held by this view

        :returns: Number of cards, as an integer
        """
        return self._grid_layout.count() - 1  # We have a stretcher

    @property
    def info_message(self):
        """
        Returns the info message

        :returns: A string
        """
        return self._info_message

    @property
    def sg_entity_type(self):
        """
        Return the PTR Entity type this view is for, as a string

        :returns: A string
        """
        return self._sg_entity_type

    @property
    def selected_sg_entity(self):
        """
        Return the selected Entity, if any

        :returns: A PTR Entity dictionary or None
        """
        if self._selected_entity_card:
            return self._selected_entity_card.sg_entity
        return None

    @QtCore.Slot(dict)
    def new_sg_entity(self, sg_entity):
        """
        Called when a new Entity card widget needs to be added to the list
        of retrieved Entities

        :param sg_entity: A PTR Entity dictionary
        """
        if sg_entity["type"] != self._sg_entity_type:
            # Not for this view which only display another type of Entities
            return

        i = self.card_count

        # Remove it
        spacer = self._grid_layout.takeAt(i)
        row = i / 2
        column = i % 2
        self._logger.debug("Adding %s at %d %d %d" % (sg_entity, i, row, column))
        widget = EntityCard(None, sg_entity)
        widget.entity_type = sg_entity["type"]
        widget.highlight_selected.connect(self.entity_selected)
        widget.chosen.connect(self.entity_chosen)
        self._grid_layout.addWidget(
            widget,
            row,
            column,
        )
        self._grid_layout.setRowStretch(row, 0)
        # Put the stretcher back
        self._grid_layout.addItem(spacer, row + 1, 0, columnSpan=2)
        self._grid_layout.setRowStretch(row + 1, 1)
        count = i + 1
        self._info_message = (
            ("%d %ss" % (count, sg_entity["type"]))
            if count > 1
            else ("%d %s" % (count, sg_entity["type"]))
        )
        self.new_info_message.emit(self._info_message)

    @QtCore.Slot(QtGui.QWidget)
    def entity_selected(self, card):
        """
        Called when an Entity card is selected, ensure only one is selected at
        a time

        :param card: An Entity card
        """
        if self._selected_entity_card:
            self._selected_entity_card.unselect()
            self._logger.debug("Unselected %s" % self._selected_entity_card)
        self._selected_entity_card = card
        self._selected_entity_card.select()
        self.selection_changed.emit(card.sg_entity)
        self._logger.debug("Selected %s" % self._selected_entity_card)

    @QtCore.Slot(str)
    def search(self, u_text):
        """
        Display only Entities whose name matches the given text,
        display all of them if text is empty

        :param u_text: A unicode string to match
        """
        text = sgutils.ensure_str(u_text)
        self._logger.debug("Searching for %s" % text)
        count = self.card_count
        if not count:
            # Avoid 0 Entities message to be emitted if we don't have
            # anything ... yet
            return
        match_count = 0
        if not text:  # Show everything
            for i in range(count - 1, -1, -1):
                witem = self._grid_layout.itemAt(i)
                widget = witem.widget()
                widget.setVisible(True)
            match_count = count
        else:
            for i in range(count - 1, -1, -1):
                witem = self._grid_layout.itemAt(i)
                widget = witem.widget()
                if text.lower() in widget.entity_name.lower():
                    match_count += 1
                    widget.setVisible(True)
                else:
                    widget.setVisible(False)
        # Sort widgets so visible ones will be first, with rows
        # distribution re-arranged
        self.sort_changed()
        self._info_message = (
            ("%d Entities" % match_count) if match_count > 1 else ("%d Entity" % count)
        )
        self.new_info_message.emit(self._info_message)

    def sort_changed(self):
        """
        Called when Entities need to be sorted again
        """
        count = self.card_count
        if count < 2:  # Not a lot of things that we can do ...
            return
        # Remove the stretcher
        spacer = self._grid_layout.takeAt(count)
        # Retrieve all cut cards
        widgets = []
        for i in range(count - 1, -1, -1):
            witem = self._grid_layout.takeAt(i)
            widgets.append(witem.widget())
        widgets.sort(
            key=lambda x: (
                x.isHidden(),
                x.entity_name.lower(),
            ),
            reverse=False,
        )
        row_count = len(widgets) / 2
        # Put them back into the grid layout
        for i in range(len(widgets)):
            row = i / 2
            column = i % 2
            widget = widgets[i]
            self._grid_layout.addWidget(
                widget,
                row,
                column,
            )
            self._grid_layout.setRowStretch(row, 0)

        # Put back the stretcher
        self._grid_layout.addItem(spacer, row + 1, 0, columnSpan=2)
        self._grid_layout.setRowStretch(row + 1, 1)
        # Avoid flashes and jittering by resizing the grid widget to a size
        # suitable to hold all cards
        wsize = widgets[0].size()
        self._grid_layout.parentWidget().resize(
            self._grid_layout.parentWidget().size().width(), wsize.height() * row_count
        )

    def clear(self):
        """
        Reset the page displaying available Entities
        """
        self._selected_entity_card = None
        count = self.card_count
        for i in range(count - 1, -1, -1):
            witem = self._grid_layout.takeAt(i)
            widget = witem.widget()
            widget.close()
