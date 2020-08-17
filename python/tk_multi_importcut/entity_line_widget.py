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


class EntityLineWidget(QtGui.QLineEdit):
    """
    A custom line edit with a completer. Using a custom widget allows easy
    style sheet styling with the class name, e.g.

    /* Make the line edit look like a QLabel when not in edit mode */
    EntityLineWidget {
        border: none;
        background: #424242;
    }

    /* QLineEdit style when in edit mode */
    EntityLineWidget:focus {
        border: 2px solid #2C93E2;
        border-radius: 2px;
        background: #565656;
    }

    """

    # A list of possible values for completion
    __known_list = []

    # Our own signal to emit new values as provided ones didn't work in our case
    value_changed = QtCore.Signal(str)

    def __init__(self, *args, **kwargs):
        """
        Instantiate a new EntityLineWidget

        :param args: Arbitrary list of parameters used in base class init
        :param kwargs: Arbitrary dictionary of parameters used in base class init
        """
        super(EntityLineWidget, self).__init__(*args, **kwargs)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.setPlaceholderText("No Link")
        # Add our known list as a completer
        completer = QtGui.QCompleter(self.__known_list, self)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setCompleter(completer)
        # Only allow alpha numeric characters, _ and -
        rx = QtCore.QRegExp("[\w-]*")
        self.setValidator(QtGui.QRegExpValidator(rx, self))
        self.set_property("valid", True)
        # Just a way to be warned when the value was edited
        self.editingFinished.connect(self.edited)

    @classmethod
    def set_known_list(cls, known_list):
        """
        Define the list of known names for the completer

        :param known_list: A list of possible values
        """
        cls.__known_list = sorted(known_list)

    def set_property(self, name, value):
        """
        Set the given property to the given value

        :param name: A property name
        :param value: The value to set
        """
        self.setProperty(name, value)
        # We are using a custom property in style sheets
        # we need to force a style sheet re-computation with
        # unpolish / polish
        self.style().unpolish(self)
        self.style().polish(self)

    def focusInEvent(self, event):
        """
        When entering editing, clear the invalid state, and
        call the QLineEdit base class focusInEvent

        :param event: A standard Qt event
        """
        self.set_property("valid", True)
        super(EntityLineWidget, self).focusInEvent(event)

    @QtCore.Slot()
    def edited(self):
        """
        Called when editingFinished is emitted
        Clear the focus for this widget and emit a signal with
        the current value.
        """
        # No need to convert the input text to utf-8 str here, as we just emit it
        value = self.text()
        self.clearFocus()
        self.value_changed.emit(value)
