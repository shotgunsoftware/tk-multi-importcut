# Copyright (c) 2021 Autodesk, Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the ShotGrid Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the ShotGrid Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk, Inc.

# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
from sgtk.platform.qt import QtCore, QtGui


class ExtendedThumbnail(QtGui.QLabel):
    """
    A custom widget allowing to draw some text on top of a thumbnail
    """

    def __init__(self, text, *args, **kwargs):
        """
        Instantiate a new ExtendedThumbnail

        :param text: A string
        :param args: Arbitrary list of parameters used in base class init
        :param kwargs: Arbitrary dictionary of parameters used in base class init
        """
        super().__init__(*args, **kwargs)
        self._text = text or ""
        self._color = None
        self._strike_through = False

    def set_text(self, text, color, strike_through=False):
        """
        Set the text, color and if this thumbnail should have a strike-through

        :param text: A string
        :param color: An optional color to override the QColor used when drawing
        :param strike_through: Whether or not a strike-through should be drawn
        """
        self._text = str(text)
        if color:
            self._color = QtGui.QColor(color)
        self._strike_through = strike_through
        self.update()

    def paintEvent(self, event):
        """
        Override QLabel paintEvent

        :param event: A QEvent
        """
        super(ExtendedThumbnail, self).paintEvent(event)
        painter = QtGui.QPainter()
        try:
            painter.begin(self)
            self._paint_overlay(painter)
        except:
            raise
        finally:
            # Make sure we end painter as not doing so can lead to very very
            # bad things
            painter.end()

    def _paint_overlay(self, painter):
        """
        Paint the overlay using the given painter

        :param painter: An active QPainter
        """
        painter.setRenderHints(QtGui.QPainter.Antialiasing)
        painter.setFont(self.font())
        if self._color:
            painter.setPen(self._color)
        brush = QtGui.QBrush(
            QtGui.QColor(
                painter.pen().color().red() * 0.1,
                painter.pen().color().green() * 0.1,
                painter.pen().color().blue() * 0.1,
                128,
            ),
            QtCore.Qt.SolidPattern,
        )
        painter.setBrush(brush)
        #        if self._strike_through:
        #            painter.fillRect(self.rect(), QtGui.QBrush(self._color, QtCore.Qt.BDiagPattern))
        #            painter.drawLine(0.0, 0.0, self.rect().width(), self.rect().height() )
        #            painter.drawLine(self.rect().width(), 0.0, 0.0, self.rect().height())
        half_size = self.fontInfo().pixelSize()
        size = 2.0 * half_size
        offset = 4.0
        painter.translate(offset, offset)
        # Draw a filled circle under the cut order
        # we use a round rect instead of an ellipse because we might have to make
        # them rounded rectangles instead of plain circles later, if we have to deal
        # with cut orders with more than 3 digits. Just add half_size to both
        # rectangles ( rect and text ) width to get a rounded rectangle
        painter.drawRoundedRect(0.0, 0.0, size, size, half_size, half_size)
        painter.drawText(0.0, 0.0, size, size, QtCore.Qt.AlignCenter, str(self._text))
