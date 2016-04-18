# Copyright (c) 2016 Shotgun Software Inc.
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
from .entity_widget import EntityCard


class EntitiesView(QtCore.QObject):
    """
    Entities view page handler
    """
    # Emitted when a sequence is chosen for next step
    sequence_chosen = QtCore.Signal(dict)
    # Emitted when a different sequence is selected
    selection_changed = QtCore.Signal(dict)

    # Emitted when the info message changed
    new_info_message = QtCore.Signal(str)

    def __init__(self, grid_widget):
        super(EntitiesView, self).__init__()
        self._grid_widget = grid_widget
        self._selected_entity_card = None
        self._logger = get_logger()
        # A one line message which can be displayed when the view is visible
        self._info_message = ""
        self._entities_display_mode = None

    @property
    def info_message(self):
        return self._info_message

    @QtCore.Slot(dict)
    def new_sg_entity(self, sg_entity):
        """
        Called when a new entity card widget needs to be added to the list
        of retrieved entities
        """
        if sg_entity.get("mode_change"):
            self._entities_display_mode = sg_entity["mode_change"]
            self._display_for_mode()
            return

        i = self._grid_widget.count() - 1  # We have a stretcher

        # Remove it
        spacer = self._grid_widget.takeAt(i)
        row = i / 2
        column = i % 2
        self._logger.debug("Adding %s at %d %d %d" % (sg_entity, i, row, column))
        widget = EntityCard(None, sg_entity)
        widget.entity_type = sg_entity["type"]
        widget.highlight_selected.connect(self.entity_selected)
        widget.show_sequence.connect(self.sequence_chosen)
        self._grid_widget.addWidget(widget, row, column, )
        self._grid_widget.setRowStretch(row, 0)
        # Put the stretcher back
        self._grid_widget.addItem(spacer, row + 1, 0, colSpan=2)
        self._grid_widget.setRowStretch(row + 1, 1)
        count = i + 1
        self._info_message = ("%d %ss" % (count, sg_entity["type"])) if count > 1 else (
            "%d %s" % (count, sg_entity["type"]))
        self.new_info_message.emit(self._info_message)
        self._entities_display_mode = sg_entity["type"]
        self._display_for_mode()

    @QtCore.Slot(QtGui.QWidget)
    def entity_selected(self, card):
        """
        Called when an entity card is selected, ensure only one is selected at
        a time
        """
        if self._selected_entity_card:
            self._selected_entity_card.unselect()
            self._logger.debug("Unselected %s" % self._selected_entity_card)
        self._selected_entity_card = card
        self._selected_entity_card.select()
        self.selection_changed.emit(card.sg_entity)
        self._logger.debug("Selected %s" % self._selected_entity_card)

    @QtCore.Slot(unicode)
    def search(self, text):
        """
        Display only sequences whose name matches the given text,
        display all of them if text is empty

        :param text: A string to match
        """
        self._logger.debug("Searching for %s" % text)
        count = self._grid_widget.count() - 1  # We have stretcher
        if not count:
            # Avoid 0 sequences message to be emitted if we don't have
            # anything ... yet
            return
        match_count = 0
        if not text:  # Show everything
            for i in range(count-1, -1, -1):
                witem = self._grid_widget.itemAt(i)
                widget = witem.widget()
                if widget.entity_type == self._entities_display_mode:
                    widget.setVisible(True)
            match_count = count
        else:
            for i in range(count-1, -1, -1):
                witem = self._grid_widget.itemAt(i)
                widget = witem.widget()
                if widget.entity_type == self._entities_display_mode:
                    if text.lower() in widget.entity_name.lower():
                        match_count += 1
                        widget.setVisible(True)
                    else:
                        widget.setVisible(False)
        # Sort widgets so visible ones will be first, with rows
        # distribution re-arranged
        self.sort_changed()
        self._info_message = ("%d Entities" % match_count) if match_count > 1 else (
            "%d Entity" % count)
        self.new_info_message.emit(self._info_message)

    def sort_changed(self):
        """
        Called when sequences need to be sorted again
        """
        method = 0
        count = self._grid_widget.count() - 1  # We have stretcher
        if count < 2:  # Not a lot of things that we can do ...
            return
        # Remove the stretcher
        spacer = self._grid_widget.takeAt(count)
        # Retrieve all cut cards
        widgets = []
        for i in range(count-1, -1, -1):
            witem = self._grid_widget.itemAt(i).widget()
            if hasattr(witem, "entity_type"):
                if witem.entity_type == self._entities_display_mode:
                    witem = self._grid_widget.takeAt(i)
                    widgets.append(witem.widget())
        field = "code"
        widgets.sort(
            key=lambda x: (
                x.isHidden(),
                x.entity_name.lower(),
            ), reverse=False
        )
        row_count = len(widgets) / 2
        # Put them back into the grid layout
        for i in range(len(widgets)):
            row = i / 2
            column = i % 2
            widget = widgets[i]
            self._grid_widget.addWidget(widget, row, column, )
            self._grid_widget.setRowStretch(row, 0)

        # Put back the stretcher
        self._grid_widget.addItem(spacer, row+1, 0, colSpan=2)
        self._grid_widget.setRowStretch(row+1, 1)
        # Avoid flashes and jittering by resizing the grid widget to a size
        # suitable to hold all cards
        wsize = widgets[0].size()
        self._grid_widget.parentWidget().resize(
            self._grid_widget.parentWidget().size().width(),
            wsize.height() * row_count)

    def _display_for_mode(self):
        """
        Hide / show CutDiff widgets depending on the current mode
        """
        count = self._grid_widget.count() - 1  # We have stretcher
        for i in range(0, count):
            widget = self._grid_widget.itemAt(i).widget()
            if hasattr(widget, "entity_type"):
                if widget.entity_type == self._entities_display_mode:
                    widget.setVisible(True)
                else:
                    widget.setVisible(False)
        self.sort_changed()

    def clear(self):
        """
        Reset the page displaying available sequences
        """
        self._selected_entity_card = None
        count = self._grid_widget.count() - 1  # We have stretcher
        for i in range(count-1, -1, -1):
            witem = self._grid_widget.takeAt(i)
            widget = witem.widget()
            widget.close()
        # print self._grid_widget.count()
