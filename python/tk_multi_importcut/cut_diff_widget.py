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
import tempfile

# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
from sgtk.platform.qt import QtCore, QtGui
edl = sgtk.platform.import_framework("tk-framework-editorial", "edl")

from .ui.cut_diff_card import Ui_CutDiffCard
from .cut_diff import CutDiff, _DIFF_TYPES
from .downloader import DownloadRunner

# Some standard colors
# Used in Sgtk apps
_COLORS = {
    "sg_blue" :     "#2C93E2",
    "sg_red"  :     "#FC6246",
    "mid_blue"  :   "#1B82D1",
    "green" :       "#57B510",
    "yellow" :      "#A1A51A",
    "lgrey" :       "#A5A5A5",
}

# Some colors for the different CuDiffType
_DIFF_TYPES_STYLE = {
    _DIFF_TYPES.NEW : "color: %s" % _COLORS["green"],
    _DIFF_TYPES.OMITTED : "color: %s" % _COLORS["sg_red"],
    _DIFF_TYPES.REINSTATED : "color: %s" % _COLORS["yellow"],
    _DIFF_TYPES.NO_CHANGE : "color: %s" % _COLORS["lgrey"],
}

# Format string for tooltips
_TOOL_TIP_FORMAT = """
Shot :
\t%s
Version :
\t%s
Cut Item :
\t%s
Edit :
\t%s
"""

