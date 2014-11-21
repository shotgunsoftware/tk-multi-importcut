# Copyright (c) 2014 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
from sgtk.platform.qt import QtCore, QtGui

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

class CutDiffCard(QtGui.QFrame):
    def __init__(self, parent, cut_diff):
        super(CutDiffCard, self).__init__(parent)
        self._cut_diff = cut_diff
        self.ui = Ui_CutDiffCard()
        self.ui.setupUi(self)
        self.ui.shot_name_label.setText("<big><b>%s</b></big>" % self._cut_diff.name)
        self.ui.version_name_label.setText(self._cut_diff.version_name)
        head_in = self._cut_diff.shot_head_in
        if head_in is None:
            head_in = self._cut_diff.default_head_in
            self.ui.shot_head_in_label.setStyleSheet(
                "%s\ncolor: %s" % (
                    self.ui.shot_head_in_label.styleSheet(),
                    _COLORS["yellow"]
                )
            )
        self.ui.shot_head_in_label.setText("%s" % head_in)
        self.ui.shot_tail_out_label.setText("%s" % self._cut_diff.shot_tail_out)

        self.ui.status_label.setText("%s" % self._cut_diff.diff_type_label)
        if self._cut_diff.diff_type in _DIFF_TYPES_STYLE:
            self.ui.status_label.setStyleSheet(_DIFF_TYPES_STYLE[self._cut_diff.diff_type])

        value = self._cut_diff.cut_in
        new_value = self._cut_diff.new_cut_in
        self.ui.cut_in_label.setText("%s (%s)" % (new_value, value))

        value = self._cut_diff.cut_out
        new_value = self._cut_diff.new_cut_out
        self.ui.cut_out_label.setText("%s (%s)" % (new_value, value))

        value = self._cut_diff.head_duration
        new_value = self._cut_diff.new_head_duration
        self.ui.head_duration_label.setText("%s (%s)" % (new_value, value))

        value = self._cut_diff.duration
        new_value = self._cut_diff.new_duration
        self.ui.cut_duration_label.setText("%s (%s)" % (new_value, value))

        value = self._cut_diff.tail_duration
        new_value = self._cut_diff.new_tail_duration
        self.ui.tail_duration_label.setText("%s (%s)" % (new_value, value))

