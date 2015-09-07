# Copyright (c) 2015 Shotgun Software Inc.
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
_DIFF_TYPES = diff_types(
    NEW=0,              # A new shot will be created
    OMITTED=1,          # The shot is not part of the cut anymore
    REINSTATED=2,       # The shot is back in the cut
    RESCAN=3,           # A rescan will be needed with the new in / out points
    CUT_CHANGE=4,       # Some values changed, but don't fall in previous categories
    NO_CHANGE=5,        # Values are identical to previous ones
    NO_LINK=6,          # Related shot name couldn't be found
)
# Display names for cut diff types
_DIFF_LABELS = {
    _DIFF_TYPES.NEW : "New",
    _DIFF_TYPES.OMITTED : "Omitted",
    _DIFF_TYPES.REINSTATED : "Reinstated",
    _DIFF_TYPES.RESCAN : "Rescan Needed",
    _DIFF_TYPES.CUT_CHANGE : "Cut Change",
    _DIFF_TYPES.NO_CHANGE : "",
    _DIFF_TYPES.NO_LINK : "",
}

class CutDiff(QtCore.QObject):
    """
    A class to retrieve differences between a previous cut and a new one.

    A cut difference is based on :
    - An EDL entry : a line from an EDL file
    - A Shotgun cut item : a previously registered cut value for an EDL entry
    - A Shotgun shot : Corresponding shot in Shotgun

    At least one of them needs to be set. A CutDiff is able to retrieve
    previous cut values and compute new values, from the EDL entry ( a line
    in the EDL file ) and the cut item ( previous value registered in SG ).
    
    The schema below shows values which are retrieved, mapping time code values
    to frame values.

                        tc cut in               tc cut out
        -----------------------------------------------------------------
        |<- head duration ->|<-      duration     ->|<- tail duration ->|
        |                   |                       |                   |
        -----------------------------------------------------------------
     head in              cut in                 cut out             tail out

    If a shot is repeated, that is, appears more than once in the cut (e.g. for
    flashback effects ), a single "media" is associated with all the entries
    linked to this shot. All frames values are relative to the earliest entry
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

    """
    # Emitted when the (shot) name for this item is changed
    name_changed=QtCore.Signal(QtCore.QObject, str, str)
    # Emitted when the diff type for this item is changed
    type_changed=QtCore.Signal(QtCore.QObject, int, int)
    # Emitted when the diff type for this item is changed
    repeated_changed=QtCore.Signal(QtCore.QObject, bool, bool)
    # Emitted when this cut diff instance is discarded
    discarded=QtCore.Signal(QtCore.QObject)

    def __init__(self, name, sg_shot=None, edit=None, sg_cut_item=None):
        """
        Instantiate a new cut difference
        
        :param name: A name for this cut difference, usually the shot name
        :param sg_shot: An optional shot dictionary, as retrieved from Shotgun
        :param edit: An optional EditEvent instance, retrieved from an EDL
        :param sg_cut_item: An optional cut item dictionary, as retrieved from Shotgun
        """
        super(CutDiff, self).__init__()
        self._name = name
        self._sg_shot = sg_shot
        self._edit = edit
        self._sg_cut_item = sg_cut_item
        self._app = sgtk.platform.current_bundle()

        self._repeated = False
        self._diff_type = _DIFF_TYPES.NO_CHANGE
        self._cut_changes_reasons = []
        self._default_head_in = self._app.get_setting("default_head_in")
        self._default_head_in_duration = self._app.get_setting("default_head_in_duration")
        self._use_smart_fields = self._app.get_setting("use_smart_fields") or False

        self._siblings = None # List of other entries for the same shot
        # Retrieve the cut diff type from the given params
        self._check_changes()

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

    def set_sg_shot(self, sg_shot):
        """
        Set the SG shot associated with this CutDiff
        :param sg_shot: A SG shot dictionary, or None
        """
        self._sg_shot=sg_shot

    @property
    def sg_cut_item(self):
        """
        Return the Shotgun cut item for this diff, if any
        """
        return self._sg_cut_item

    def set_sg_cut_item(self, sg_cut_item):
        """
        Set the SG cut item for this CutDiff
        :param sg_cut_item: A SG CutItem dictionary or None
        """
        self._sg_cut_item=sg_cut_item

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
    def is_name_editable(self):
        """
        Return True if the name for this instance can be changed
        """
        # We can only change names coming from an edit entry
        if not self._edit:
            return False
        # And only if there is no version linked to it
        if self._sg_cut_item and self._sg_cut_item["sg_version.Version.code"]:
            return False
        return True

    def set_name(self, name):
        """
        Set a new name for this cut diff
        :param name: A string
        :raises: RuntimeError if the name is not editable
        """
        if name==self._name:
            return
        if not self.is_name_editable:
            raise RuntimeErrror("Attempting to change a read only name")
        # if we changed the shot name, it means that we :
        # - need to check the sg_shot we are linked to
        # - need to check the sg_cutitem we are linked to
        # - need to check the new diff type
        # - need to check if shots are repeated or not
        self.name_changed.emit(self, self._name, name)
        self._name=name

    @property
    def version_name(self):
        """
        Return the version name for this diff, if any
        """
        if self._edit:
            return self._edit.get_version_name()
        if self._sg_cut_item and self._sg_cut_item["sg_version.Version.code"]:
            return self._sg_cut_item["sg_version.Version.code"]
        return None

    @property
    def sg_version(self):
        """
        Return the Shotgun version for this diff, if any

        :returns: A SG Version dictionary or None
        """
        if self._edit:
            return self._edit.get_sg_version()
        if self._sg_cut_item and self._sg_cut_item["sg_version"]:
            return self._sg_cut_item["sg_version"]
        return None

    def set_sg_version(self, sg_version):
        """
        Set the Shotgun version associated with this diff

        :param sg_version: A SG version, as a dictionary
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
    def head_in(self):
        """
        Return the current head in from the associated cut item, or None

        :returns: An integer or None
        """
        if self._sg_cut_item:
            return self._sg_cut_item.get("sg_head_in")
        return None

    @property
    def new_head_in(self):
        """
        Return the new head in value
        """
        # Special case if we are dealing with a repeated shot
        # Frames are relative to the earliest entry in our siblings
        if self.repeated:
            # Get the head in for the earliest entry
            earliest = self._siblings.earliest
            if not earliest:
                raise ValueError("%s is repeated but does not have an earliest entry defined" % self)
            if earliest != self: # We are not the earliest
                return earliest.new_head_in
        # Default case : retrieve the value from the shot
        # or fall back to the default one
        nh = self.shot_head_in
        if nh is None:
            nh = self.default_head_in
        return nh

    @property
    def tail_out(self):
        """
        Return the current tail out value from the associated cut item, or None

        :returns: An integer or None
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

        :returns: An integer or None
        """
        if self._sg_cut_item:
            return self._sg_cut_item["sg_cut_in"]
        return None

    @property
    def tc_cut_in(self):
        """
        Return the timecode associated with the current cut in value from the
        associated cut item, or none

        :returns: A Timecode instance or None
        """
        if self._sg_cut_item:
            return edl.Timecode(
                self._sg_cut_item["sg_timecode_cut_in"],
                self._sg_cut_item["sg_fps"]
            )
        return None

    @property
    def cut_out(self):
        """
        Return the current cut out value from the associated cut item, or None

        :returns: An integer or None
        """
        if self._sg_cut_item:
            return self._sg_cut_item["sg_cut_out"]
        return None

    @property
    def cut_order(self):
        """
        Return the current cut order value from the associated cut item, 
        or associated shot, or None

        :returns: An integer or None
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
            head_in = self.head_in
            cut_in = self._sg_cut_item["sg_cut_in"]
            tc_cut_in = self.tc_cut_in
            if cut_in is not None and tc_cut_in is not None:
                # Calculate the cut offset
                offset = self._edit.source_in.to_frame() - tc_cut_in.to_frame()
                # Just apply the offset to the old cut in
                return cut_in + offset
        # If repeated our cut in is relative to the earliest entry
        if self.repeated:
            # Get the head in for the earliest entry
            earliest = self._siblings.earliest
            if not earliest:
                raise ValueError("%s is repeated but does not have an earliest entry defined" % self)
            if earliest != self: # We are not the earliest
                # get its tc_cut_in
                earliest_tc_cut_in = earliest.new_tc_cut_in
                if earliest_tc_cut_in is None:
                    raise ValueError("Earliest %s is not able to compute tc cut in" % earliest_tc_cut_in)
                # Compute the difference with ours
                offset = self.new_tc_cut_in.to_frame() - earliest_tc_cut_in.to_frame()
                # add it the earliest head in
                return earliest.new_cut_in + offset
        # If we don't have a previous entry, retrieve default values
        # and return an arbitrary value
        head_in = self.new_head_in
        head_duration = self._default_head_in_duration
        return head_in + head_duration

    @property
    def new_tc_cut_in(self):
        """
        Return the new timecode cut in, or None.
        The new value is retrieved from the edit source timecode in,
        if there is an edit.

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
            return cut_in + self._edit.source_duration -1
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

        :returns: An integer or None
        """
        if self._edit:
            new_cut_in = self.new_cut_in
            if new_cut_in is None:
                return None
            head_in = self.new_head_in
            if head_in is None:
                return None
            return new_cut_in - head_in
        return None

    @property
    def duration(self):
        """
        Return the current duration from the associated cut item, or None

        :returns: An integer or None
        """
        if self._sg_cut_item:
            return self._sg_cut_item["sg_cut_duration"]
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

        :returns: An integer or None
        """
        if not self._edit: # No new value
            return None
        cut_out = self.new_cut_out
        if cut_out is None:
            return None
        tail_out = self.shot_tail_out
        if tail_out is None:
            if self.repeated:
                latest = self._siblings.latest
                if not latest:
                    raise ValueError("Couldn't get latest entry for repeated shot %s" % self)
                if latest != self:
                    # If we are not ourself the latest entry
                    tail_out = latest.new_tail_out
        if tail_out is None:
            # Fallback to defaults
            return self._app.get_setting("default_tail_out_duration")
        return tail_out - cut_out

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
#        if not self._siblings or len(self._siblings) < 2:
#            return False
#        return True
        # We use an explicit flag for repeated shots and don't rely
        # on the self._siblings list containing more then one entry
        # as this is controlled by the cut summary and can be changed
        # without us being notified. The cut summary will call set_repeated
        # explicitely when changing our flag, giving us a chance to compare the
        # new value with the old one.
        return self._repeated

    @property
    def is_vfx_shot(self):
        """
        Return True if this item is linked to a VFX shot
        """
        # Non vfx shots are not handled in SG by our current clients
        # so, for the time being, just check if the item is linked to
        # a shot : if not, then this is not a VFX shot entry
        if self._sg_shot:
            # Later we might want to do additional checks on the linked shot
            return True
        if not self._edit:
            # If we don't have an edit entry we should always have a sg_shot
            # coming from the Sequence
            return True
        # Return True if the edit has a shot name
        return bool(self._name)

    def set_siblings(self, siblings):
        """
        Set our list of siblings, which is other entries for the same shot
        :param siblings: a ShotCutDiffList or None
        """
        self._siblings  = siblings

    def check_changes(self):
        """
        Set the cut difference type for this cut difference
        Emit a type_changed if the value changed
        """
        old_type=self._diff_type
        self._check_changes()
        if old_type != self._diff_type:
            self.type_changed.emit(self, old_type, self._diff_type)
    
    def _check_changes(self):
        """
        Set the cut difference type for this cut difference
        """
        self._diff_type = _DIFF_TYPES.NO_CHANGE
        self._cut_changes_reasons = []
        # The type of difference we are dealing with
        if not self.name:
            self._diff_type = _DIFF_TYPES.NO_LINK
            return
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
        if self.new_head_in < self.head_in:
            self._diff_type = _DIFF_TYPES.RESCAN
            self._cut_changes_reasons.append("Head extended %d frs" % (self.head_in-self.new_head_in))

        if self.new_head_duration < 0:
            self._diff_type = _DIFF_TYPES.RESCAN
            self._cut_changes_reasons.append("Head extended %d frs" % (-self.new_head_duration+self.head_duration))

        if self.new_tail_out > self.tail_out:
            self._diff_type = _DIFF_TYPES.RESCAN
            self._cut_changes_reasons.append("Tail extended %d frs" % (self.new_tail_out-self.tail_out))

        if self.new_tail_duration < 0:
            self._diff_type = _DIFF_TYPES.RESCAN
            self._cut_changes_reasons.append("Tail extended %d frs" % (-self.new_tail_duration+self.tail_duration))

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
        # This is set explicetely by the cut summary, so we have a chance to
        # compare the new value with the old one
        if repeated != self.repeated:
            old_repeated = self._repeated
            self._repeated = repeated
            self.repeated_changed.emit(self, old_repeated, self._repeated)
            # Cut in / out values are affected by repeated changes
            self._check_changes()

    def summary(self):
        """
        Return a summary for this CutDiff instance as a tuple with :
         shot details, cut item details, version details and edit details
        :return: A four entries tuple, where each entry is a potentially empty string
        """
        shot_details = ""
        if self.sg_shot:
            if self._use_smart_fields:
                shot_details = \
                "Name : %s, Status : %s, Head In : %s, Cut In : %s, Cut Out : %s, Tail Out : %s, Cut Order : %s" % (
                    self.sg_shot["code"],
                    self.sg_shot["sg_status_list"],
                    self.sg_shot["smart_head_in"],
                    self.sg_shot["smart_cut_in"],
                    self.sg_shot["smart_cut_out"],
                    self.sg_shot["smart_tail_out"],
                    self.sg_shot["sg_cut_order"],
                )
            else:
                shot_details = \
                "Name : %s, Status : %s, Head In : %s, Cut In : %s, Cut Out : %s, Tail Out : %s, Cut Order : %s" % (
                    self.sg_shot["code"],
                    self.sg_shot["sg_status_list"],
                    self.sg_shot["sg_head_in"],
                    self.sg_shot["sg_cut_in"],
                    self.sg_shot["sg_cut_out"],
                    self.sg_shot["sg_tail_out"],
                    self.sg_shot["sg_cut_order"],
                )
        cut_item_details = ""
        if self.sg_cut_item:
            if self.sg_cut_item["sg_fps"] :
                fps = self.sg_cut_item["sg_fps"]
                tc_in = edl.Timecode(self.sg_cut_item["sg_timecode_cut_in"], fps)
                tc_out = edl.Timecode(self.sg_cut_item["sg_timecode_cut_out"], fps)
            else:
                tc_in = "????"
                tc_out = "????"
            cut_item_details = \
            "Cut Order %s, TC in %s, TC out %s, Cut In %s, Cut Out %s, Cut Duration %s" % (
                self.sg_cut_item["sg_cut_order"],
                tc_in,
                tc_out,
                self.sg_cut_item["sg_cut_in"],
                self.sg_cut_item["sg_cut_out"],
                self.sg_cut_item["sg_cut_duration"],
            )
        version_details = ""
        sg_version = self.sg_version
        if sg_version:
            version_details = "%s, link %s %s" % (
            sg_version["code"],
            sg_version["entity"]["type"] if sg_version["entity"] else "None",
            sg_version["entity.Shot.code"] if sg_version["entity.Shot.code"] else "",
            )
        return (shot_details, cut_item_details, version_details, str(self._edit))

