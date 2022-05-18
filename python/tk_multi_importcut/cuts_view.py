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
from tank_vendor import six
from .logger import get_logger

from .cut_widget import CutCard

_SORT_METHODS = ["Sort by Date", "Sort by Name", "Sort by Status"]


class CutsView(QtCore.QObject):
    """
    A view which shows CutCards arranged in a gird layout
    """

    # Emitted when the cut summary for a cut should be shown
    cut_chosen = QtCore.Signal(dict)

    # Emitted when a different cut is selected
    selection_changed = QtCore.Signal(dict)

    # Emitted when the info message changed
    new_info_message = QtCore.Signal(str)

    def __init__(self, grid_layout, sort_menu_button):
        """
        Instantiate a new Cuts view

        :param grid_layout: A QGridLayout used to arrange all CutCards
        :param sort_menu_button: A QPushButton, QActions are added to it
        """
        super(CutsView, self).__init__()
        self._grid_layout = grid_layout
        self._sort_menu_button = sort_menu_button
        self._selected_card_cut = None
        self._action_group = None
        self._logger = get_logger()
        self.build_cuts_sort_menu()
        # A one line message which can be displayed when the view is visible
        self._info_message = ""

    @property
    def info_message(self):
        """
        Returns the info message for this view

        :returns: A the info message as a string
        """
        return self._info_message

    @property
    def card_count(self):
        """
        Return the number of cards currently held by this view
        """
        return self._grid_layout.count() - 1  # We have a stretcher

    @QtCore.Slot(dict)
    def new_sg_cut(self, sg_entity):
        """
        Called when a new cut card widget needs to be added to the list
        of retrieved cuts

        :param sg_entity: A SG Cut dictionary
        """
        i = self.card_count
        # Remove it
        spacer = self._grid_layout.takeAt(i)
        row = i / 2
        column = i % 2
        self._logger.debug("Adding %s at %d %d %d" % (sg_entity, i, row, column))
        widget = CutCard(None, sg_entity)
        widget.highlight_selected.connect(self.cut_selected)
        widget.chosen.connect(self.show_cut)
        self._grid_layout.addWidget(
            widget,
            row,
            column,
        )
        self._grid_layout.setRowStretch(row, 0)
        self._grid_layout.addItem(spacer, row + 1, 0, colSpan=2)
        self._grid_layout.setRowStretch(row + 1, 1)
        self._info_message = (
            ("%d Cuts" % (i + 1)) if (i + 1) > 1 else ("%d Cut" % (i + 1))
        )
        self.new_info_message.emit(self._info_message)

    @QtCore.Slot(six.text_type)
    def search(self, u_text):
        """
        Display only Cuts whose name matches the given text.

        Display all of them if text is empty.

        :param u_text: A unicode string to match
        """
        text = six.ensure_str(u_text)
        self._logger.debug("Searching for %s" % text)
        count = self.card_count
        match_count = 0
        if not count:
            return
        if not text:
            # Show everything
            for i in range(count - 1, -1, -1):
                witem = self._grid_layout.itemAt(i)
                widget = witem.widget()
                widget.setVisible(True)
            match_count = count
        else:
            for i in range(count - 1, -1, -1):
                witem = self._grid_layout.itemAt(i)
                widget = witem.widget()
                # Case insensitive match
                if text.lower() in widget.sg_cut["code"].lower():
                    widget.setVisible(True)
                    match_count += 1
                else:
                    widget.setVisible(False)
        # Sort widgets so visible ones will be first, with rows
        # distribution re-arranged
        self.sort_changed(self._action_group.checkedAction())
        self._info_message = (
            ("%d Cuts" % match_count) if match_count > 1 else ("%d Cut" % count)
        )
        self.new_info_message.emit(self._info_message)

    @QtCore.Slot(QtGui.QWidget)
    def cut_selected(self, card):
        """
        Called when a cut card is selected.

        Ensure only one is selected at a time.

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
        Called when cut changes needs to be shown for a particular Cut

        :param sg_cut: A ShotGrid Cut dictionary, as retrieved from a find
        """
        self._logger.info("%s selected for cut summary" % sg_cut["code"])
        self.cut_chosen.emit(sg_cut)

    @QtCore.Slot(QtGui.QAction)
    def sort_changed(self, action):
        """
        Called when sorting method is changed

        :param action: The QAction to activate
        """
        method = action.data()
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
        # Sort them by prepending a primary field to our usual sort
        # order
        field = ["created_at", "code", "sg_status_list"][method]
        widgets.sort(
            key=lambda x: (
                x.isVisible(),
                x.sg_cut[field],
                x.sg_cut["created_at"],
                x.sg_cut["code"],
                x.sg_cut["sg_status_list"],
            ),
            reverse=True,
        )
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
        self._grid_layout.addItem(spacer, row + 1, 0, colSpan=2)
        self._grid_layout.setRowStretch(row + 1, 1)
        # And update the menu label
        self._sort_menu_button.setText(action.text())

    def build_cuts_sort_menu(self):
        """
        Build the popup menu with different sort methods
        Attach it to the given button
        """
        self._cuts_sort_menu = QtGui.QMenu()
        self._sort_menu_button.setMenu(self._cuts_sort_menu)
        self._action_group = QtGui.QActionGroup(self)
        self._action_group.triggered.connect(self.sort_changed)
        for smeth in _SORT_METHODS:
            sort_action = QtGui.QAction(
                smeth,
                self._action_group,
            )
            sort_action.setCheckable(True)
            sort_action.setData(_SORT_METHODS.index(smeth))
            self._cuts_sort_menu.addAction(sort_action)
        action = self._action_group.actions()[0]
        action.setChecked(True)
        self._sort_menu_button.setText(action.text())

    def clear(self):
        """
        Reset the page displaying available cuts
        """
        self._selected_card_cut = None
        count = self.card_count
        for i in range(count - 1, -1, -1):
            witem = self._grid_layout.takeAt(i)
            widget = witem.widget()
            widget.close()
        action = self._action_group.actions()[0]
        action.setChecked(True)
        self._sort_menu_button.setText(action.text())
