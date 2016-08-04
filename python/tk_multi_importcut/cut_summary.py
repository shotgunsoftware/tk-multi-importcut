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
from collections import defaultdict

# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
from sgtk.platform.qt import QtCore
from .cut_diff import CutDiff, _DIFF_TYPES
from .logger import get_logger
from .constants import _SHOT_FIELDS

# Some counts are per Shot, some others per edits
# As a rule of thumb, everything which directly affects the Shot is per
# Shot:
# - Creation of new Shots (NEW)
# - Omission of existing Shots (OMITTED)
# - Re-enabling existing Shots (REINSTATED)
# - Need for a rescan (RESCAN)
# On the other hand, in and out point changes, some repeated Shots being
# added or removed are counted per item and are considered CUT_CHANGES
_PER_SHOT_TYPE_COUNTS = [
    _DIFF_TYPES.NEW,
    _DIFF_TYPES.OMITTED,
    _DIFF_TYPES.REINSTATED,
    _DIFF_TYPES.RESCAN
]

# Template used by summary report
_BODY_REPORT_FORMAT = """
%s
Links : %s

The changes in %s are as follows:

%d New Shots
%s

%d Omitted Shots
%s

%d Reinstated Shot
%s

%d Cut Changes
%s

%d Rescan Needed
%s

"""


