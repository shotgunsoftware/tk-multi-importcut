# Copyright (c) 2014 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk
from sgtk.platform.qt import QtCore, QtGui

class EntityLineWidget(QtGui.QLineEdit):
    """
    A custom line edit with a completer. Using a custom widget allows easy
    style sheet styling with the class name, e.g. 

    /* Make the line edit looks like a QLabel when not in edit mode */
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
    __known_list = []

    def __init__(self, *args, **kwargs):
        super(EntityLineWidget, self).__init__(*args, **kwargs)
        self.set_property("valid", True)

    @classmethod
    def set_known_list(cls, known_list):
        """
        Define the list of known names for the completer
        """
        cls.__known_list=known_list

    def __init__(self, *args, **kwargs):
        super(EntityLineWidget, self).__init__(*args, **kwargs)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.setPlaceholderText("No Link")
        completer = QtGui.QCompleter(self.__known_list, self)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setCompleter(completer)

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
        self.style().unpolish(self);
        self.style().polish(self);

    def focusInEvent(self, event):
        self.set_property("valid", True)
        super(EntityLineWidget,self).focusInEvent(event)

#    def mousePressEvent(self, event):
#        """
#        Handle single click events : select this card
#        """
#        self.setReadOnly(False)
#        print "Click !"
#
#    def focusOutEvent(self, event):
#        self.setReadOnly(True)
#        print "Out !"
