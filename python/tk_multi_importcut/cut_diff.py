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
# Import the EDL framework
edl = sgtk.platform.import_framework("tk-framework-editorial", "edl")

# Define difference types as enums
def diff_types(**enums):
    return type("CutDiffType", (), enums)
# Values for cut diff types
_DIFF_TYPES = diff_types(NEW=0, OMITTED=1, REINSTATED=2, RESCAN=3, CUT_CHANGE=4, NO_CHANGE=5)
# Display names for cut diff types
_DIFF_LABELS = {
    _DIFF_TYPES.NEW : "New",
    _DIFF_TYPES.OMITTED : "Omitted",
    _DIFF_TYPES.REINSTATED : "Reinstated",
    _DIFF_TYPES.RESCAN : "Rescan Needed",
    _DIFF_TYPES.CUT_CHANGE : "Cut Change",
    _DIFF_TYPES.NO_CHANGE : "No Change",
}

class CutDiff(QtCore.QObject):
    """
    A cut difference is based on :
    - An EDL entry
    - A Shotgun cut item
    - A Shotgun shot
    At least one of them needs to be set
    A Shotgun Version can be given, for reference purpose
    """
    def __init__(self, name, sg_shot=None, sg_version=None, edit=None, sg_cut_item=None):
        """
        Instantiate a new cut difference
        
        :param name: A name for this cut difference, usually the shot name
        :param sg_shot: An optional shot dictionary, as retrieved from Shotgun
        :param sg_version: An optional version dictionary, as retrieved from Shotgun
        :param edit: An optional EditEvent instance, retrieved from an EDL
        :param sg_cut_item: An optional cut item dictionary, as retrieved from Shotgun
        """
        super(CutDiff, self).__init__()
        self._name = name
        self._sg_shot = sg_shot
        self._sg_version = sg_version
        self._edit = edit
        self._sg_cut_item = sg_cut_item
        self._app = sgtk.platform.current_bundle()

        self._repeated = False
        self._diff_type = _DIFF_TYPES.NO_CHANGE
        self._cut_changes_reasons = []
        self._default_head_in = self._app.get_setting("default_head_in")
        self._default_head_in_duration = self._app.get_setting("default_head_in_duration")
        self._use_smart_fields = self._app.get_setting("use_smart_fields") or False

        # Retrieve the cut diff type from the given params
        self.check_changes()

    @classmethod
    def get_diff_type_label(cls, diff_type):
        """
        Return a display name for the given cut diff type
        :param diff_type: A _DIFF_TYPES entry
        """
        return _DIFF_LABELS[diff_type]

    @property
    def sg_shot(self):
        """
        Return the Shotgun shot for this diff, if any
        """
        return self._sg_shot

    @property
    def sg_cut_item(self):
        """
        Return the Shotgun cut item for this diff, if any
        """
        return self._sg_cut_item

    @property
    def edit(self):
        """
        Return the EditEntry for this diff, if any
        """
        return self._edit

    @property
    def name(self):
        """
        Return the name of this diff
        """
        return self._name

    @property
    def version_name(self):
        """
        Return the version name for this diff, if any
        """
        if self._edit:
            return self._edit.get_version_name()
        return None

    @property
    def sg_version(self):
        """
        Return the Shotgun version for this diff, if any
        """
        if self._edit:
            return self._edit.get_sg_version()
        return None

    def set_sg_version(self, sg_version):
        """
        Set the Shotgun version associated with this diff
        :raises: ValueError if no EditEvent is associated to this diff
        """
        if not self._edit:
            raise ValueError("Can't set Shotgun version without an edit entry")
        self._edit._sg_version = sg_version
    
    @property
    def default_head_in(self):
        """
        Return the default head in value, e.g. 1001
        """
        return self._default_head_in

    @property
    def default_tail_out(self):
        """
        Return the default tail out value, computed from new cut values, or None
        """
        new_tail_duration = self.new_tail_duration
        if new_tail_duration is None:
            return None
        new_cut_out = self.new_cut_out
        if new_cut_out is None:
            return None
        return new_cut_out + new_tail_duration

    @property
    def shot_head_in(self):
        """
        Return the head in value from associated shot, or None
        """
        if self._sg_shot:
            if self._use_smart_fields:
                return self._sg_shot.get("smart_head_in")
            return self._sg_shot.get("sg_head_in")
        return None

    @property
    def shot_tail_out(self):
        """
        Return the tail out value from associated shot, or None
        """
        if self._sg_shot:
            if self._use_smart_fields:
                return self._sg_shot.get("smart_tail_out")
            return self._sg_shot.get("sg_tail_out")
        return None

    @property
    def head_in(self):
        """
        Return the current head in from the associated cut item, or None
        """
        if self._sg_cut_item:
            return self._sg_cut_item.get("sg_head_in")
        return None

    @property
    def new_head_in(self):
        """
        Return the new head in value
        """
        nh = self.shot_head_in
        if nh is None:
            nh = self.default_head_in
        return nh

    @property
    def tail_out(self):
        """
        Return the current tail out value from the associated cut item, or None
        """
        if self._sg_cut_item:
            return self._sg_cut_item.get("sg_tail_out")
        return None

    @property
    def new_tail_out(self):
        """
        Return the new tail out value
        """
        nt = self.shot_tail_out
        if nt is None:
            nt = self.default_tail_out
        return nt

    @property
    def cut_in(self):
        """
        Return the current cut in value from the associated cut item, or None
        """
        if self._sg_cut_item:
            return self._sg_cut_item["sg_cut_in"]
        return None

    @property
    def cut_out(self):
        """
        Return the current cut out value from the associated cut item, or None
        """
        if self._sg_cut_item:
            return self._sg_cut_item["sg_cut_out"]
        return None

    @property
    def cut_order(self):
        """
        Return the current cut order value from the associated cut item, 
        or associated shot, or None
        """
        if self._sg_cut_item:
            return self._sg_cut_item["sg_cut_order"]
        if self._sg_shot:
            return self._sg_shot["sg_cut_order"]
        return None

    @property
    def new_cut_order(self):
        """
        Return the new cut order value from the associated EditEvent, or None
        """
        if self._edit:
            return self._edit.id
        return None

    @property
    def new_cut_in(self):
        """
        Return the new cut in value, or None
        """
        if not self._edit:
            return None
        new_head_in = self.shot_head_in
        if new_head_in is None:
            new_head_in = self.default_head_in
        if self._sg_cut_item:
            head_in = self.head_in
            cut_in = self._sg_cut_item["sg_cut_in"]
            tc_cut_in = edl.Timecode(self._sg_cut_item["sg_timecode_cut_in"], self._sg_cut_item["sg_fps"])
            if cut_in is not None and tc_cut_in is not None:
                offset = self._edit.source_in.to_frame() - tc_cut_in.to_frame()
                offset += new_head_in - head_in
                return cut_in + offset