class CutDiffCard(QtGui.QFrame):
    """
    A widget showing cut differences
    """
    def __init__(self, parent, cut_diff):
        """
        Instantiate a new cut diff card for the given CutDiff instance
        :param parent: A parent QWidget for this widget
        :param cut_diff: A CutDiff instance
        """
        super(CutDiffCard, self).__init__(parent)
        self._cut_diff = cut_diff
        self.ui = Ui_CutDiffCard()
        self.ui.setupUi(self)
        
        self._thumbnail_requested = False
        app = sgtk.platform.current_bundle()
        self._use_smart_fields = app.get_setting("use_smart_fields") or False
        # Cut order
        new_cut_order = self._cut_diff.new_cut_order or 0
        old_cut_order = self._cut_diff.cut_order or 0
        cut_order = new_cut_order or old_cut_order
        if old_cut_order != new_cut_order:
            font_color= _COLORS["sg_red"]
        else:
            font_color= _COLORS["lgrey"]
        
        if self._cut_diff.diff_type == _DIFF_TYPES.OMITTED:
            self.ui.cut_order_label.setText("<s><font color=%s>%03d</font></s>" % (font_color, cut_order))
        else:
            self.ui.cut_order_label.setText("<font color=%s>%03d</font>" % (font_color, cut_order))
        self.ui.shot_name_label.setText("<big><b>%s</b></big>" % self._cut_diff.name)
        
        sg_version = self._cut_diff.sg_version
        if not sg_version:
            self.ui.version_name_label.setText("<font color=%s>%s</font>" % (
                _COLORS["yellow"],
                self._cut_diff.version_name,
            ))
        elif sg_version.get("entity.Shot.code") != self._cut_diff.name:
            self.ui.version_name_label.setText("<font color=%s>%s</font>" % (
                _COLORS["sg_red"],
                self._cut_diff.version_name,
            ))
        else:
            self.ui.version_name_label.setText(self._cut_diff.version_name)

        value = self._cut_diff.head_in
        new_value = self._cut_diff.new_head_in
        self.display_values(self.ui.shot_head_in_label, new_value, value)

        value = self._cut_diff.tail_out
        new_value = self._cut_diff.new_tail_out
        self.display_values(self.ui.shot_tail_out_label, new_value, value)

        diff_type_label = self._cut_diff.diff_type_label
        reasons = ",<br>".join(self._cut_diff.reasons)
        if reasons:
            self.ui.status_label.setText("%s : <small>%s</small>" % (diff_type_label, reasons))
        else:
            self.ui.status_label.setText("%s" % diff_type_label)
        if self._cut_diff.diff_type in _DIFF_TYPES_STYLE:
            self.ui.status_label.setStyleSheet(_DIFF_TYPES_STYLE[self._cut_diff.diff_type])

        value = self._cut_diff.cut_in
        new_value = self._cut_diff.new_cut_in
        self.display_values(self.ui.cut_in_label, new_value, value)

        value = self._cut_diff.cut_out
        new_value = self._cut_diff.new_cut_out
        self.display_values(self.ui.cut_out_label, new_value, value)

        value = self._cut_diff.head_duration
        new_value = self._cut_diff.new_head_duration
        self.display_values(self.ui.head_duration_label, new_value, value)

        value = self._cut_diff.duration
        new_value = self._cut_diff.new_duration
        self.display_values(self.ui.cut_duration_label, new_value, value)

        value = self._cut_diff.tail_duration
        new_value = self._cut_diff.new_tail_duration
        self.display_values(self.ui.tail_duration_label, new_value, value)

        self.set_tool_tip()
        
        self.set_thumbnail(":/tk_multi_importcut/sg_shot_thumbnail.png")

    @QtCore.Slot(str)
    def new_thumbnail(self, path):
        """
        Called when a new thumbnail is available for this card
        """
        self.set_thumbnail(path)

    @property
    def cut_order(self):
        """
        Return a cut order that can be used to sort cards together
        """
        if self._cut_diff.new_cut_order is not None:
            return int(self._cut_diff.new_cut_order)
        if self._cut_diff.cut_order is not None:
            return int(self._cut_diff.cut_order)
        return -1

    def __getattr__(self, attr_name):
        """
        Allow access to attached cut diff
        """
        return getattr(self._cut_diff, attr_name)

    def display_values(self, widget, new_value, old_value):
        """
        Format the text for the given widget ( typically a QLabel ), comparing
        the old value to the new one, displaying only one of them if the two values
        are equal, coloring them otherwise
        """
        if self._cut_diff.diff_type == _DIFF_TYPES.NEW:
            widget.setText("<font color=%s>%s</font>" % (_COLORS["sg_red"], new_value))
        elif self._cut_diff.diff_type == _DIFF_TYPES.OMITTED:
            widget.setText("<font color=%s>(%s)</font>" % (_COLORS["lgrey"], old_value))
        else:
            if new_value != old_value:
                widget.setText("<font color=%s>%s</font> <font color=%s>(%s)</font>" % (
                    _COLORS["sg_red"], new_value,
                    _COLORS["lgrey"], old_value
                ))
            else:
                widget.setText("<font color=%s>%s</font>" % (_COLORS["lgrey"], new_value))

    def set_tool_tip(self):
        """
        Build a toolitp displaying details about this cut difference
        """
        shot_details = ""
        if self._cut_diff.sg_shot:
            if self._use_smart_fields:
                shot_details = \
                "Name : %s, Status : %s, Head In : %s, Cut In : %s, Cut Out : %s, Tail Out : %s, Cut Order : %s" % (
                    self._cut_diff.sg_shot["code"],
                    self._cut_diff.sg_shot["sg_status_list"],
                    self._cut_diff.sg_shot["smart_head_in"],
                    self._cut_diff.sg_shot["smart_cut_in"],
                    self._cut_diff.sg_shot["smart_cut_out"],
                    self._cut_diff.sg_shot["smart_tail_out"],
                    self._cut_diff.sg_shot["sg_cut_order"],
                )
            else:
                shot_details = \
                "Name : %s, Status : %s, Head In : %s, Cut In : %s, Cut Out : %s, Tail Out : %s, Cut Order : %s" % (
                    self._cut_diff.sg_shot["code"],
                    self._cut_diff.sg_shot["sg_status_list"],
                    self._cut_diff.sg_shot["sg_head_in"],
                    self._cut_diff.sg_shot["sg_cut_in"],
                    self._cut_diff.sg_shot["sg_cut_out"],
                    self._cut_diff.sg_shot["sg_tail_out"],
                    self._cut_diff.sg_shot["sg_cut_order"],
                )
        cut_item_details = ""
        if self._cut_diff.sg_cut_item:
            if self._cut_diff.sg_cut_item["sg_fps"] :
                fps = self._cut_diff.sg_cut_item["sg_fps"]
                tc_in = edl.Timecode(self._cut_diff.sg_cut_item["sg_timecode_cut_in"], fps)
                tc_out = edl.Timecode(self._cut_diff.sg_cut_item["sg_timecode_cut_out"], fps)
            else:
                tc_in = "????"
                tc_out = "????"
            cut_item_details = \
            "Cut Order %s, TC in %s, TC out %s, Cut In %s, Cut Out %s, Cut Duration %s" % (
                self._cut_diff.sg_cut_item["sg_cut_order"],
                tc_in,
                tc_out,
                self._cut_diff.sg_cut_item["sg_cut_in"],
                self._cut_diff.sg_cut_item["sg_cut_out"],
                self._cut_diff.sg_cut_item["sg_cut_duration"],
            )
        version_details = ""
        sg_version = self._cut_diff.sg_version
        if sg_version:
            version_details = "%s, link %s %s" % (
            sg_version["code"],
            sg_version["entity"]["type"] if sg_version["entity"] else "None",
            sg_version["entity.Shot.code"] if sg_version["entity.Shot.code"] else "",
            )
        msg = _TOOL_TIP_FORMAT % (
            shot_details,
            version_details,
            cut_item_details,
            self._cut_diff.edit
        )
        self.setToolTip(msg)

    def showEvent(self, event):
        """
        Request an async thumbnail download on first expose, if a thumbnail is 
        avalaible in SG.
        """
        if self._thumbnail_requested:
            event.ignore()
            return

        self._thumbnail_requested = True

        thumb_url = None
        if self._cut_diff.sg_version and self._cut_diff.sg_version.get("image"):
            thumb_url = self._cut_diff.sg_version["image"]
        elif self._cut_diff.sg_shot and self._cut_diff.sg_shot.get("image"):
            thumb_url = self._cut_diff.sg_shot["image"]
        if thumb_url:
            _, path = tempfile.mkstemp()
            downloader = DownloadRunner(
                sg_attachment=thumb_url,
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
        if pixmap.isNull():
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

