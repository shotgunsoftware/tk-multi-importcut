# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk
# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
from sgtk.platform.qt import QtCore

# Different frame mapping modes
from .constants import _ABSOLUTE_MODE, _AUTOMATIC_MODE, _RELATIVE_MODE

# Import the EDL framework
edl = sgtk.platform.import_framework("tk-framework-editorial", "edl")


# Define difference types as enums
def diff_types(**enums):
    return type("CutDiffType", (), enums)

# Values for CutDiff types
_DIFF_TYPES = diff_types(
    NEW=0,              # A new Shot will be created
    OMITTED=1,          # The Shot is not part of the cut anymore
    REINSTATED=2,       # The Shot is back in the cut
    RESCAN=3,           # A rescan will be needed with the new in / out points
    CUT_CHANGE=4,       # Some values changed, but don't fall in previous categories
    NO_CHANGE=5,        # Values are identical to previous ones
    NO_LINK=6,          # Related Shot name couldn't be found
    NEW_IN_CUT=7,       # A new Shot entry is added, but the Shot already exists
    OMITTED_IN_CUT=8,   # A repeated Shot entry was removed
)

# Display names for cut diff types
_DIFF_LABELS = {
    _DIFF_TYPES.NEW: "New",
    _DIFF_TYPES.OMITTED: "Omitted",
    _DIFF_TYPES.REINSTATED: "Reinstated",
    _DIFF_TYPES.RESCAN: "Rescan Needed",
    _DIFF_TYPES.CUT_CHANGE: "Cut Change",
    _DIFF_TYPES.NO_CHANGE: "",
    _DIFF_TYPES.NO_LINK: "",
    _DIFF_TYPES.NEW_IN_CUT: "New in Cut",
    _DIFF_TYPES.OMITTED_IN_CUT: "Omitted",
}


