# Copyright (c) 2014 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import tempfile

# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
from sgtk.platform.qt import QtCore, QtGui
from .downloader import DownloadRunner
from .logger import get_logger

from .ui.cut_card import Ui_CutCard
# Some standard colors
# Used in Sgtk apps
_COLORS = {
    "sg_blue" : "#2C93E2",
    "sg_red"  : "#FC6246",
    "mid_blue"  : "#1B82D1",
    "green" :       "#57B510",
    "yellow" :      "#A1A51A",
    "lgrey" :       "#A5A5A5",
    "dgrey" :       "#666666",
}


_STYLES = {
    "selected" : "border-color: %s" % _COLORS["sg_blue"],
}
_STATUS_COLORS = {
    "omt" : _COLORS["sg_red"],
    "act" : _COLORS["green"],
    "ip" : _COLORS["sg_blue"],
    "hld" : _COLORS["lgrey"],
    "fin" : _COLORS["dgrey"],
}
class CutCard(QtGui.QFrame):
    """
    Widget displaying a Shotgun Cut
    """
    # Emitted when cut changes for the attached Sequence should be displayed
    show_cut = QtCore.Signal(dict)
    # Emitted when this card wants to be selected
    highlight_selected = QtCore.Signal(QtGui.QWidget)
    def __init__(self, parent, sg_cut):
        """
        Instantiate a new SequenceCard for the given Shotgun Sequence
        :param parent: A parent QWidget
        :param sg_cut: A Shotgun cut, as a dictionary, to display
        """
        super(CutCard, self).__init__(parent)
        self._thumbnail_requested = False
        self._sg_cut = sg_cut
        self._logger = get_logger()

        self.ui = Ui_CutCard()
        self.ui.setupUi(self)
        self.ui.title_label.setText("<big><b>%s</b></big>" % sg_cut["code"])
        if self._sg_cut["_display_status"]:
            self.ui.status_label.setText(
                "<font color=%s>%s</font>" % (
                    _STATUS_COLORS.get(self._sg_cut["sg_status_list"], _COLORS["lgrey"]),
                    self._sg_cut["_display_status"]["name"],
                )
            )
        else:
            self.ui.status_label.setText(sg_cut["sg_status_list"])
        self.ui.details_label.setText("<small>%s</small>" % sg_cut["description"])
        self.ui.select_button.setVisible(False)
        self.ui.select_button.clicked.connect(self.show_selected)
        self.set_thumbnail(":/tk_multi_importcut/sg_sequence_thumbnail.png")
#        from random import randint
#        self.set_thumbnail( [
#            "/Users/steph/devs/sg/sgtk/apps/tk-multi-importcut/resources/no_thumbnail.png",
#            "/Users/steph/Pictures/microsoftazurelogo.png",
#            "/Users/steph/Pictures/IMG_4720.jpg"
#        ][randint(0, 2)])

    @QtCore.Slot()
    def select(self):
        """
        Set this card UI to selected mode
        """
        self.setProperty("selected", True)
        self.ui.select_button.setVisible(True)
        self.setStyleSheet(_STYLES["selected"])

    @QtCore.Slot()
    def unselect(self):
        """
        Set this card UI to unselected mode
        """
        self.setProperty("selected", False)
        self.ui.select_button.setVisible(False)
        self.setStyleSheet("")

    @QtCore.Slot()
    def show_selected(self):
        """
        Gently ask to show cut summary for the attached Shotgun sequence
        """
        self.highlight_selected.emit(self)
        self.show_sequence.emit(self._sg_cut)
        self.ui.select_button.setVisible(False)

    @QtCore.Slot(str)
    def new_thumbnail(self, path):
        """
        Called when a new thumbnail is available for this card
        """
        self._logger.debug("Loading thumbnail %s for %s" % (path, self._sg_cut["code"]))
        self.set_thumbnail(path)

    def mouseDoubleClickEvent(self, event):
        """
        Handle double clicks : show cut changes for the attached sequence
        """
        self.show_selected()

    def mousePressEvent(self, event):
        """
        Handle single click events : select this card
        """
        self.highlight_selected.emit(self)

    def enterEvent(self, event):
        """
        Display a "chevron" button when the mouse enter the widget
        """
        self.ui.select_button.setVisible(True)

    def leaveEvent(self, event):
        """
        Hide the "chevron" button when the mouse leave the widget
        """
        self.ui.select_button.setVisible(False)

    def showEvent(self, event):
        """
        Request an async thumbnail download on first expose, if a thumbnail is 
        avalaible in SG.
        """
        if self._thumbnail_requested:
            event.ignore()
            return
        self._thumbnail_requested = True
        if self._sg_cut and self._sg_cut["image"]:
            self._logger.debug("Requesting %s for %s" % ( self._sg_cut["image"], self._sg_cut["code"]))
            _, path = tempfile.mkstemp()
            downloader = DownloadRunner(
                sg_attachment=self._sg_cut["image"],
                path=path,
            )
            downloader.file_downloaded.connect(self.new_thumbnail)
            QtCore.QThreadPool.globalInstance().start(downloader)

        event.ignore()
    
    def set_thumbnail(self, thumb_path):
        """
        Build a pixmap from the given file path and use it as icon, resizing it to 
        fit into the widget icon size
        
        :param thumb_path: Full path to an image to use as thumbnail
        """
        size = self.ui.icon_label.size()
        ratio = size.width() / float(size.height())
        pixmap = QtGui.QPixmap(thumb_path)
        qimage = QtGui.QImage()
        #print QtGui.QImageReader.supportedImageFormats()
        if pixmap.isNull():
            self._logger.debug("Null pixmap %s %d %d for %s" % (
                thumb_path,
                pixmap.size().width(), pixmap.size().height(),
                self._sg_cut["code"]))
            return
        psize = pixmap.size()
        pratio = psize.width() / float(psize.height())
        if pratio > ratio:
            self.ui.icon_label.setPixmap(
                pixmap.scaledToWidth(size.width(), mode=QtCore.Qt.SmoothTransformation)
            )
        else:
            self.ui.icon_label.setPixmap(
                pixmap.scaledToHeight(size.height(), mode=QtCore.Qt.SmoothTransformation)
            )