# new_cut_in = cut_item.cut_in + ( shot_head_in or default head_in ) - cut_item.head_in + edl.tc_cut_in - cut_item.tc_cut_in
        head_in = self.shot_head_in
        if head_in is None:
            head_in = self.default_head_in
        return self.default_head_in + self._default_head_in_duration

    @property
    def new_cut_out(self):
        """
        Return the new cut out value, or None
        """
        cut_in = self.new_cut_in
        if cut_in is None:
            return None
        if self._edit:
            offset = self.shot_head_in
            if offset is None:
                offset = self.default_head_in
            return cut_in + self._edit.source_duration -1
        return None

    @property
    def head_duration(self):
        """
        Return the current head duration, or None
        """
        if not self._sg_cut_item:
            return None
        cut_in = self._sg_cut_item["sg_cut_in"]
        head_in = self._sg_cut_item["sg_head_in"]
        if cut_in is None or head_in is None:
            return None
        return cut_in - head_in

    @property
    def new_head_duration(self):
        """
        Return the new head duration, or None
        """
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
        """
        Return the current duration from the associated cut item, or None
        """
        if self._sg_cut_item:
            return self._sg_cut_item["sg_cut_duration"]
        return None

    @property
    def new_duration(self):
        """
        Return the new duration, or None
        """
        if self._edit:
            return self._edit.source_duration
        return None

    @property
    def tail_duration(self):
        """
        Return the current tail duration, or None
        """
        if not self._sg_cut_item:
            return None
        cut_out = self._sg_cut_item["sg_cut_out"]
        tail_out = self._sg_cut_item["sg_tail_out"]
        if cut_out is None or tail_out is None:
            return None
        return  tail_out - cut_out

    @property
    def new_tail_duration(self):
        """
        Return the new tail duration, or None
        """
        cut_out = self.new_cut_out
        if cut_out is None:
            return None
        tail_out = self.shot_tail_out
        if tail_out is None:
            return self._app.get_setting("default_tail_out_duration")
        if self._edit:
            return tail_out - cut_out
        return None

    @property
    def diff_type(self):
        """
        Return the CutDiff type of this cut difference
        """
        return self._diff_type

    @property
    def diff_type_label(self):
        """
        Return a display string for the CutDiff type of this cut difference
        """
        return self.get_diff_type_label(self._diff_type)

    @property
    def reasons(self):
        """
        Return a list of reasons strings for this cut difference.
        Return an empty list for any difference which is not
        a CUT_CHANGE or a RESCAN
        """
        return self._cut_changes_reasons

    @property
    def need_rescan(self):
        """
        Return true if this cut change implies a rescan
        """
        return self._diff_type == _DIFF_TYPES.RESCAN

    @property
    def repeated(self):
        """
        Return true if the associated shot appears more than once in the 
        cut summary
        """
        return self._repeated

    def check_changes(self):
        """
        Set the cut difference type for this cut difference
        """
        self._diff_type = _DIFF_TYPES.NO_CHANGE
        self._cut_changes_reasons = []
        # The type of difference we are dealing with
        if not self._sg_shot:
            self._diff_type = _DIFF_TYPES.NEW
            return
        if not self._edit:
            self._diff_type = _DIFF_TYPES.OMITTED
            return
        # We have both a shot and an edit
        omit_statuses = self._app.get_setting("omit_statuses") or []
        if self._sg_shot["sg_status_list"] in omit_statuses:
            self._diff_type = _DIFF_TYPES.REINSTATED
            return
        # Check if we have a difference
        # If any of the previous value is not set, then assume all changed ( initial import )
        if self.cut_order is None or self.cut_in is None or self.cut_out is None or\
            self.head_duration is None or self.tail_duration is None or self.duration is None:
                self._diff_type = _DIFF_TYPES.CUT_CHANGE
                return

        if self.new_cut_order != self.cut_order:
            self._diff_type = _DIFF_TYPES.CUT_CHANGE
            self._cut_changes_reasons.append("Cut order changed from %d to %d" % (self.cut_order, self.new_cut_order))

        # Check if some rescan is needed
        if self.new_head_in < self.head_in or self.new_head_duration < 0:
            self._diff_type = _DIFF_TYPES.RESCAN
            self._cut_changes_reasons.append("Head extended %d frs" % (self.cut_in-self.new_cut_in))

        if self.new_tail_out > self.tail_out or self.new_tail_duration < 0:
            self._diff_type = _DIFF_TYPES.RESCAN
            self._cut_changes_reasons.append("Tail extended %d frs" % (self.new_cut_out-self.cut_out))

        # Cut changes which does not imply a rescan
        if self._diff_type != _DIFF_TYPES.RESCAN:
            if self.new_head_duration != self.head_duration:
                self._diff_type = _DIFF_TYPES.CUT_CHANGE
                diff = self.new_head_duration-self.head_duration
                if diff > 0:
                    self._cut_changes_reasons.append("Head extended %d frs" % diff)
                else:
                    self._cut_changes_reasons.append("Head trimmed %d frs" % -diff)
            if self.new_tail_duration != self.tail_duration:
                self._diff_type = _DIFF_TYPES.CUT_CHANGE
                diff = self.new_tail_duration-self.tail_duration
                if diff > 0:
                    self._cut_changes_reasons.append("Tail extended %d frs" % diff)
                else:
                    self._cut_changes_reasons.append("Tail trimmed %d frs" % -diff)
    
    def set_repeated(self, val):
        """
        Set this cut difference as repeated
        """
        self._repeated = val