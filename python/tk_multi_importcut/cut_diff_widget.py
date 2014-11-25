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
import decimal
# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
from sgtk.platform.qt import QtCore, QtGui
edl = sgtk.platform.import_framework("tk-framework-editorial", "edl")

from .ui.cut_diff_card import Ui_CutDiffCard
from .cut_diff import CutDiff, _DIFF_TYPES

# Some standard colors
# Used in Sgtk apps
_COLORS = {
    "sg_blue" : "#2C93E2",
    "sg_red"  : "#FC6246",
    "mid_blue"  : "#1B82D1",
    "green" : "rgb(87, 181, 16)",
    "yellow" : "rgb(161, 165, 26)",
}


_STYLES = {
    "selected" : "border-color: %s" % _COLORS["sg_blue"],
}

_DIFF_TYPES_STYLE = {
    _DIFF_TYPES.NEW : "color: %s" % _COLORS["green"],
    _DIFF_TYPES.OMITTED : "color: %s" % _COLORS["sg_red"],
    _DIFF_TYPES.REINSTATED : "color: %s" % _COLORS["yellow"],
}
_TOOL_TIP_FORMAT = """
Shot :
\t%s
Cut Item :
\t%s
Edit :
\t%s
"""
class CutDiffCard(QtGui.QFrame):
    def __init__(self, parent, cut_diff):
        super(CutDiffCard, self).__init__(parent)
        self._cut_diff = cut_diff
        self.ui = Ui_CutDiffCard()
        self.ui.setupUi(self)
        self.ui.cut_order_label.setText("%s" % (self._cut_diff.new_cut_order or self._cut_diff.cut_order or "0"))
        self.ui.shot_name_label.setText("<big><b>%s</b></big>" % self._cut_diff.name)
        self.ui.version_name_label.setText(self._cut_diff.version_name)
        head_in = self._cut_diff.shot_head_in
        if head_in is None:
            head_in = self._cut_diff.default_head_in
            self.ui.shot_head_in_label.setStyleSheet(
                "%s\ncolor: %s" % (
                    self.ui.shot_head_in_label.styleSheet(),
                    _COLORS["sg_red"]
                )
            )
        self.ui.shot_head_in_label.setText("%s" % head_in)
        tail_out = self._cut_diff.shot_tail_out
        if tail_out is None:
            tail_out = self._cut_diff.default_tail_out
            self.ui.shot_tail_out_label.setStyleSheet(
                "%s\ncolor: %s" % (
                    self.ui.shot_tail_out_label.styleSheet(),
                    _COLORS["sg_red"]
                )
            )
        self.ui.shot_tail_out_label.setText("%s" % tail_out)

        self.ui.status_label.setText("%s" % self._cut_diff.diff_type_label)
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
        
    @property
    def cut_order(self):
        if self._cut_diff.new_cut_order is not None:
            return int(self._cut_diff.new_cut_order)
        if self._cut_diff.cut_order is not None:
            return int(self._cut_diff.cut_order)
        return -1

    def display_values(self, widget, new_value, old_value):
        if self._cut_diff.diff_type == _DIFF_TYPES.NEW:
            widget.setText("<font color=%s>%s</font>" % (_COLORS["sg_red"], new_value))
        else:
            if new_value != old_value:
                widget.setText("<font color=%s>%s</font> (%s)" % (_COLORS["sg_red"], new_value, old_value))
            else:
                widget.setText("%s (%s)" % (new_value, old_value))

    def set_tool_tip(self):
        shot_details = ""
        if self._cut_diff.sg_shot:
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
                fps = decimal.Decimal(self._cut_diff.sg_cut_item["sg_fps"])
                tc_in = edl.timecode_from_frame(
                    int(self._cut_diff.sg_cut_item["sg_timecode_cut_in"] * fps / 1000)
                )
                tc_out = edl.timecode_from_frame(
                    int(self._cut_diff.sg_cut_item["sg_timecode_cut_out"] * fps / 1000)
                )
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
        msg = _TOOL_TIP_FORMAT % (
            shot_details,
            cut_item_details,
            self._cut_diff.edit
        )
        self.setToolTip(msg)
