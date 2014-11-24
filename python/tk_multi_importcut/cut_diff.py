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

import sgtk
from sgtk.platform.qt import QtCore
edl = sgtk.platform.import_framework("tk-framework-editorial", "edl")

def diff_types(**enums):
    return type("CutDiffType", (), enums)

_DIFF_TYPES = diff_types(NEW=0, OMITTED=1, REINSTATED=2, CUT_CHANGE=3)
_DIFF_LABELS = {
    _DIFF_TYPES.NEW : "New",
    _DIFF_TYPES.OMITTED : "Omitted",
    _DIFF_TYPES.REINSTATED : "Reinstated",
    _DIFF_TYPES.CUT_CHANGE : "Cut Change",
}

class CutDiff(QtCore.QObject):

    def __init__(self, name, sg_shot=None, sg_version=None, edit=None, cut_item=None):
        super(CutDiff, self).__init__()
        self._name = name
        self._sg_shot = sg_shot
        self._sg_version = sg_version
        self._edit = edit
        self._cut_item = cut_item
        self._app = sgtk.platform.current_bundle()

        self._default_head_in = self._app.get_setting("default_head_in")
        self._head_in_base = edl.frame_from_timecode(self._app.get_setting("head_in_base_timecode"))

        # The type of difference we are dealing with
        if not self._sg_shot:
            self._diff_type = _DIFF_TYPES.NEW
        elif not self._edit:
            self._diff_type = _DIFF_TYPES.OMITTED
        # We have both a shot and an edit
        elif self._sg_shot["sg_status_list"] == "omt":
            self._diff_type = _DIFF_TYPES.REINSTATED
        else:
            self._diff_type = _DIFF_TYPES.CUT_CHANGE

    @classmethod
    def get_diff_type_label(cls, diff_type):
        return _DIFF_LABELS[diff_type]

    @property
    def sg_shot(self):
        return self._sg_shot

    @property
    def edit(self):
        return self._edit

    @property
    def name(self):
        return self._name

    @property
    def version_name(self):
        if self._edit:
            clip_name = self._edit.get_clip_name()
            if clip_name:
                # Can have a .mov extension
                return clip_name.split(".")[0]
        return None

    @property
    def default_head_in(self):
        return self._default_head_in

    @property
    def default_tail_out(self):
        new_tail_duration = self.new_tail_duration
        if new_tail_duration is None:
            return None
        new_cut_out = self.new_cut_out
        if new_cut_out is None:
            return None
        return new_cut_out + new_tail_duration

    @property
    def head_in_base(self):
        return self._head_in_base

    @property
    def shot_head_in(self):
        if self._sg_shot:
            return self._sg_shot.get("sg_head_in")
        return None

    @property
    def shot_tail_out(self):
        if self._sg_shot:
            return self._sg_shot.get("sg_tail_out")
        return None

    @property
    def cut_in(self):
        return None

    @property
    def cut_out(self):
        return None

    @property
    def new_cut_in(self):
        if self._edit:
            offset = self.shot_head_in
            if offset is None:
                offset = self.default_head_in
            return offset + self._edit.source_in.to_frame() - self.head_in_base
        return None

    @property
    def new_cut_out(self):
        if self._edit:
            offset = self.shot_head_in
            if offset is None:
                offset = self.default_head_in
            return offset + self._edit.source_out.to_frame() - self.head_in_base
        return None

    @property
    def head_duration(self):
        if not self._cut_item or not self._sg_shot:
            return None
        cut_in = self._cut_item["sg_cut_in"]
        head_in = self.shot_head_in
        if cut_in is None or head_in is None:
            return None
        return cut_in - head_in

    @property
    def new_head_duration(self):
        if self._edit:
            new_cut_in = self.new_cut_in
            if new_cut_in is None:
                return None
            head_in = self.shot_head_in
            if head_in is None:
                head_in = self.default_head_in
            offset = self.shot_head_in or self._app.get_setting("default_head_in") or 1001
            return new_cut_in - head_in
        return None

    @property
    def duration(self):
        if self._cut_item:
            return self._cut_item["sg_cut_duration"]
        return None

    @property
    def new_duration(self):
        if self._edit:
            return self._edit.source_duration
        return None

    @property
    def tail_duration(self):
        if not self._cut_item or not self._sg_shot:
            return None
        cut_out = self._cut_item["sg_cut_out"]
        tail_out = self.shot_tail_out
        if cut_out is None or tail_out is None:
            return None
        return cut_out - tail_out

    @property
    def new_tail_duration(self):
        cut_out = self.new_cut_out
        if cut_out is None:
            return None
        tail_out = self.shot_tail_out
        if tail_out is None:
            return self._app.get_setting("default_tail_out_duration")
        if self._edit:
            return tail_out - cut_out - self.head_in_base
        return None

    @property
    def diff_type(self):
        return self._diff_type

    @property
    def diff_type_label(self):
        return self.get_diff_type_label(self._diff_type)
