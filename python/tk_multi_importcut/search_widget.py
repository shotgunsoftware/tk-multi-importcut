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

try:
    from tank_vendor import sgutils
except ImportError:
    from tank_vendor import six as sgutils

# TODO : This is based on TK search widget code, before it was available in Qt widgets
# framework. So, at some point, this code should be replaced with the TK
# implementation, when it is available.
# This is why styling is kept inline, as it is likely to go away when the switch
# happens


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

        :param parent: Parent QWidget for this widget
        """
        super().__init__(parent)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        # dynamically create the clear button so that we can place it over the
        # edit widget.
        self._clear_btn = QtGui.QPushButton(self)
        self._clear_btn.setFocusPolicy(QtCore.Qt.StrongFocus)
        self._clear_btn.setFlat(True)
        self._clear_btn.setCursor(QtCore.Qt.ArrowCursor)
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

    def _get_search_text(self):
        return self._safe_get_text()

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

    @QtCore.Slot(str)
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
        """ """
        text = sgutils.ensure_str(self.text())
        return text