class ShotCutDiffList(list):
    """
    A list of cut differences for a given Shot. Minimum and maximum values
    are computed when adding / removing entries. These values are used to deal
    with repeated shots, that is, shots which appear more than once in the Cut.

    List of CutDiffs is typically stored in a dictionary where keys are Shot names
    """
    def __init__(self, cut_diff, *args, **kwargs):
        """
        Instantiate a new list with a single value

        :param cut_diff: A CutDiff instance
        :param args: An arbitrary list of parameters
        :param kwargs: An arbitrary dictionary of parameters
        """
        super(ShotCutDiffList, self).__init__(*args, **kwargs)
        self._logger = get_logger()
        # Defines default attributes
        self._reset_min_and_max()
        # Values above are populated in the append call below
        self.append(cut_diff)

    def _reset_min_and_max(self):
        """
        Reset values used to handle repeated shots min and max
        """
        # From a previous Cut
        self._min_tc_cut_in = None
        self._max_tc_cut_out = None
        self._earliest_entry = None
        self._last_entry = None
        # From the new edit values
        self._new_min_tc_cut_in = None
        self._new_max_tc_cut_out = None
        self._new_earliest_entry = None
        self._new_last_entry = None

    def append(self, cut_diff):
        """
        Add the given Cut difference to our list, recompute min and max values

        :param cut_diff: A CutDiff instance
        """
        super(ShotCutDiffList, self).append(cut_diff)
        self._update_min_and_max(cut_diff)
        cut_diff.set_siblings(self)
        if cut_diff == self._earliest_entry or cut_diff == self._last_entry:
            # We need to recompute in and out for all entries
            for cdiff in self:
                self._update_min_and_max(cdiff)

    def remove(self, cut_diff):
        """
        Remove the given Cut difference from our list, recompute min and max values

        :param cut_diff: A CutDiff instance
        """
        cut_diff.set_siblings(None)
        super(ShotCutDiffList, self).remove(cut_diff)
        # Reset our internal values
        self._reset_min_and_max()
        # And recompute them from what is left
        for cdiff in self:
            self._update_min_and_max(cdiff)

    @property
    def earliest(self):
        """
        Return the entry with the earliest tc cut in from our list

        :returns: A CutDiff instance, or None
        """

        # We might have a mix of omitted edits (no new value) and non omitted edits
        # (with new values) in our list. If we have at least one entry which is
        # not omitted (has new value) we consider entries with new values, so we
        # will consider omitted edits only if all edits are omitted
        if self._new_earliest_entry:
            return self._new_earliest_entry
        return self._earliest_entry

    @property
    def last(self):
        """
        Return the entry with last tc cut out from out list

        :returns: A CutDiff instance, or None
        """

        # We might have a mix of omitted edits (no new value) and non omitted edits
        # (with new values) in our list. If we have at least one entry which is
        # not omitted (has new value) we consider entries with new values, so we
        # will consider omitted edits only if all edits are omitted
        if self._new_last_entry:
            return self._new_last_entry
        return self._last_entry

    @property
    def min_tc_cut_in(self):
        """
        Return the earliest cut in timecode

        :returns: A Timecode
        """
        if self._new_min_tc_cut_in is not None:
            return self._new_min_tc_cut_in
        return self._min_tc_cut_in

    @property
    def min_cut_in(self):
        """
        Return the cut in for the earliest entry in the list

        :returns: A frame number as an integer
        """
        if self._new_earliest_entry:
            return self._new_earliest_entry.new_cut_in
        return self._earliest_entry.cut_in

    @property
    def max_tc_cut_out(self):
        """
        Return the maximum cut out timecode

        :returns: A Timecode
        """
        if self._new_max_tc_cut_out is not None:
            return self._new_max_tc_cut_out
        return self._max_tc_cut_out

    @property
    def max_cut_out(self):
        """
        Return the cut out for the last entry in this list

        :returns: A frame number as an integer
        """
        if self._new_last_entry:
            return self._new_last_entry.new_cut_out
        return self._last_entry.cut_out

    def get_shot_values(self):
        """
        Loop over our Cut diff list and return values which should be set on the
        Shot.

        The Shot difference type can be different from individual Cut difference
        types, for example a new edit can be added, but the Shot itself is not
        new.

        Return a tuple with :
        - A SG Shot dictionary or None
        - The smallest cut order
        - The earliest head in
        - The earliest cut in
        - The last cut out
        - The last tail out
        - The Shot difference type

        :returns: A tuple
        """
        min_cut_order = None
        min_head_in = None
        min_cut_in = None
        max_cut_out = None
        max_tail_out = None
        sg_shot = None
        shot_diff_type = None
        # Do a first pass with all entries to get min and max
        for cut_diff in self:
            if sg_shot is None and cut_diff.sg_shot:
                sg_shot = cut_diff.sg_shot
            edit = cut_diff.edit
            if edit and (min_cut_order is None or edit.id < min_cut_order):
                min_cut_order = edit.id
            if cut_diff.new_head_in is not None and (
                min_head_in is None or cut_diff.new_head_in < min_head_in):
                    min_head_in = cut_diff.new_head_in
            if cut_diff.new_cut_in is not None and (
                min_cut_in is None or cut_diff.new_cut_in < min_cut_in):
                    min_cut_in = cut_diff.new_cut_in
            if cut_diff.new_cut_out is not None and (
                max_cut_out is None or cut_diff.new_cut_out > max_cut_out):
                    max_cut_out = cut_diff.new_cut_out
            if cut_diff.new_tail_out is not None and (
                max_tail_out is None or cut_diff.new_tail_out > max_tail_out):
                    max_tail_out = cut_diff.new_tail_out
        # We do a second pass for the Shot difference type, as we might stop
        # iteration at some point. Given that the number of duplicated shots is
        # usually low, there shouldn't be a big performance hit in iterating twice
        for cut_diff in self:
            # Special cases for diff type:
            # - A Shot is NO_LINK if any of its items is NO_LINK (should be all of them)
            # - A Shot is OMITTED if all its items are OMITTED
            # - A Shot is NEW if any of its items is NEW (should be all of them)
            # - A Shot is REINSTATED if at least one of its items is REINSTATED (should
            #       be all of them)
            # - A Shot needs RESCAN if any of its items need RESCAN
            cut_diff_type = cut_diff.diff_type
            if cut_diff_type in [
                _DIFF_TYPES.NO_LINK,
                _DIFF_TYPES.NEW,
                _DIFF_TYPES.REINSTATED,
                _DIFF_TYPES.OMITTED,
                _DIFF_TYPES.RESCAN
            ]:
                shot_diff_type = cut_diff_type
                # Can't be changed by another entry, no need to loop further
                break

            if cut_diff_type == _DIFF_TYPES.OMITTED_IN_CUT:
                # Could be a repeated Shot entry removed from the Cut
                # or really the whole Shot being removed
                if shot_diff_type is None:
                    # Set initial value
                    shot_diff_type = _DIFF_TYPES.OMITTED
                elif shot_diff_type == _DIFF_TYPES.NO_CHANGE:
                    shot_diff_type = _DIFF_TYPES.CUT_CHANGE
                else:
                    # Shot is already with the right state, no need to do anything
                    pass

            elif cut_diff_type == _DIFF_TYPES.NEW_IN_CUT:
                shot_diff_type = _DIFF_TYPES.CUT_CHANGE
            else:    # _DIFF_TYPES.NO_CHANGE, _DIFF_TYPES.CUT_CHANGE
                if shot_diff_type is None:
                    # initial value
                    shot_diff_type = cut_diff_type
                elif shot_diff_type != cut_diff_type:
                    # If different values fall back to CUT_CHANGE
                    # If values are identical, do nothing
                    shot_diff_type = _DIFF_TYPES.CUT_CHANGE
        # Having _OMITTED_IN_CUT here means that all entries were _OMITTED_IN_CUT
        # so the whole Shot is _OMITTED
        if shot_diff_type == _DIFF_TYPES.OMITTED_IN_CUT:
            shot_diff_type = _DIFF_TYPES.OMITTED
        return (
            sg_shot,
            min_cut_order,
            min_head_in,
            min_cut_in,
            max_cut_out,
            max_tail_out,
            shot_diff_type,
        )

    def _update_min_and_max(self, cut_diff):
        """
        Update min and max values from the given Cut difference

        :param cut_diff: A CutDiff instance
        """
        tc_cut_in = cut_diff.tc_cut_in
        if tc_cut_in is not None and (
            self._min_tc_cut_in is None or tc_cut_in.to_frame() < self._min_tc_cut_in.to_frame()):
                self._min_tc_cut_in = tc_cut_in
                self._earliest_entry = cut_diff
        tc_cut_out = cut_diff.tc_cut_out
        if tc_cut_out is not None and (
            self._max_tc_cut_out is None or tc_cut_out.to_frame() > self._max_tc_cut_out.to_frame()):
                self._max_tc_cut_out = tc_cut_out
                self._last_entry = cut_diff

        tc_cut_in = cut_diff.new_tc_cut_in
        if tc_cut_in is not None and (
            self._new_min_tc_cut_in is None or tc_cut_in.to_frame() < self._new_min_tc_cut_in.to_frame()):
                self._new_min_tc_cut_in = tc_cut_in
                self._new_earliest_entry = cut_diff
        tc_cut_out = cut_diff.new_tc_cut_out
        if tc_cut_out is not None and (
            self._new_max_tc_cut_out is None or tc_cut_out.to_frame() > self._new_max_tc_cut_out.to_frame()):
                self._new_max_tc_cut_out = tc_cut_out
                self._new_last_entry = cut_diff


