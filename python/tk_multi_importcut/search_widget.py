# Copyright (c) 2014 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
"""

import sgtk
from sgtk.platform.qt import QtCore, QtGui

# Style sheet for the QLineEdit
_LINE_EDIT_STYLE = """
QLineEdit {
    background-image: url(:/tk_multi_importcut/search.png);
    background-repeat: no-repeat;
    background-position: center left;
    border-radius: 5px;
    padding-left:20px;
    padding-right:20px;
    margin-left: 12px;
    margin-right 12px;
}
"""

# Style sheet for the search button
_BUTTON_STYLE = """
QPushButton {
border: 0px solid;
background-image: "";
image: url(:/tk_multi_importcut/clear_search.png);
width: 16;
height: 16;
}
QPushButton::hover {
    image: url(:/tk_multi_importcut/clear_search_hover.png);
}
"""

class SearchWidget(QtGui.QLineEdit):
    """
    A search widget based on a QLineEdit
    - Add a search icon
    - Add a clear search button
    - Expose some signals
    """
    
    search_edited = QtCore.Signal(str)
    search_changed = QtCore.Signal(str)
    
    def __init__(self, parent=None):
        """
        Instantiate a new search widget
        """
        super(SearchWidget, self).__init__(parent)
        self.setStyleSheet(_LINE_EDIT_STYLE)

        # dynamically create the clear button so that we can place it over the
        # edit widget:
        self._clear_btn = QtGui.QPushButton(self)
        self._clear_btn.setFocusPolicy(QtCore.Qt.StrongFocus)
        self._clear_btn.setFlat(True)
        self._clear_btn.setCursor(QtCore.Qt.ArrowCursor)
        self._clear_btn.setStyleSheet(_BUTTON_STYLE)
        self._clear_btn.hide()
        
        h_layout = QtGui.QHBoxLayout(self)
        h_layout.addStretch()
        h_layout.addWidget(self._clear_btn)
        h_layout.setContentsMargins(3, 0, 3, 0)
        h_layout.setSpacing(0)
        self.setLayout(h_layout)


        # hook up the signals:
        self.textEdited.connect(self._on_text_edited)
        self.returnPressed.connect(self._on_return_pressed)
        self._clear_btn.clicked.connect(self.clear)
                
    # @property
    def _get_search_text(self):
        return self._safe_get_text()
    # @search_text.setter
    def _set_search_text(self, value):
        self.setText(value)
    
    search_text = property(_get_search_text, _set_search_text)

    def set_placeholder_text(self, text):
        """
        Small wrapper to follow our camel case naming conventions
        """
        self.setPlaceholderText(text)
                
    @QtCore.Slot()
    def clear(self):
        """
        Clear text
        """
        self.setText("")
        self.search_changed.emit("")
        self._clear_btn.hide()
                
    @QtCore.Slot(unicode)
    def _on_text_edited(self, text):
        """
        Called when the text is manually edited
        """
        self._clear_btn.setVisible(bool(text))
        self.search_edited.emit(text)
        
    @QtCore.Slot()
    def _on_return_pressed(self):
        """
        Called when the return key is pressed
        """
        self.search_changed.emit(self._safe_get_text())
        
    def _safe_get_text(self):
        """
        """
        text = self.text()
        # TODO - handle unicode
        return text
        
        