class CutDiff(QtCore.QObject):
    """
    A class to retrieve differences between a previous Cut and a new one.

    A Cut difference is based on :
    - An EDL entry: a line from an EDL file
    - A Shotgun CutItem: a previously registered cut value for an EDL entry
    - A Shotgun Shot: Corresponding Shot in Shotgun

    At least one of them needs to be set. A CutDiff is able to retrieve
    previous cut values and compute new values, from the EDL entry ( a line
    in the EDL file ) and the CutItem ( previous value registered in SG ).

    The schema below shows values which are retrieved, mapping time code values
    to frame values.

                        tc cut in               tc cut out
        -----------------------------------------------------------------
        |<- head duration ->|<-      duration     ->|<- tail duration ->|
        |                   |                       |                   |
        -----------------------------------------------------------------
     head in              cut in                 cut out             tail out

    If a Shot is repeated, that is, appears more than once in the cut (e.g. for
    flashback effects ), a single "media item" is associated with all the entries
    linked to this shot. All frame values are relative to the earliest entry
    head in value.
        --------------------------
        |       instance 1       |
        --------------------------
        ^   --------------------
        |   |   instance 2     |
            --------------------
        |  ---------------------------------
           |      instance 3               |
        |  ---------------------------------
                                           ^
        |                                  |
        ------------------------------------
        |  media covering all instances    |
        ------------------------------------


    Some methods are provided to retrieve values from a previous import (if any)
    and the "new" values which will be used for the current import, allowing
    comparisons. The convention is to prefix these methods with "new_" when values
    for the current import are retrieved, and to not have a prefix for previous
    import values, e.g. cut_in and new_cut_in.

    Some values are stored at the Shot level, but needs to be computed if they are
    not already set on the Shot. Otherwise, previous values are typically retrieved
    from a linked CutItem (if any) and new values from the linked EditEvent (if any)
    """
    # Emitted when the (shot) name for this item is changed
    name_changed = QtCore.Signal(QtCore.QObject, str, str)
    # Emitted when the diff type for this item is changed
    type_changed = QtCore.Signal(QtCore.QObject, int, int)
    # Emitted when the repeated property for this item is changed
    repeated_changed = QtCore.Signal(QtCore.QObject, bool, bool)
    # Emitted when this CutDiff instance is discarded
    discarded = QtCore.Signal(QtCore.QObject)

    __default_timecode_frame_mapping = None

    def __init__(self, name, sg_shot=None, edit=None, sg_cut_item=None):
        """
        Instantiate a new Cut difference

        :param name: A name for this Cut difference, usually the Shot name
        :param sg_shot: An optional Shot dictionary, as retrieved from Shotgun
        :param edit: An optional EditEvent instance, retrieved from an EDL
        :param sg_cut_item: An optional CutItem dictionary, as retrieved from Shotgun
        """
        super(CutDiff, self).__init__()
        self._name = name
        self._sg_shot = sg_shot
        self._edit = edit
        self._sg_cut_item = sg_cut_item
        self._sg_version = None
        # Make a copy of SG Version so we can change it if needed, e.g. when
        # editing Shot name
        if self._sg_cut_item and self._sg_cut_item["version"]:
            self._sg_version = self._sg_cut_item["version"]
        elif self._edit:
            self._sg_version = self._edit.get_sg_version()

        # User settings for non-class methods
        self._user_settings = sgtk.platform.current_bundle().user_settings

        self._repeated = False
        self._diff_type = _DIFF_TYPES.NO_CHANGE
        self._cut_changes_reasons = []
        # The values coming back from retrieve here have been validated
        # by settings_dialog.py on their way in, so we should be good
        self._timecode_to_frame_mapping = self._user_settings.retrieve("timecode_to_frame_mapping")
        self._default_head_in = int(self._user_settings.retrieve("default_head_in"))
        self._default_head_in_duration = int(self._user_settings.retrieve("default_head_duration"))
        self._default_tail_out_duration = int(self._user_settings.retrieve("default_tail_duration"))
        self._use_smart_fields = self._user_settings.retrieve("use_smart_fields")

        # List of other entries for the same Shot
        self._siblings = None
        # Later we might want to allow users to edit the mapping, so
        # so let's make a copy of defaults in this instance
        self._timecode_frame_map = self.__default_timecode_frame_mapping
        # Retrieve the Cut diff type from the given params
        self._check_and_set_changes()

    @classmethod
    def get_diff_type_label(cls, diff_type):
        """
        Return a display name for the given cut diff type

        :param diff_type: A _DIFF_TYPES entry
        """
        return _DIFF_LABELS[diff_type]

    @classmethod
    def retrieve_default_timecode_frame_mapping(cls):
        """
        Read timecode to frame mapping user settings and store them at the class
        level.
        
        Three mapping modes are available, which are only relevant for first 
        imports:
        - Automatic: On first import, the timecode in is mapped to the Shot head in.
        - Absolute: On first import, timecode in is converted to an absolute frame
                    number.
        - Relative: On first import, timecode in is converted to an arbitrary frame
                    number specified through settings.

        Subsequent imports for all modes compute an offset between the previous 
        timecode in and the new one, and apply this offset to the previous Cut
        in value to compute the new cut in. This allows to change the mapping mode
        without affecting existing imported Cuts. Users have the ability to import
        Cuts without comparing to an existing one, which acts as an initial import.
        So, if needed, they can change the mapping mode by just ignoring previous
        imports.
        """
        user_settings = sgtk.platform.current_bundle().user_settings
        timecode_to_frame_mapping = user_settings.retrieve("timecode_to_frame_mapping")
        default_frame_rate = float(user_settings.retrieve("default_frame_rate"))
        if timecode_to_frame_mapping == _ABSOLUTE_MODE:
            # if we're in absolute mode, we need to reset our tc/frame values to 0
            cls.__default_timecode_frame_mapping = (
                edl.Timecode("00:00:00:00", fps=default_frame_rate), 0)
        elif timecode_to_frame_mapping == _RELATIVE_MODE:
            # the values from users settings are only used in relative mode
            timecode_mapping = user_settings.retrieve("timecode_mapping")
            frame_mapping = int(user_settings.retrieve("frame_mapping"))
            cls.__default_timecode_frame_mapping = (
                edl.Timecode(timecode_mapping, fps=default_frame_rate), frame_mapping)
        elif timecode_to_frame_mapping == _AUTOMATIC_MODE:
            default_head_in = int(user_settings.retrieve("default_head_in"))
            cls.__default_timecode_frame_mapping = (None, default_head_in)

    def get_matching_score(self, other):
        """
        Compares this CutDiff with the other and returns a matching score, based
        on:
        - Similar cut order
        - Similar timecode cut in
        - Similar timecode cut out

        :returns: An integer, the higher the
        """
        # A CutDiff always has either a CutItem or an edit event, so if one is
        # available, the other will be. Edit events contain new values, so we
        # use them if available and fall back on CutItem values
        if self._edit:
            cut_order = self._edit.id
            cut_in = self._edit.source_in
            cut_out = self._edit.source_out
        else:
            cut_order = self._sg_cut_item["cut_order"]
            cut_in = edl.Timecode(
                    self._sg_cut_item["timecode_cut_item_in_text"],
                    self._sg_cut_item["cut.Cut.fps"]
                ).to_frame()
            cut_out = edl.Timecode(
                    self._sg_cut_item["timecode_cut_item_out_text"],
                    self._sg_cut_item["cut.Cut.fps"]
                ).to_frame()

        if other._edit:
            other_cut_order = other._edit.id
            other_cut_in = other._edit.source_in
            other_cut_out = other._edit.source_out
        else:
            other_cut_order = other._sg_cut_item["cut_order"]
            other_cut_in = edl.Timecode(
                    other._sg_cut_item["timecode_cut_item_in_text"],
                    other._sg_cut_item["cut.Cut.fps"]
                ).to_frame()
            other_cut_out = edl.Timecode(
                    other._sg_cut_item["timecode_cut_item_out_text"],
                    other._sg_cut_item["cut.Cut.fps"]
                ).to_frame()
        score = 0
        if cut_order - other_cut_order == 0:
            score += 1
        if cut_in - other_cut_in == 0:
            score += 1
        if cut_out - other_cut_out == 0:
            score += 1
        return score

    @property
    def sg_shot(self):
        """
        Return the Shotgun Shot for this diff, if any

        :returns: A SG Shot dictionary or None
        """
        return self._sg_shot

    def set_sg_shot(self, sg_shot):
        """
        Set the SG Shot associated with this CutDiff

        :param sg_shot: A SG Shot dictionary, or None
        """
        self._sg_shot = sg_shot

    @property
    def sg_cut_item(self):
        """
        Return the Shotgun CutItem for this diff, if any

        :returns: A SG CutItem dictionary or None
        """
        return self._sg_cut_item

    def set_sg_cut_item(self, sg_cut_item):
        """
        Set the SG CutItem for this CutDiff

        :param sg_cut_item: A SG CutItem dictionary or None
        """
        self._sg_cut_item = sg_cut_item

    @property
    def edit(self):
        """
        Return the EditEntry for this diff, if any

        :returns: An EditEvent or None
        """
        return self._edit

    @property
    def name(self):
        """
        Return the name of this diff

        :returns: A string
        """
        return self._name

    @property
    def is_name_editable(self):
        """
        Return True if the name for this instance can be changed

        :returns: True if the name is editable, False otherwise
        """
        # We can only change names coming from an edit entry
        if not self._edit:
            return False
        # And only if there is no Version linked to it
        if self.sg_version:
            return False
        return True

    def set_name(self, name):
        """
        Set a new name for this cut diff

        :param name: A string
        :raises: RuntimeError if the name is not editable
        """
        if name == self._name:
            return
        if not self.is_name_editable:
            raise RuntimeError("Attempting to change a read only name")
        # if we changed the Shot name, it means that we :
        # - need to check the sg_shot we are linked to
        # - need to check the sg_cutitem we are linked to
        # - need to check the new diff type
        # - need to check if Shots are repeated or not
        self.name_changed.emit(self, self._name, name)
        self._name = name

    @property
    def version_name(self):
        """
        Return the Version name for this diff, if any. The Version name can come
        from a linked Version, or from a name extracted from the EDL edit

        :returns: A string or None
        """
        if self._sg_version:
            return self._sg_version["code"]
        if self._edit:
            return self._edit.get_version_name()
        return None

    @property
    def sg_version(self):
        """
        Return the Shotgun Version for this diff, if any

        :returns: A SG Version dictionary or None
        """
        return self._sg_version

    def set_sg_version(self, sg_version):
        """
        Set the Shotgun Version associated with this diff

        :param sg_version: A SG Version, as a dictionary
        """
        self._sg_version = sg_version

    @property
    def computed_tail_out(self):
        """
        Return a tail out value, computed from new cut values, or None

        Usually the tail out value is retrieved from the linked Shot, however,
        if this value is not set, a value must be computed which will be set
        on the Shot on import

        :returns: An integer or None
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

        :returns: An integer or None
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

        :returns: An integer or None
        """
        if self._sg_shot:
            if self._use_smart_fields:
                return self._sg_shot.get("smart_tail_out")
            return self._sg_shot.get("sg_tail_out")
        return None

    @property
    def new_head_in(self):
        """
        Return the new head in value

        :returns: An integer
        """
        # If we don't have any edit entry, then we don't have
        # any new head in by definition
        if not self._edit:
            return None

        # Special case if we are dealing with a repeated Shot:
        # Frames are relative to the earliest entry in our siblings
        # If we don't have any edit we don't need to do it and the
        # earliest entry might be None, as it is based on tc cut in,
        # and this is not defined without edits
        if self.repeated:
            # Get the head in for the earliest entry
            earliest = self._siblings.earliest
            if not earliest:
                raise ValueError(
                    "%s is repeated but does not have an earliest entry defined" % self)
            if earliest != self:  # We are not the earliest
                return earliest.new_head_in
        # If we don't have a previous entry, we need to retrieve the initial value
        # Default case: retrieve the value from the Shot or fall back to the default
        nh = self.shot_head_in
        if nh is None:
            if self._timecode_to_frame_mapping != _AUTOMATIC_MODE:  # Explicit timecode
                base_tc = self._timecode_frame_map[0]
                base_frame = self._timecode_frame_map[1]
                cut_in = self.new_tc_cut_in.to_frame() - base_tc.to_frame() + base_frame
                nh = cut_in - self._default_head_in_duration
            else:
                # Use the frame number as default head in
                nh = self._timecode_frame_map[1]
        return nh

    @property
    def new_tail_out(self):
        """
        Return the new tail out value

        :returns: An integer
        """
        nt = self.shot_tail_out
        if nt is None:
            nt = self.computed_tail_out
        return nt

    @property
    def cut_in(self):
        """
        Return the current cut in value for the Shot linked to the associated
        CutItem, or None.

        :returns: An integer or None
        """
        if self._sg_cut_item:
            return self._sg_cut_item["cut_item_in"]
        if self._sg_shot:
            # If repeated and we are not the first entry, we
            # need to compute an offset from first entry
            if self.repeated:
                earliest = self._siblings.earliest
                if not earliest:
                    raise ValueError(
                        "%s is repeated but does not have an earliest entry defined" % self)
                # If we are the earliest, we will fall back to the default case below
                if earliest != self:  # We are not the earliest
                    # get its tc_cut_in
                    earliest_tc_cut_in = self._siblings.min_tc_cut_in
                    if earliest_tc_cut_in is None:
                        raise ValueError(
                            "Earliest %s is not able to compute tc cut in" % earliest_tc_cut_in
                        )
                    # Compute the difference with ours
                    offset = self.new_tc_cut_in.to_frame() - earliest_tc_cut_in.to_frame()
                    # add it the earliest head in
                    return self._siblings.min_cut_in + offset
            # Default case if not repeated or first entry
            if self._use_smart_fields:
                return self._sg_shot.get("smart_cut_in")
            return self._sg_shot["sg_cut_in"]
        return None

    @property
    def tc_cut_in(self):
        """
        Return the timecode associated with the current cut in value from the
        associated CutItem, or None

        :returns: A Timecode instance or None
        """
        if self._sg_cut_item:
            return edl.Timecode(
                self._sg_cut_item["timecode_cut_item_in_text"],
                self._sg_cut_item["cut.Cut.fps"]
            )
        return None

    @property
    def tc_cut_out(self):
        """
        Return the timecode associated with the current cut out value from the
        associated CutItem, or None

        :returns: A Timecode instance or None
        """
        if self._sg_cut_item:
            return edl.Timecode(
                self._sg_cut_item["timecode_cut_item_out_text"],
                self._sg_cut_item["cut.Cut.fps"]
            )
        return None

    @property
    def cut_out(self):
        """
        Return the current cut out value for the Shot linked to the associated
        CutItem, or None.

        :returns: An integer or None
        """
        if self._sg_cut_item:
            return self._sg_cut_item["cut_item_out"]
        if self._sg_shot:
            if self.repeated:
                last = self._siblings.last
                if not last:
                    raise ValueError(
                        "%s is repeated but does not have a last entry defined" % self
                    )
                # If we are the last, we will fall back to the default case below
                if last != self:  # We are not the last
                    # get its tc_cut_out
                    last_tc_cut_out = self._siblings.max_tc_cut_out
                    if last_tc_cut_out is None:
                        raise ValueError(
                            "Last %s is not able to compute tc cut out" % last_tc_cut_out
                        )
                    # Compute the difference with ours
                    offset = self.new_tc_cut_out.to_frame() - last_tc_cut_out.to_frame()
                    # add it the earliest head in
                    return self._siblings.max_cut_out + offset
            # Default: not repeated or last entry
            if self._use_smart_fields:
                return self._sg_shot.get("smart_cut_out")
            return self._sg_shot["sg_cut_out"]
        return None

    @property
    def cut_order(self):
        """
        Return the current cut order value from the associated CutItem,
        or associated shot, or None

        :returns: An integer or None
        """
        if self._sg_cut_item:
            return self._sg_cut_item["cut_order"]
        if self._sg_shot:
            return self._sg_shot["sg_cut_order"]
        return None

    @property
    def new_cut_order(self):
        """
        Return the new cut order value from the associated EditEvent, or None

        :returns: An integer or None
        """
        if self._edit:
            return self._edit.id
        return None

    @property
    def new_cut_in(self):
        """
        Return the new cut in value, or None

        :returns: An integer or None
        """
        # If we don't have any edit entry, then we don't have
        # any new cut in by definition
        if not self._edit:
            return None
        if self._sg_cut_item:
            cut_in = self._sg_cut_item["cut_item_in"]
            tc_cut_in = self.tc_cut_in
            if cut_in is not None and tc_cut_in is not None:
                # Calculate the cut offset
                offset = self._edit.source_in.to_frame() - tc_cut_in.to_frame()
                # Just apply the offset to the old cut in
                return cut_in + offset
        # If we don't have a previous CutItem, we can't just compute an offset
        # from the previous cut values, so we need to compute brand new values
        # If repeated, our cut in is relative to the earliest entry
        if self.repeated:
            # Get the head in for the earliest entry
            earliest = self._siblings.earliest
            if not earliest:
                raise ValueError(
                    "%s is repeated but does not have an earliest entry defined" % self)
            # If we are the earliest, we will fall back to the default case below
            if earliest != self:  # We are not the earliest
                # get its tc_cut_in
                earliest_tc_cut_in = self._siblings.min_tc_cut_in
                if earliest_tc_cut_in is None:
                    raise ValueError(
                        "Earliest %s is not able to compute tc cut in" % earliest_tc_cut_in)
                # Compute the difference with ours
                offset = self.new_tc_cut_in.to_frame() - earliest_tc_cut_in.to_frame()
                # add it the earliest head in
                return self._siblings.min_cut_in + offset
        # Not repeated or earliest entry case
        # If we don't have a previous entry, retrieve default values
        # and return an arbitrary value
        if self._timecode_frame_map[0] is not None:
            base_tc = self._timecode_frame_map[0]
            base_frame = self._timecode_frame_map[1]
            cut_in = self.new_tc_cut_in.to_frame() - base_tc.to_frame() + base_frame
            return cut_in
        else:
            head_in = self.new_head_in
            head_duration = self._default_head_in_duration
            return head_in + head_duration

    @property
    def new_tc_cut_in(self):
        """
        Return the new timecode cut in, or None.

        The new value is retrieved from the Edit source timecode in, if there is
        an Edit.

        :returns: A Timecode instance or None
        """
        # If we don't have any edit entry, then we don't have
        # any new tc cut in by definition
        if not self._edit:
            return None
        return self._edit.source_in

    @property
    def new_cut_out(self):
        """
        Return the new cut out value, or None

        :returns: An integer or None
        """
        cut_in = self.new_cut_in
        if cut_in is None:
            return None
        if self._edit:
            return cut_in + self._edit.source_duration - 1
        return None

    @property
    def new_tc_cut_out(self):
        """
        Return the new timecode cut out, or None.
        The new value is retrieved from the edit source timecode out,
        if there is an edit.

        :returns: A Timecode instance or None
        """
        # If we don't have any edit entry, then we don't have
        # any new tc cut in by definition
        if not self._edit:
            return None
        return self._edit.source_out

    @property
    def head_duration(self):
        """
        Return the current head duration, or None

        :returns: An integer or None
        """
        if self.cut_in is None or self.shot_head_in is None:
            return None
        # Shot head_out would be cut_in -1, so head_duration would be:
        # cut_in -1 - head_in + 1, we use a simplified formula below
        return self.cut_in - self.shot_head_in

    @property
    def new_head_duration(self):
        """
        Return the new head duration, or None

        :returns: An integer or None
        """
        if self._edit:
            new_cut_in = self.new_cut_in
            if new_cut_in is None:
                return None
            head_in = self.new_head_in
            if head_in is None:
                return None
            # head_out would be cut_in -1, so head_duration would be:
            # cut_in -1 - head_in + 1, we use a simplified formula below
            return new_cut_in - head_in
        return None

    @property
    def duration(self):
        """
        Return the current duration from the associated CutItem, or None

        :returns: An integer or None
        """
        if self._sg_cut_item:
            return self._sg_cut_item["cut_item_duration"]
        if self.cut_in is not None and self.cut_out is not None:
            return self.cut_out - self.cut_in + 1
        else:
            return None

    @property
    def new_duration(self):
        """
        Return the new duration, or None

        :returns: An integer or None
        """
        if self._edit:
            return self._edit.source_duration
        return None

    @property
    def tail_duration(self):
        """
        Return the current tail duration, or None

        :returns: An integer or None
        """
        if self.cut_out is None or self.shot_tail_out is None:
            return None
        # tail_in would be cut_out + 1, so tail_duration would be
        # tail_out - (cut_out + 1) -1, we use a simplified formula below
        return self.shot_tail_out - self.cut_out

    @property
    def new_tail_duration(self):
        """
        Return the new tail duration, or None

        :returns: An integer or None
        """
        if not self._edit:  # No new value
            return None
        cut_out = self.new_cut_out
        if cut_out is None:
            return None
        tail_out = self.shot_tail_out
        if tail_out is None:
            # Special case if we have an edit and are repeated
            # if we don't have an edit, the new_tail_duration is irrelevant
            if self._edit and self.repeated:
                last = self._siblings.last
                if not last:
                    raise ValueError("Couldn't get last entry for repeated Shot %s" % self)
                if last != self:
                    # If this is not the last entry
                    tail_out = last.new_tail_out
        if tail_out is None:
            # Fallback to defaults
            return self._default_tail_out_duration
        # tail_in would be cut_out + 1, so tail_duration would be
        # tail_out - (cut_out + 1) -1, we use a simplified formula below
        return tail_out - cut_out

    @property
    def diff_type(self):
        """
        Return the CutDiff type of this cut difference

        :returns: A _DIFF_TYPES
        """
        return self._diff_type

    @property
    def diff_type_label(self):
        """
        Return a display string for the CutDiff type of this cut difference

        :returns: A string
        """
        return self.get_diff_type_label(self._diff_type)

    @property
    def reasons(self):
        """
        Return a list of reasons strings for this cut difference.

        Return an empty list for any diff_type that is not
        a CUT_CHANGE or a RESCAN

        :returns: A possibly empty list of strings
        """
        return self._cut_changes_reasons

    @property
    def need_rescan(self):
        """
        Return True if this cut change implies a rescan

        :returns: True if a rescan is needed, False otherwise
        """
        return self._diff_type == _DIFF_TYPES.RESCAN

    @property
    def repeated(self):
        """
        Return true if the associated Shot appears more than once in the
        cut summary

        :returns: True if the Shot is repeated, False otherwise
        """
        # We use an explicit flag for repeated Shots and don't rely
        # on the self._siblings list containing more then one entry
        # as this is controlled by the cut summary and can be changed
        # without us being notified. The cut summary will call set_repeated
        # explicitly when changing our flag, giving us a chance to compare the
        # new value with the old one.
        return self._repeated

    @property
    def is_vfx_shot(self):
        """
        Return True if this item is linked to a VFX Shot

        :returns: True if a Vfx Shot, False otherwise
        """
        # Non vfx Shots are not handled in SG by our current clients so, for the
        # time being, just check if the item is linked to a Shot.
        # If not, then this is not a VFX Shot entry.
        if self._sg_shot:
            # Later we might want to do additional checks on the linked Shot
            return True
        if not self._edit:
            # If we don't have an edit entry we should always have a sg_shot
            # coming from the linked Entity
            return True
        # Return True if the edit has a Shot name
        return bool(self._name)

    def set_siblings(self, siblings):
        """
        Set our list of siblings, which is other entries for the same Shot

        :param siblings: a ShotCutDiffList or None
        """
        self._siblings = siblings

    def is_earliest(self):
        """
        Return True if this CutDiff is the earliest in repeated shots.
        If the Shot is not repeated, this entry is the earliest.

        :returns: True of False
        """
        if not self._siblings:
            return True
        if self._siblings.earliest == self:
            return True
        return False

    @property
    def interpreted_diff_type(self):
        """
        Some difference types are grouped under a common type to deal with repeated
        Shots. Invididual entries can be flagged as NEW_IN_CUT or OMITTED_IN_CUT.

        - If all entries for a given Shot are OMITTED_IN_CUT, then the Shot is
        OMITTED, and this is the returned type. Otherwise it is just a CUT_CHANGE.

        - NEW_IN_CUT is different, even if all entries for a Shot are NEW_IN_CUT,
        if a Shot exists it is not NEW. Individual entries will be set to NEW if
        the Shot does not exist in Shotgun.

        Other cases fall back to the actual diff type.

        :returns: A _DIFF_TYPES
        """
        # Please note that a loop is done over all siblings, so this must be used
        # with care as it can be inefficient
        if self.diff_type == _DIFF_TYPES.OMITTED_IN_CUT and self.repeated:
            # Check if all our siblings are omitted_in_cut as well
            all_omitted = all(x._diff_type == _DIFF_TYPES.OMITTED_IN_CUT for x in self._siblings)
            if all_omitted:
                return _DIFF_TYPES.OMITTED

        if self.diff_type in [_DIFF_TYPES.NEW_IN_CUT, _DIFF_TYPES.OMITTED_IN_CUT]:
            return _DIFF_TYPES.CUT_CHANGE
        # Fall back to reality!
        return self.diff_type

    def check_and_set_changes(self):
        """
        Set the cut difference type for this cut difference
        Emit a type_changed if the value changed
        """
        old_type = self._diff_type
        self._check_and_set_changes()
        if old_type != self._diff_type:
            self.type_changed.emit(self, old_type, self._diff_type)

    def _check_and_set_changes(self):
        """
        Set the cut difference type for this cut difference.
        """
        self._diff_type = _DIFF_TYPES.NO_CHANGE
        self._cut_changes_reasons = []
        # The type of difference we are dealing with.
        if not self.name:
            self._diff_type = _DIFF_TYPES.NO_LINK
            return
        if not self._sg_shot:
            self._diff_type = _DIFF_TYPES.NEW
            return

        if not self._edit:
            if not self.repeated:
                self._diff_type = _DIFF_TYPES.OMITTED
            else:
                self._diff_type = _DIFF_TYPES.OMITTED_IN_CUT
            return
        # We have both a Shot and an edit.
        omit_statuses = self._user_settings.retrieve("reinstate_shot_if_status_is") or []
        if self._sg_shot["sg_status_list"] in omit_statuses:
            self._diff_type = _DIFF_TYPES.REINSTATED
            return

        # This cut_item hasn't appeared in previous Cuts.
        if not self._sg_cut_item:
            self._diff_type = _DIFF_TYPES.NEW_IN_CUT
            return

        # Check if we have a difference.
        # If any of the previous values are not set, then assume they all changed
        # (initial import)
        if (self.cut_order is None or
            self.cut_in is None or
            self.cut_out is None or
            self.head_duration is None or
            self.tail_duration is None or
            self.duration is None):
                self._diff_type = _DIFF_TYPES.CUT_CHANGE
                return

        # note: leaving this in here in case we decide to switch back to the old behavior
        # if self.new_cut_order != self.cut_order:
        #     self._diff_type = _DIFF_TYPES.CUT_CHANGE
        #     self._cut_changes_reasons.append(
        #         "Cut order changed from %d to %d" % (self.cut_order, self.new_cut_order))

        # Check if some rescan is needed
        if self.new_head_in < self.shot_head_in:
            self._diff_type = _DIFF_TYPES.RESCAN
            self._cut_changes_reasons.append(
                "Head extended %d frs" % (self.shot_head_in - self.new_head_in))

        if self.new_head_duration < 0:
            self._diff_type = _DIFF_TYPES.RESCAN
            self._cut_changes_reasons.append(
                "Head extended %d frs" % (-self.new_head_duration + self.head_duration))

        if self.new_tail_out > self.shot_tail_out:
            self._diff_type = _DIFF_TYPES.RESCAN
            self._cut_changes_reasons.append(
                "Tail extended %d frs" % (self.new_tail_out - self.tail_out))

        if self.new_tail_duration < 0:
            self._diff_type = _DIFF_TYPES.RESCAN
            self._cut_changes_reasons.append(
                "Tail extended %d frs" % (-self.new_tail_duration + self.tail_duration))

        # Cut changes which does not imply a rescan
        if self._diff_type != _DIFF_TYPES.RESCAN:
            if self.new_head_duration != self.head_duration:
                self._diff_type = _DIFF_TYPES.CUT_CHANGE
                diff = self.new_head_duration-self.head_duration
                if diff > 0:
                    self._cut_changes_reasons.append("Head trimmed %d frs" % diff)
                else:
                    self._cut_changes_reasons.append("Head extended %d frs" % -diff)
            if self.new_tail_duration != self.tail_duration:
                self._diff_type = _DIFF_TYPES.CUT_CHANGE
                diff = self.new_tail_duration-self.tail_duration
                if diff > 0:
                    self._cut_changes_reasons.append("Tail trimmed %d frs" % diff)
                else:
                    self._cut_changes_reasons.append("Tail extended %d frs" % -diff)

    def set_repeated(self, repeated):
        """
        Set this cut difference as repeated

        :param repeated: A boolean
        """
        # This is set explicitly by the cut summary, so we have a chance to
        # compare the new value with the old one
        if repeated != self.repeated:
            old_repeated = self._repeated
            self._repeated = repeated
            self.repeated_changed.emit(self, old_repeated, self._repeated)
            # Cut in / out values are affected by repeated changes
            old_type = self._diff_type
            self._check_and_set_changes()
            if old_type != self._diff_type:
                self.type_changed.emit(self, old_type, self._diff_type)

    def summary(self):
        """
        Return a summary for this CutDiff instance as a tuple with :
         Shot details, Cut item details, Version details and Edit details

        :returns: A four entries tuple, where each entry is a potentially empty string
        """
        shot_details = ""
        if self.sg_shot:
            if self._use_smart_fields:
                shot_details = (
                    "Name : %s, Status : %s, Head In : %s, Cut In : %s, Cut Out : %s, "
                    "Tail Out : %s, Cut Order : %s" % (
                        self.sg_shot["code"],
                        self.sg_shot["sg_status_list"],
                        self.sg_shot["smart_head_in"],
                        self.sg_shot["smart_cut_in"],
                        self.sg_shot["smart_cut_out"],
                        self.sg_shot["smart_tail_out"],
                        self.sg_shot["sg_cut_order"],
                    )
                )
            else:
                shot_details = (
                    "Name : %s, Status : %s, Head In : %s, Cut In : %s, Cut Out : %s, "
                    "Tail Out : %s, Cut Order : %s" % (
                        self.sg_shot["code"],
                        self.sg_shot["sg_status_list"],
                        self.sg_shot["sg_head_in"],
                        self.sg_shot["sg_cut_in"],
                        self.sg_shot["sg_cut_out"],
                        self.sg_shot["sg_tail_out"],
                        self.sg_shot["sg_cut_order"],
                    )
                )
        cut_item_details = ""
        if self.sg_cut_item:
            fps = self.sg_cut_item["cut.Cut.fps"]
            tc_in = edl.Timecode(self.sg_cut_item["timecode_cut_item_in_text"], fps)
            tc_out = edl.Timecode(self.sg_cut_item["timecode_cut_item_out_text"], fps)
            cut_item_details = (
                "Cut Order %s, TC in %s, TC out %s, Cut In %s, Cut Out %s, Cut Duration %s" % (
                    self.sg_cut_item["cut_order"],
                    tc_in,
                    tc_out,
                    self.sg_cut_item["cut_item_in"],
                    self.sg_cut_item["cut_item_out"],
                    self.sg_cut_item["cut_item_duration"]
                )
            )
        version_details = ""
        sg_version = self.sg_version
        if sg_version:
            version_details = "%s, link %s %s" % (
                sg_version["code"],
                sg_version["entity"]["type"] if sg_version["entity"] else "None",
                sg_version["entity.Shot.code"] if sg_version["entity.Shot.code"] else "",
            )
        edit_details = str(self._edit) if self._edit else ""
        return shot_details, cut_item_details, version_details, edit_details