class CutSummary(QtCore.QObject):
    """
    A list of Cut differences, stored in CutDiff instances
    
    CutDiffs are organised in a dictionary where keys are Shot names, allowing
    to group together entries for the same Shots
    """
    # Emitted when a new CutDiff was added to the summary
    new_cut_diff = QtCore.Signal(CutDiff)
    # Emitted when totals per diff type changed
    totals_changed = QtCore.Signal()
    # Emitted when a CutDiff was removed from the summary
    delete_cut_diff = QtCore.Signal(CutDiff)

    def __init__(
            self,
            sg_project,
            sg_entity,
            sg_shot_link_field_name,
            tc_edit_in=None,
            tc_edit_out=None,
            ):
        """
        Create a new empty CutSummary

        Two timecodes can be given to define the whole edit range. If given, an
        offset will be available so when creating CutItems all edit timecodes can
        be 00:00:00:00 based, instead of being kept absolute.
        
        A Shotgun Project is needed, as it might differ from the current context
        Project, if the user picked another one.

        The Shotgun Entity can be a Scene, a Sequence, or any other Shot container.
        It is the Entity the Cut is related to

        :param sg_project: A SG Project dictionary
        :param sg_entity: A SG Entity dictionary
        :param sg_shot_link_field_name: The name of the field used to link Shots
                                        to the SG Entity
        :param tc_edit_in: A Timecode instance, the very first edit timecode in
        :param tc_edit_out: A Timecode instance, the very last edit timecode out
        """
        super(CutSummary, self).__init__()
        self._cut_diffs = {}
        self._total_count = 0
        # Use a defaultdict so we don't have to worry about key existence
        self._counts = defaultdict(int)
        self._logger = get_logger()
        self._app = sgtk.platform.current_bundle()

        self._tc_start = tc_edit_in
        self._tc_end = tc_edit_out
        self._sg_project = sg_project
        self._sg_entity = sg_entity
        self._sg_shot_link_field_name = sg_shot_link_field_name
        self._edit_offset = 0
        self._duration = 0
        if self._tc_start is not None:
            self._edit_offset = tc_edit_in.to_frame()
            if self._tc_end is not None:
                # TC in is inclusive, TC out is exclusive, the real formula would be
                # duration = tc_out - 1 - tc_in + 1
                # so we simplify it by not adding and subtracting 1
                # and reuse the frame conversion computed for the edit offset
                self._duration = tc_edit_out.to_frame() - self._edit_offset

        self._logger.info("Edit offset %s, duration %s" % (self._edit_offset, self._duration))

    @property
    def timecode_start(self):
        """
        Return the very first edit timecode in

        :returns: A Timecode or None
        """
        return self._tc_start

    @property
    def timecode_end(self):
        """
        Return the very last edit timecode out

        :returns: A Timecode or None
        """
        return self._tc_end

    @property
    def duration(self):
        """
        Return the duration of the edit

        :returns: A frame count as an integer
        """
        return self._duration

    @property
    def edit_offset(self):
        """
        Return an offset to rebase all edit timecodes to 00:00:00:00

        :returns: A frame count as an integer
        """
        return self._edit_offset

    def add_cut_diff(self, shot_name, sg_shot=None, edit=None, sg_cut_item=None):
        """
        Add a new Cut difference to this summary

        :param shot_name: Shot name, as a string
        :param sg_shot: An optional Shot, as a dictionary retrieved from Shotgun
        :param edit: An optional CutEdit object
        :param sg_cut_item: An optional Cut Item, as a dictionary retrieved from Shotgun
        :return: A new CutDiff instance
        """
        if sg_shot is None and edit is None and sg_cut_item is None:
            raise ValueError("At least one of the Shot, Edit or CutItem must be specified")

        cut_diff = CutDiff(
            shot_name,
            sg_shot=sg_shot,
            edit=edit,
            sg_cut_item=sg_cut_item
        )
        cut_diff.name_changed.connect(self.cut_diff_name_changed)
        cut_diff.type_changed.connect(self.cut_diff_type_changed)
        # Force a lowercase key to make Shot names case-insensitive. Shot names
        # we retrieve from EDLs may be uppercase, but actual SG Shots may be
        # lowercase.
        # We might not have a valid Shot name if we have an edit without any
        # Shot name or Version name. To avoid considering all these entries
        # as repeated Shots we forge a key based on the cut order.
        shot_key = shot_name.lower() if shot_name else "_no_shot_name_%s" % cut_diff.new_cut_order
        if shot_key in self._cut_diffs:
            self._cut_diffs[shot_key].append(cut_diff)
            if len(self._cut_diffs[shot_key]) > 1:
                for cdiff in self._cut_diffs[shot_key]:
                    cdiff.set_repeated(True)
        else:
            self._cut_diffs[shot_key] = ShotCutDiffList(cut_diff)
            cut_diff.set_repeated(False)

        diff_type = cut_diff.diff_type
        self._recompute_counts()
        self.new_cut_diff.emit(cut_diff)
        return cut_diff

    @QtCore.Slot(CutDiff, unicode, unicode)
    def cut_diff_name_changed(self, cut_diff, uold_name, unew_name):
        """
        Handle Cut diff (Shot) name changes

        When a CutDiff name is changed, we need to link it to the right Shot. This
        can change its "repeated" property, if we are already holding an entry for
        this Shot, which in turn can change the DiffType we are dealing with.
        
        We need to unlink it as well from the Shot associated with the previous name, 
        leading to similar changes for entries associated with this Shot, if any.

        Whether or not the name can be edited is controlled by CutDiff.is_name_editable.
        At the very least, the CutDiff should have a valid Edit: we don't rename
        entries from a previous import.

        :param cut_diff: A CutDiff instance
        :param uold_name: A string, the CutDiff previous name, as a unicode string
        :param unew_name: A string, the CutDiff new name, as a unicode string
        """

        # Only CutDiff with a valid edit should be allowed to be renamed.
        # This is checked in CutDiff.is_name_editable, however, re-iterate
        # the check here, so coders know what to expect
        if not cut_diff.edit:
            raise RuntimeError(
                "%s does not have a a valid edit and can't be renamed" % cut_diff.name
            )

        new_name = unew_name.encode("utf-8")
        old_name = uold_name.encode("utf-8")
        # We might have empty names here. To avoid considering all entries
        # with no name as repeated Shots we forge a key based on the cut order.
        new_shot_key = new_name.lower() if new_name else "_no_shot_name_%s" % cut_diff.new_cut_order
        old_shot_key = old_name.lower() if old_name else "_no_shot_name_%s" % cut_diff.new_cut_order
        if new_shot_key == old_shot_key:
            return

        # Remove it from our internal Shot / cut_diff dictionary
        if old_shot_key not in self._cut_diffs:
            raise RuntimeError("Can't retrieve Shot %s in internal list" % old_shot_key)
        self._cut_diffs[old_shot_key].remove(cut_diff)
        # If we have a SG Shot, and a CutItem, it is now an omitted one
        if cut_diff.sg_cut_item and cut_diff.sg_shot:
            self._logger.debug("Adding omitted entry for old shot key %s" % old_shot_key)
            sg_shot = cut_diff.sg_shot
            sg_cut_item = cut_diff.sg_cut_item
            self.add_cut_diff(
                sg_shot["code"],
                sg_shot=sg_shot,
                edit=None,
                sg_cut_item=sg_cut_item,
            )
        count = len(self._cut_diffs[old_shot_key])
        if count == 0:
            self._logger.debug("No more entries for old shot key %s" % old_shot_key)
            self._logger.debug("Discarding list for old shot key %s" % old_shot_key)
            # We can discard the list for this shot
            del self._cut_diffs[old_shot_key]
        elif count == 1:
            self._logger.debug("Single entry for old Shot key %s" % old_shot_key)
            # This guy is alone now, so not repeated
            self._cut_diffs[old_shot_key][0].set_repeated(False)

        # If the Cut diff was repeated, default back to non repeated
        if cut_diff.repeated:
            cut_diff.set_repeated(False)

        # These are not valid anymore
        cut_diff.set_sg_shot(None)
        cut_diff.set_sg_cut_item(None)

        # Add it back with the new name
        if new_shot_key in self._cut_diffs:
            for cdiff in self._cut_diffs[new_shot_key]:
                self._logger.debug("%s %s %s %s" % cdiff.summary())
            count = len(self._cut_diffs[new_shot_key])
            self._logger.debug("%d Entrie(s) for new shot key %s" % (count, new_shot_key))
            # Check if there is some omitted entries (no edit) which we should
            # replace, and choose the best one to replace
            matching_omit_entries = [
                x for x in self._cut_diffs[new_shot_key] if not x.edit
            ]
            self._logger.debug("Potential matches: %s" % matching_omit_entries)
            if matching_omit_entries:
                # Loop over candidates and choose the best one
                best_cdiff = None
                best_score = -1
                for cdiff in matching_omit_entries:
                    score = cut_diff.get_matching_score(cdiff)
                    if best_cdiff is None or score > best_score:
                        best_cdiff = cdiff
                        best_score = score
                self._logger.debug(
                    "Found omitted entry for new shot key %s: %s" % (
                        new_shot_key, str(best_cdiff)
                ))
                # Remove the chosen CutDiff
                self._cut_diffs[new_shot_key].remove(best_cdiff)
                self.delete_cut_diff.emit(best_cdiff)
                # Recompute totals with the removed cut diff
                self.cut_diff_type_changed(best_cdiff, best_cdiff.diff_type, None)
                # And add the edited CutDiff, reusing some data of the CutDiff
                # we are replacing
                cut_diff.set_sg_shot(best_cdiff.sg_shot)
                cut_diff.set_sg_cut_item(best_cdiff.sg_cut_item)
                if cut_diff.edit:
                    cut_diff.set_sg_version(best_cdiff.sg_version)
                self._cut_diffs[new_shot_key].append(cut_diff)
                if count > 1:
                    # If the Shot is repeated, flag the edited CutDiff as repeated
                    try:
                        cut_diff.set_repeated(True)
                    except TypeError, e:
                        # Adding some extra debug information here, because a lot
                        # of edge cases exist when editing shot names for repeated
                        # shots
                        self._logger.debug("%s".join(cut_diff.summary()))
                        self._logger.debug(str(self._cut_diffs[new_shot_key]))
                        raise
            else:
                self._logger.debug("Adding new entry for new Shot key %s" % new_shot_key)
                # SG Shot is shared by all entries in this list
                cdiff = self._cut_diffs[new_shot_key][0]
                cut_diff.set_sg_shot(cdiff.sg_shot)
                cut_diff.set_sg_version(cdiff.sg_version)
                # Append and flag everything as repeated
                self._cut_diffs[new_shot_key].append(cut_diff)
                for cdiff in self._cut_diffs[new_shot_key]:
                    cdiff.set_repeated(True)
        else:
            existing_linked_shot = self._app.shotgun.find_one(
                "Shot", [
                    ["project", "is", self._sg_project],
                    [self._sg_shot_link_field_name, "is", self._sg_entity],
                    ["code", "is", new_name]
                ],
                _SHOT_FIELDS
            )
            if existing_linked_shot:
                # Link to the first Shot found in the linked Entity whose name matches new_name
                cut_diff.set_sg_shot(existing_linked_shot)
            else:
                # Link to the first Shot found whose name matches new_name
                existing_unlinked_shot = self._app.shotgun.find_one(
                    "Shot", [
                        ["project", "is", self._sg_project], ["code", "is", new_name]
                    ],
                    _SHOT_FIELDS
                )
                if existing_unlinked_shot:
                    cut_diff.set_sg_shot(existing_unlinked_shot)
            self._logger.debug("Creating single entry for new Shot key %s" % new_shot_key)
            self._cut_diffs[new_shot_key] = ShotCutDiffList(cut_diff)
        cut_diff.check_and_set_changes()
        self._recompute_counts()

    @QtCore.Slot(CutDiff, int, int)
    def cut_diff_type_changed(self, cut_diff, old_type, new_type):
        """
        Recompute internal totals when a Cut diff type changed

        :param cut_diff: A CutDiff instance
        :param old_type: Previous diff type for the CutDiff instance
        :param new_type: New diff type for the CutDiff instance, or None if it
                         has been deleted
        :raises: RuntimeError if the old type is unknown
        """
        if old_type == new_type:
            return
        if old_type not in self._counts:
            # This can happen if the diff type changed when a cut_diff is added
            # with repeated shots
            self._logger.debug(
                "Couldn't retrieve Cut diff type %s in counts (new type : %s)" % (
                    old_type, new_type,
                )
            )
        else:
            self._counts[old_type] -= 1
            if self._counts[old_type] == 0:
                del self._counts[old_type]

        if new_type is not None:  # None is used when some cut diff are deleted
            self._counts[new_type] += 1

        # Maintain our total count, excluding OMITTED entries.
        # If the entry was OMITTED, and is not OMITTED anymore, count it in our
        # total
        if (old_type in [_DIFF_TYPES.OMITTED, _DIFF_TYPES.OMITTED_IN_CUT] and
            new_type not in [_DIFF_TYPES.OMITTED, _DIFF_TYPES.OMITTED_IN_CUT]):
            self._total_count += 1
        # If the entry was not OMITTED, and is now OMITTED, remove it from our total
        elif (old_type not in [_DIFF_TYPES.OMITTED, _DIFF_TYPES.OMITTED_IN_CUT] and
              new_type in [_DIFF_TYPES.OMITTED, _DIFF_TYPES.OMITTED_IN_CUT]):
            self._total_count -= 1
        self.totals_changed.emit()

    @property
    def total_count(self):
        """
        Return the total number of entries

        :returns: An integer
        """
        return self._total_count

    @property
    def rescans_count(self):
        """
        Return the number of entries needing a rescan

        :returns: An integer
        """
        return self._counts.get(_DIFF_TYPES.RESCAN, 0)

    @property
    def repeated_count(self):
        """
        Return the number of entries which share their Shot with another entry

        :returns: An integer
        """
        return sum([len(self._cut_diffs[x]) for x in self._cut_diffs if len(self._cut_diffs[x]) > 1])

    def count_for_type(self, diff_type):
        """
        Return the number of entries for the given CutDiffType

        :param diff_type: A CutDiffType
        :returns: An integer
        """
        return self._counts.get(diff_type, 0)

    def edits_for_type(self, diff_type, just_earliest=False):
        """
        Iterate over CutDiff instances for the given CutDiffType

        :param diff_type: A CutDiffType
        :param just_earliest: Whether or not all matching CutDiff should be
                              returned or just the earliest(s)
        :yields: CutDiff instances
        """
        for name, items in self._cut_diffs.iteritems():
            for item in items:
                if item.interpreted_diff_type == diff_type and (not just_earliest or item.is_earliest()):
                    yield item

    def has_shot(self, shot_name):
        """
        Return True if there is already an entry in this summary for the given Shot

        :param shot_name: A Shot name, as a string
        :returns: True if the Shot is already known, False otherwise
        """
        return shot_name.lower() in self._cut_diffs

    def diffs_for_shot(self, shot_name):
        """
        Return the CutDiff(s) list for the given shot, if any.

        :param shot_name: A Shot name, as a string
        :returns: A list of CutDiffs
        """
        return self._cut_diffs.get(shot_name.lower())

    def _recompute_counts(self):
        """
        Recompute internal counts from Cut differences
        """
        # Use a defaultdict so we don't have to worry about key existence
        self._counts = defaultdict(int)
        self._total_count = 0
        for shot, diff_list in self._cut_diffs.iteritems():
            _, _, _, _, _, _, shot_diff_type = diff_list.get_shot_values()
            if shot_diff_type in _PER_SHOT_TYPE_COUNTS:
                # We count these per shots
                self._counts[shot_diff_type] += 1
                # We don't want to include omitted entries in our total
                if shot_diff_type != _DIFF_TYPES.OMITTED:
                    self._total_count += 1
            else:
                # We count others per entries
                for cut_diff in diff_list:
                    # We don't use cut_diff.interpreted_type here, as it will
                    # loop over all siblings, repeated shots cases are handled
                    # with the shot_diff_type
                    diff_type = self._interpreted_diff_type(cut_diff.diff_type)
                    self._counts[diff_type] += 1
                    # We don't want to include omitted entries in our total
                    if cut_diff.diff_type not in [
                        _DIFF_TYPES.OMITTED_IN_CUT, _DIFF_TYPES.OMITTED]:
                        self._total_count += 1
        self._logger.debug(str(self._counts))
        self.totals_changed.emit()

    def _interpreted_diff_type(self, diff_type):
        """
        Some difference types are grouped under a common type, return
        this group type for the given difference type

        :returns: A _DIFF_TYPES
        """
        if diff_type in [_DIFF_TYPES.NEW_IN_CUT, _DIFF_TYPES.OMITTED_IN_CUT]:
            return _DIFF_TYPES.CUT_CHANGE
        return diff_type

    def __len__(self):
        """
        Return the total number of CutDiff entries in this summary

        :returns: An integer
        """
        return sum([len(self._cut_diffs[k]) for k in self._cut_diffs], 0)

    def __iter__(self):
        """
        Iterate over shots for this summary

        :yields: Shot names, as strings
        """
        for name in self._cut_diffs.keys():
            yield name

    def __getitem__(self, key):
        """
        Return CutDiffs list for a given Shot

        :returns: A list of CutDiffs
        """
        return self._cut_diffs.get(key.lower())

    def iteritems(self):
        """
        Iterate over Shot names for this summary, yielding (name, CutDiffs list)
        tuple

        :yields: (name, CutDiffs list) tuples
        """
        for name, items in self._cut_diffs.iteritems():
            yield (name, items)

    def get_report(self, title, sg_links):
        """
        Build a text report for this summary, highlighting changes

        :param title: A title for the report
        :param sg_links: Shotgun URLs to display in the report as links
        :return: A (subject, body) tuple, as strings
        """
        # Body should look like this:
        # The changes in {Name of Cut/EDL} are as follows:
        #
        # 5 New Shots
        # HT0500
        # HT0510
        # HT0520
        # HT0530
        # HT0540
        #
        # 2 Omitted Shots
        # HT0050
        # HT0060
        #
        # 1 Reinstated Shot
        # HT0110
        #
        # 4 Cut Changes
        # HT0070 - Head extended 2 frs
        # HT0080 - Tail extended 6 frs
        # HT0090 - Tail trimmed 5 frs
        # HT0100 - Head extended 5 frs
        #
        # 1 Rescan Needed
        # HT0120 - Head extended 15 frs

        subject = "%s Cut Summary changes on %s" % (
            self._sg_entity["type"].title(),
            title
        )

        cut_changes_details = [
            "%s - %s" % (
                edit.name, ", ".join(edit.reasons)
            ) for edit in sorted(
                self.edits_for_type(_DIFF_TYPES.CUT_CHANGE),
                key=lambda x: x.new_cut_order
            )
        ]
        rescan_details = [
            "%s - %s" % (
                edit.name, ", ".join(edit.reasons)
            ) for edit in sorted(
                self.edits_for_type(_DIFF_TYPES.RESCAN),
                key=lambda x: x.new_cut_order
            )
        ]
        no_link_details = [
            edit.version_name or str(edit.new_cut_order) for edit in sorted(
                self.edits_for_type(_DIFF_TYPES.NO_LINK),
                key=lambda x: x.new_cut_order
            )
        ]
        body = _BODY_REPORT_FORMAT % (
            # Let the user know that something is potentially wrong
            "WARNING, following edits couldn't be linked to any Shot :\n%s\n" % (
                "\n".join(no_link_details)
            ) if no_link_details else "",
            # Urls
            " , ".join(sg_links),
            # Title
            title,
            # And then counts and lists per type of changes
            self.count_for_type(_DIFF_TYPES.NEW),
            "\n".join([
                edit.name for edit in sorted(
                    self.edits_for_type(_DIFF_TYPES.NEW, just_earliest=True),
                    key=lambda x: x.new_cut_order
                )
            ]),
            self.count_for_type(_DIFF_TYPES.OMITTED),
            "\n".join([
                edit.name for edit in sorted(
                    self.edits_for_type(_DIFF_TYPES.OMITTED, just_earliest=True),
                    key=lambda x: x.cut_order or -1
                )
            ]),
            self.count_for_type(_DIFF_TYPES.REINSTATED),
            "\n".join([
                edit.name for edit in sorted(
                    self.edits_for_type(_DIFF_TYPES.REINSTATED, just_earliest=True),
                    key=lambda x: x.new_cut_order
                )
            ]),
            self.count_for_type(_DIFF_TYPES.CUT_CHANGE),
            "\n".join(cut_changes_details),
            self.count_for_type(_DIFF_TYPES.RESCAN),
            "\n".join(rescan_details),
        )
        return subject, body
