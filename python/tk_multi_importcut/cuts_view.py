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

from .cut_widget import CutCard

_SORT_METHODS = ["Sort by Date", "Sort by Name", "Sort by Status"]

class CutsView(QtCore.QObject):
    """
    Cuts view page handler
    """
    # Emitted when the cut summary for a cut should be shown
    show_cut_diff = QtCore.Signal(dict)

    # Emitted when a different cut is selected
    selection_changed=QtCore.Signal(dict)

    # Emitted when the info message changed
    new_info_message=QtCore.Signal(str)

    def __init__(self, grid_widget, sort_menu_button):
        super(CutsView, self).__init__()
        self._grid_widget = grid_widget
        self._sort_menu_button = sort_menu_button
        self._selected_card_cut = None
        self._action_group = None
        self._logger = get_logger()
        self.build_cuts_sort_menu()
         # A one line message which can be displayed when the view is visible
        self._info_message=""

    @property
    def info_message(self):
        return self._info_message

    @QtCore.Slot(dict)
    def new_sg_cut(self, sg_entity):
        """
        Called when a new cut card widget needs to be added to the list
        of retrieved cuts
        """
        i = self._grid_widget.count() -1 # We have a stretcher
        # Remove it
        spacer = self._grid_widget.takeAt(i)
        row = i / 2
        column = i % 2
        self._logger.debug("Adding %s at %d %d %d" % ( sg_entity, i, row, column))
        widget = CutCard(None, sg_entity)
        widget.highlight_selected.connect(self.cut_selected)
        widget.show_cut.connect(self.show_cut)
        self._grid_widget.addWidget(widget, row, column, )
        self._grid_widget.setRowStretch(row, 0)
        self._grid_widget.addItem(spacer, row+1, 0, colSpan=2 )
        self._grid_widget.setRowStretch(row+1, 1)
        self._info_message="%d Cuts" % (i+1)
        self.new_info_message.emit(self._info_message)

    @QtCore.Slot(unicode)
    def search(self, text):
        """
        Display only cuts whose name matches the given text,
        display all of them if text is empty

        :param text: A string to match
        """
        self._logger.debug("Searching for %s" % text)
        count = self._grid_widget.count() -1 # We have stretcher
        match_count=0
        if not count:
            return
        if not text:
            # Show everything
            for i in range(count-1, -1, -1):
                witem = self._grid_widget.itemAt(i)
                widget = witem.widget()
                widget.setVisible(True)
            match_count=count
        else:
            for i in range(count-1, -1, -1):
                witem = self._grid_widget.itemAt(i)
                widget = witem.widget()
                # Case insentitive match
                if text.lower() in widget._sg_cut["code"].lower():
                    widget.setVisible(True)
                    match_count += 1
                else:
                    widget.setVisible(False)
        # Sort widgets so visible ones will be first, with rows
        # distribution re-arranged
        self.sort_changed(self._action_group.checkedAction())
        self._info_message="%d Cuts" % match_count
        self.new_info_message.emit(self._info_message)

    @QtCore.Slot(QtGui.QWidget)
    def cut_selected(self, card):
        """
        Called when a cut card is selected, ensure only one is selected at
        a time

        :param card: The CutCard widget to select
        """
        if self._selected_card_cut:
            self._selected_card_cut.unselect()
            self._logger.debug("Unselected %s" % self._selected_card_cut)
        self._selected_card_cut = card
        self._selected_card_cut.select()
        self.selection_changed.emit(card.sg_entity)
        self._logger.debug("Selected %s" % self._selected_card_cut)

    @QtCore.Slot(dict)
    def show_cut(self, sg_cut):
        """
        Called when cut changes needs to be shown for a particular sequence/cut

        :param sg_cut: A Shotgun cut dictionary, as retrieved from a find
        """
        self._logger.info("%s selected for cut summary" % sg_cut["code"] )
        self.show_cut_diff.emit(sg_cut)

    @QtCore.Slot(QtGui.QAction)
    def sort_changed(self, action):
        """
        Called when sorting method is changed

        :param action: The QAction to activate
        """
        method = action.data()
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
        # Sort them by prepending a primary field to our usual sort
        # order
        field = ["created_at", "code", "sg_status_list"][method]
        widgets.sort(
            key=lambda x: (
                x.isVisible(),
                x._sg_cut[field],
                x._sg_cut["created_at"],
                x._sg_cut["code"],
                x._sg_cut["sg_status_list"],
            ), reverse=True
        )
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
        # And update the menu label
        self._sort_menu_button.setText(action.text())

    def build_cuts_sort_menu(self):
        """
        Build the popup menu with different sort methods
        Attach it to the given button
        """
        self._cuts_sort_menu = QtGui.QMenu()
        self._sort_menu_button.setMenu(self._cuts_sort_menu)
        self._action_group =  QtGui.QActionGroup(self)
        self._action_group.triggered.connect(self.sort_changed)
        for s in _SORT_METHODS:
            sort_action = QtGui.QAction(
                s,
                self._action_group,
            )
            sort_action.setCheckable(True)
            sort_action.setData(_SORT_METHODS.index(s))
            self._cuts_sort_menu.addAction(sort_action)
        action = self._action_group.actions()[0]
        action.setChecked(True)
        self._sort_menu_button.setText(action.text())

    def clear(self):
        """
        Reset the page displaying available cuts
        """
        self._selected_card_cut = None
        count = self._grid_widget.count() -1 # We have stretcher
        for i in range(count-1, -1, -1):
            witem = self._grid_widget.takeAt(i)
            widget = witem.widget()
            widget.close()
        action = self._action_group.actions()[0]
        action.setChecked(True)
        self._sort_menu_button.setText(action.text())


