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
    A custom line edit used to edit the value
    """
    __matching_list = ["one", "two", "001_001"]

    def __init__(self, *args, **kwargs):
        super(EntityLineWidget, self).__init__(*args, **kwargs)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        completer = QtGui.QCompleter(self.__matching_list, self)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setCompleter(completer)


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
