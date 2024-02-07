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

from .project_widget import ProjectCard


class ProjectsView(QtCore.QObject):
    """
    Projects view page handler, display Project cards in a grid layout
    """

    # Emitted when a Project is chosen for next step
    project_chosen = QtCore.Signal(dict)
    # Emitted when a different Project is selected
    selection_changed = QtCore.Signal(dict)
    # Emitted when the info message changed
    new_info_message = QtCore.Signal(str)

    def __init__(self, grid_layout):
        """
        Instantiate a new Project view with the given layout

        :param grid_layout: A QGridLayout
        """
        super(ProjectsView, self).__init__()
        self._grid_layout = grid_layout
        self._selected_project_card = None
        self._logger = get_logger()
        # A one line message which can be displayed when the view is visible
        self._info_message = ""

    @property
    def card_count(self):
        """
        Return the number of cards held by this view

        :returns: The number of cards, as an integer
        """
        return self._grid_layout.count() - 1  # We have a stretcher

    @property
    def info_message(self):
        """
        Returns the info message

        :returns: The info message as a string
        """
        return self._info_message

    @QtCore.Slot(dict)
    def new_sg_project(self, sg_project):
        """
        Called when a new Project card widget needs to be added to the list
        of retrieved Projects

        :param sg_project: A PTR Project dictionary
        """
        i = self.card_count
        # Remove it
        spacer = self._grid_layout.takeAt(i)
        row = i / 2
        column = i % 2
        self._logger.debug("Adding %s at %d %d %d" % (sg_project, i, row, column))
        widget = ProjectCard(parent=None, sg_project=sg_project)
        widget.highlight_selected.connect(self.project_selected)
        widget.chosen.connect(self.project_chosen)
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
            ("%d %ss" % (count, sg_project["type"]))
            if count > 1
            else ("%d %s" % (count, sg_project["type"]))
        )
        self.new_info_message.emit(self._info_message)

    @QtCore.Slot(QtGui.QWidget)
    def project_selected(self, card):
        """
        Called when a Project card is selected, ensure only one is selected at
        a time

        :param card: A Project card
        """
        if self._selected_project_card:
            self._selected_project_card.unselect()
            self._logger.debug("Unselected %s" % self._selected_project_card)
        self._selected_project_card = card
        self._selected_project_card.select()
        self.selection_changed.emit(card.sg_project)
        self._logger.debug("Selected %s" % self._selected_project_card)

    @QtCore.Slot(six.text_type)
    def search(self, u_text):
        """
        Display only projects whose name matches the given text,
        display all of them if text is empty

        :param u_text: A unicode string to match
        """
        text = six.ensure_str(u_text)
        self._logger.debug("Searching for %s" % text)
        count = self.card_count
        if not count:
            # Avoid 0 projects message to be emitted if we don't have
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
                if text.lower() in widget.project_name.lower():
                    match_count += 1
                    widget.setVisible(True)
                else:
                    widget.setVisible(False)
        # Sort widgets so visible ones will be first, with rows
        # distribution re-arranged
        self.sort_changed()
        self._info_message = (
            ("%d Projects" % match_count) if match_count > 1 else ("%d Project" % count)
        )
        self.new_info_message.emit(self._info_message)

    def sort_changed(self):
        """
        Called when projects need to be sorted again
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
                x.project_name.lower(),
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
        Reset the page displaying available projects
        """
        self._selected_project_card = None
        count = self.card_count
        for i in range(count - 1, -1, -1):
            witem = self._grid_layout.takeAt(i)
            widget = witem.widget()
            widget.close()
