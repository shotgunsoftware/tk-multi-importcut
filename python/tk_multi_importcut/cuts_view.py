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

from .cut_widget import CutCard

class CutsView(QtCore.QObject):
    """
    Cuts view page handler
    """
    show_cut_diff = QtCore.Signal(dict)

    def __init__(self, grid_widget, sort_menu_button):
        super(CutsView, self).__init__()
        self._grid_widget = grid_widget
        self._selected_card_cut = None
        self._logger = get_logger()
        self.build_cuts_sort_menu(sort_menu_button)

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

    @QtCore.Slot(QtGui.QWidget)
    def cut_selected(self, card):
        """
        Called when a cut card is selected, ensure only one is selected at
        a time
        """
        if self._selected_card_cut:
            self._selected_card_cut.unselect()
            self._logger.debug("Unselected %s" % self._selected_card_cut)
        self._selected_card_cut = card
        self._selected_card_cut.select()
        self._logger.debug("Selected %s" % self._selected_card_cut)

    @QtCore.Slot(dict)
    def show_cut(self, sg_cut):
        """
        Called when cut changes needs to be shown for a particular sequence/cut
        """
        self._logger.info("Retrieving cut information for %s" % sg_cut["code"] )
        self.show_cut_diff.emit(sg_cut)
        #self.step_done(2)

    def build_cuts_sort_menu(self, button):
        self._cuts_sort_menu = QtGui.QMenu()
        button.setMenu(self._cuts_sort_menu)
        action_group =  QtGui.QActionGroup(self)
        for s in ["Sort by Date", "Sort by Name", "Sort by Status"]:
            sort_action = QtGui.QAction(
                s,
                action_group,)
            sort_action.setCheckable(True)
            self._cuts_sort_menu.addAction(sort_action)
        action = action_group.actions()[0]
        action.setChecked(True)
        button.setText(action.text())

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


