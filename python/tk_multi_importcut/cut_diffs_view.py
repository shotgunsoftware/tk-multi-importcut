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
from .cut_diff_widget import CutDiffCard
from .cut_diff import CutDiff, _DIFF_TYPES

class CutDiffsView(QtCore.QObject):
    """
    Handle CutDiffWidget view
    """
    totals_changed = QtCore.Signal()
    
    def __init__(self, list_widget):
        """
        Construct a new CutDiffsView, using the given list_widget as widgets 
        container

        :param list_widget: A QVBoxLayout
        """
        super(CutDiffsView, self).__init__()
        self._list_widget = list_widget
        self._logger = get_logger()
        self._cuts_display_repeated = False
        self._vfx_shots_only=False
        self._cuts_display_mode = -1

    @QtCore.Slot(CutDiff)
    def new_cut_diff(self, cut_diff):
        """
        Called when a new cut diff card widget needs to be added to the list of retrieved
        changes

        :param cut_diff: A CutDiff instance for whose a widget needs to be added
        """
        self._logger.debug("Adding %s" % cut_diff.name)
        self.totals_changed.emit()
        widget = CutDiffCard(parent=None, cut_diff=cut_diff)

        cut_order = widget.cut_order
        count = self._list_widget.count()
        # Shortcut : instead of looping over all entries, check if we can simply
        # insert it at the end
        if count > 1: # A widget + the stretcher
            witem = self._list_widget.itemAt(count-2)
            if cut_order > witem.widget().cut_order:
                self._list_widget.insertWidget(count-1, widget)
                self._list_widget.setStretch(self._list_widget.count()-1, 1)
                return
        # Retrieve where we should insert it
        # Last widget is a stretcher, so we stop at self._list_widget.count()-2
        for i in range(0, count-1):
            witem = self._list_widget.itemAt(i)
            if witem.widget().cut_order == cut_order:
                if cut_diff.diff_type == _DIFF_TYPES.OMITTED:
                    self._list_widget.insertWidget(i, widget)
                else:
                    self._list_widget.insertWidget(i+1, widget)
                break
            elif witem.widget().cut_order > cut_order: # Insert before next widget
                self._list_widget.insertWidget(i, widget)
                break
        else:
            self._list_widget.insertWidget(count-1, widget)
        self._list_widget.setStretch(self._list_widget.count()-1, 1)
        # Redisplay widgets
        self._display_for_summary_mode()

    @QtCore.Slot(CutDiff)
    def delete_cut_diff(self, cut_diff):
        """
        Delete the widget associated with the given CutDiff instance

        :param cut_diff: A CutDiff instance
        """
        # Retrieve the widget we can delete
        count = self._list_widget.count()
        # Last widget is a stretcher, so we stop at self._list_widget.count()-2
        for i in range(0, count-1):
            witem = self._list_widget.itemAt(i)
            widget = witem.widget()
            if widget.cut_diff==cut_diff: # Found it
                witem = self._list_widget.takeAt(i)
                widget=witem.widget()
                widget.setParent(None)
                widget.deleteLater()
                break
        else:
            # This should never happen, raise an error if it does ...
            raise RuntimeError("Couldn't retrieve a widget for %s" % cut_diff)
        # Redisplay widgets
        self._display_for_summary_mode()

    @QtCore.Slot(bool)
    def display_repeated_cuts(self, checked):
        """
        Only display cut diff cards widget affecting the same shot(s)
        :param checked: A boolean, whether or not repeated cuts should be displayed
        """
        self._cuts_display_repeated = checked
        self.set_display_summary_mode(True, self._cuts_display_mode)

    @QtCore.Slot(bool)
    def display_vfx_cuts(self, checked):
        """
        Only display cut diff cards for VFX shots
        :param checked: A boolean, whether or not non VFX cuts should be displayed
        """
        self._vfx_shots_only = checked
        self.set_display_summary_mode(True, self._cuts_display_mode)

    def set_display_summary_mode(self, activated, mode):
        """
        Called when the user click on the top views selectors in the cut summary
        page
        :param activated: A boolean, whether or not the selector was turned on
        :param mode: The mode which was activated
        """
        # Modes are exclusive, so we don't have to handle the case were a mode
        # was turned off as it means another one was turned on
        if not activated:
            return
        self._cuts_display_mode = mode
        self._logger.debug("Switching to %s mode" % mode)
        self._display_for_summary_mode()

    def _display_for_summary_mode(self):
        """
        Hide / show CutDiff widgets depending on the current mode
        """
        show_only_repeated = self._cuts_display_repeated
        show_only_vfx=self._vfx_shots_only
        count = self._list_widget.count() -1 # We have stretcher
        if self._cuts_display_mode == -1: # Show everything
            for i in range(0, count):
                widget = self._list_widget.itemAt(i).widget()
                widget.setVisible(not show_only_vfx or widget.is_vfx_shot)
        elif self._cuts_display_mode > 99: # Show "Need Rescan"
            for i in range(0, count):
                widget = self._list_widget.itemAt(i).widget()
                if widget.need_rescan:
                    widget.setVisible(not show_only_vfx or widget.is_vfx_shot)
                else:
                    widget.hide()
        else:
            for i in range(0, count):
                widget = self._list_widget.itemAt(i).widget()
                if widget.diff_type == self._cuts_display_mode:
                    widget.setVisible(not show_only_vfx or widget.is_vfx_shot)
                else:
                    widget.hide()
        if count > 1:
            # Avoid flashes and jittering by resizing the grid widget to a size
            # suitable to hold all cards
            wsize = self._list_widget.itemAt(0).widget().size()
            self._list_widget.parentWidget().resize(
                self._list_widget.parentWidget().size().width(),
                wsize.height()* count)


    def clear(self):
        """
        Reset the cut summary view page
        """
        count = self._list_widget.count() -1 # We have stretcher
        for i in range(count-1, -1, -1):
            witem = self._list_widget.takeAt(i)
            widget = witem.widget()
            widget.close()

