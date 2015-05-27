# Copyright (c) 2014 Shotgun Software Inc.
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

class SequencesView(QtCore.QObject):
    """
    Sequences view page handler
    """
    # Emitted when a sequence is chosen for next step
    sequence_chosen = QtCore.Signal(dict)
    # Emitted when a different sequence is selected
    selection_changed=QtCore.Signal(dict)

    def __init__(self, grid_widget):
        super(SequencesView, self).__init__()
        self._grid_widget = grid_widget
        self._selected_card_sequence = None
        self._logger = get_logger()

    @QtCore.Slot(dict)
    def new_sg_sequence(self, sg_entity):
        """
        Called when a new sequence card widget needs to be added to the list
        of retrieved sequences
        """
        i = self._grid_widget.count() -1 # We have a stretcher
        # Remove it
        spacer = self._grid_widget.takeAt(i)
        row = i / 2
        column = i % 2
        self._logger.debug("Adding %s at %d %d %d" % ( sg_entity, i, row, column))
        widget = SequenceCard(None, sg_entity)
        widget.highlight_selected.connect(self.sequence_selected)
        widget.show_sequence.connect(self.sequence_chosen)
        self._grid_widget.addWidget(widget, row, column, )
        self._grid_widget.setRowStretch(row, 0)
        # Put the stretcher back
        self._grid_widget.addItem(spacer, row+1, 0, colSpan=2 )
        self._grid_widget.setRowStretch(row+1, 1)

    @QtCore.Slot(QtGui.QWidget)
    def sequence_selected(self, card):
        """
        Called when a sequence card is selected, ensure only one is selected at
        a time
        """
        if self._selected_card_sequence:
            self._selected_card_sequence.unselect()
            self._logger.debug("Unselected %s" % self._selected_card_sequence)
        self._selected_card_sequence = card
        self._selected_card_sequence.select()
        self.selection_changed.emit(card.sg_entity)
        self._logger.debug("Selected %s" % self._selected_card_sequence)

    @QtCore.Slot(unicode)
    def search(self, text):
        """
        Display only sequences whose name matches the given text,
        display all of them if text is empty

        :param text: A string to match
        """
        self._logger.debug("Searching for %s" % text)
        count = self._grid_widget.count() -1 # We have stretcher
        for i in range(count-1, -1, -1):
            witem = self._grid_widget.itemAt(i)
            widget = witem.widget()
            if text:
                widget.setVisible(text in widget._sg_sequence["code"])
            else:
                widget.setVisible(True)
        # Sort widgets so visible ones will be first, with rows
        # distribution re-arranged
        self.sort_changed()

    def sort_changed(self):
        """
        Called when sequences need to be sorted again
        """
        method = 0
        count = self._grid_widget.count() -1 # We have stretcher
        if count < 2: # Not a lot of things that we can do ...
            return
        # Remove the stretcher
        spacer = self._grid_widget.takeAt(count)
        # Retrieve all cut cards
        widgets = []
        for i in range(count-1, -1, -1):
            witem = self._grid_widget.takeAt(i)
            widgets.append(witem.widget())
        field = "code"
        widgets.sort(
            key=lambda x: (
                x.isHidden(),
                x._sg_sequence[field],
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
        self._grid_widget.addItem(spacer, row+1, 0, colSpan=2 )
        self._grid_widget.setRowStretch(row+1, 1)
        # Avoid flashes and jittering by resizing the grid widget to a size
        # suitable to hold all cards
        wsize = widgets[0].size()
        self._grid_widget.parentWidget().resize(
            self._grid_widget.parentWidget().size().width(),
            wsize.height()* row_count)


    def clear(self):
        """
        Reset the page displaying available sequences
        """
        self._selected_card_sequence = None
        count = self._grid_widget.count() -1 # We have stretcher
        for i in range(count-1, -1, -1):
            witem = self._grid_widget.takeAt(i)
            widget = witem.widget()
            widget.close()
        # print self._grid_widget.count()

