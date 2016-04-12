# Copyright (c) 2016 Shotgun Software Inc.
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
from .cut_diff import CutDiff, _DIFF_TYPES
from .logger import get_logger

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
    A list of cut differences for a given shot. Minimum and maximum values
    are computed when adding / removing entries. These values are used to deal
    with repeated shots, that is, shots which appears more than once in the cut.
    """
    def __init__(self, cut_diff, *args, **kwargs):
        super(ShotCutDiffList, self).__init__(*args, **kwargs)
        self._logger = get_logger()
        self._reset_min_and_max()  # Just so attributes are defined
        # Values above are populated in the append call below
        self.append(cut_diff)

    def _reset_min_and_max(self):
        """
        Reset values used to handle repeated shots min and max
        """
        # From a previous cut
        self._min_tc_cut_in = None
        self._max_tc_cut_out = None
        self._earliest_entry = None
        self._latest_entry = None
        # From the new edit
        self._new_min_tc_cut_in = None
        self._new_max_tc_cut_out = None
        self._new_earliest_entry = None
        self._new_latest_entry = None

    def append(self, cut_diff):
        """
        Add the given cut difference to our list, recompute min and max values
        :param cut_diff: A CutDiff instance
        """
        old_len = len(self)
        super(ShotCutDiffList, self).append(cut_diff)
        self._update_min_and_max(cut_diff)
        cut_diff.set_siblings(self)
        if cut_diff == self._earliest_entry or cut_diff == self._latest_entry:
            # We neeed to recompute in and out for all entries
            for cdiff in self:
                self._update_min_and_max(cdiff)

    def remove(self, cut_diff):
        """
        Remove the given cut difference from our list, recompute min and max values
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
        if self._earliest_entry:
            return self._earliest_entry
        return self._new_earliest_entry

    @property
    def latest(self):
        """
        Return the entry with latest tc cut out from out list

        :returns: A CutDiff instance, or None
        """
        if self._latest_entry:
            return self._latest_entry
        return self._new_latest_entry

    @property
    def min_tc_cut_in(self):
        if self._min_tc_cut_in is not None:
            return self._min_tc_cut_in
        return self._new_min_tc_cut_in

    @property
    def min_cut_in(self):
        if self._earliest_entry:
            return self._earliest_entry.cut_in
        return self._new_earliest_entry.new_cut_in

    @property
    def max_tc_cut_out(self):
        if self._max_tc_cut_out is not None:
            return self._max_tc_cut_out
        return self._new_max_tc_cut_out

    def get_shot_values(self):
        """
        Loop over our cut diff list and return values which should be set on the
        Shot.

        The shot difference type can be different from individual cut difference
        types, for example a new edit can be added, but the shot itself is not
        new.

        Return a tuple with :
        - A SG Shot dictionary or None
        - The smallest cut order
        - The earliest cut in
        - The latest cut out
        - The shot difference type
        """
        min_cut_order = None
        min_cut_in = None
        max_cut_out = None
        sg_shot = None
        shot_diff_type = None
        for cut_diff in self:
            if sg_shot is None and cut_diff.sg_shot:
                sg_shot = cut_diff.sg_shot
            edit = cut_diff.edit
            if edit and (min_cut_order is None or edit.id < min_cut_order):
                min_cut_order = edit.id
            if cut_diff.new_cut_in is not None and (
                min_cut_in is None or cut_diff.new_cut_in < min_cut_in):
                    min_cut_in = cut_diff.new_cut_in
            if cut_diff.new_cut_out is not None and (
                max_cut_out is None or cut_diff.new_cut_out > max_cut_out):
                    max_cut_out = cut_diff.new_cut_out
            # Special cases for diff type :
            # - A shot is no link if any of its items is no link (should be all of them)
            # - A shot is omitted if all its items are omitted
            # - A shot is new if any of its items is new (should be all of them)
            # - A shot is reinstated if at least one of its items is reinstated (should be all of them)
            # - A shot needs rescan if any of its items neeed rescan
            cut_diff_type = cut_diff.diff_type
            if cut_diff_type in [
                _DIFF_TYPES.NO_LINK,
                _DIFF_TYPES.NEW,
                _DIFF_TYPES.REINSTATED,
                _DIFF_TYPES.OMITTED
            ]:
                shot_diff_type = cut_diff_type
                # Can't be changed by another entry, no need to loop further
                break

            if cut_diff_type == _DIFF_TYPES.OMITTED_IN_CUT:
                # Could be a repeated shot entry removed from the cut
                # or really the whole shot being removed
                if shot_diff_type is None:
                    # Set initial value
                    shot_diff_type = _DIFF_TYPES.OMITTED
                elif shot_diff_type == _DIFF_TYPES.NO_CHANGE:
                    shot_diff_type = _DIFF_TYPES.CUT_CHANGE
                else:
                    # Shot is already with the right state, no need to do anything
                    pass

            elif cut_diff_type == _DIFF_TYPES.RESCAN:
                shot_diff_type = _DIFF_TYPES.RESCAN
            elif cut_diff_type == _DIFF_TYPES.NEW_IN_CUT:
                # Only set the value if not already set to something and
                # not RESCAN, to preserve it
                if shot_diff_type is None or shot_diff_type != _DIFF_TYPES.RESCAN:
                    # Report them as cut changes at the shot level
                    shot_diff_type = _DIFF_TYPES.CUT_CHANGE
            else:    # _DIFF_TYPES.NO_CHANGE, _DIFF_TYPES.CUT_CHANGE
                if shot_diff_type is None:
                    # initial value
                    shot_diff_type = cut_diff_type
                elif shot_diff_type != _DIFF_TYPES.RESCAN:  # Preserve rescan
                    if shot_diff_type != cut_diff_type:
                        # If different values fall back to CUT_CHANGE
                        shot_diff_type = _DIFF_TYPES.CUT_CHANGE
        # Having _OMITTED_IN_CUT here means that all entries were _OMITTED_IN_CUT
        # so the whole shot is _OMITTED
        if shot_diff_type == _DIFF_TYPES.OMITTED_IN_CUT:
            shot_diff_type = _DIFF_TYPES.OMITTED
        return (sg_shot, min_cut_order, min_cut_in, max_cut_out, shot_diff_type,)

    def _update_min_and_max(self, cut_diff):
        """
        Update min and max values from the given cut diffence

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
                self._latest_entry = cut_diff

        tc_cut_in = cut_diff.new_tc_cut_in
        if tc_cut_in is not None and (
            self._new_min_tc_cut_in is None or tc_cut_in.to_frame() < self._new_min_tc_cut_in.to_frame()):
                self._new_min_tc_cut_in = tc_cut_in
                self._new_earliest_entry = cut_diff
        tc_cut_out = cut_diff.new_tc_cut_out
        if tc_cut_out is not None and (
            self._new_max_tc_cut_out is None or tc_cut_out.to_frame() > self._new_max_tc_cut_out.to_frame()):
                self._new_max_tc_cut_out = tc_cut_out
                self._new_latest_entry = cut_diff


class CutSummary(QtCore.QObject):
    """
    A list of cut differences, stored in CutDiff instances
    """
    new_cut_diff = QtCore.Signal(CutDiff)
    totals_changed = QtCore.Signal()
    delete_cut_diff = QtCore.Signal(CutDiff)

    def __init__(self, tc_edit_in=None, tc_edit_out=None):
        """
        Create a new empty CutSummary
        :param tc_edit_in: A Timecode instance, first edit timecode in
        :param tc_edit_out: A Timecode instance, very last edit timecode out
        """
        super(CutSummary, self).__init__()
        self._cut_diffs = {}
        self._counts = {}
        self._cut_item_notes = {}
        self._rescans_count = 0
        self._logger = get_logger()

        user_settings = sgtk.platform.current_bundle().user_settings

        self._omit_statuses = [user_settings.retrieve("omit_status")]

        self._tc_start = tc_edit_in
        self._tc_end = tc_edit_out
        self._edit_offset = 0
        self._duration = 0
        self._fps = float(user_settings.retrieve("default_frame_rate"))

    @property
    def timecode_start(self):
        return self._tc_start

    @property
    def timecode_end(self):
        return self._tc_end

    @property
    def duration(self):
        return self._duration

    @property
    def edit_offset(self):
        return self._edit_offset

    @property
    def fps(self):
        return self._fps

    @property
    def cut_item_notes(self):
        return self._cut_item_notes

    @timecode_start.setter
    def timecode_start(self, value):
        self._tc_start = value

    @timecode_end.setter
    def timecode_end(self, value):
        self._tc_end = value

    @duration.setter
    def duration(self, value):
        self._duration = value

    @edit_offset.setter
    def edit_offset(self, value):
        self._edit_offset = value

    @fps.setter
    def fps(self, value):
        self._fps = value

    @cut_item_notes.setter
    def cut_item_notes(self, value):
        self._cut_item_notes = value

    def add_cut_diff(self, shot_name, sg_shot=None, edit=None, sg_cut_item=None):
        """
        Add a new cut difference to this summary

        :param shot_name: Shot name, as a string
        :param sg_shot: An optional Shot, as a dictionary retrieved from Shotgun
        :param edit: An optional CutEdit object
        :param sg_cut_item: An optional Cut Item, as a dictionary retrieved from Shotgun
        :return: A new CutDiff instance
        """
        if sg_shot is None and edit is None and sg_cut_item is None:
            raise ValueError("At least one of the shot, edit or cut item must be speified")

        cut_diff = CutDiff(
            shot_name,
            sg_shot=sg_shot,
            edit=edit,
            sg_cut_item=sg_cut_item
        )
        cut_diff.name_changed.connect(self.cut_diff_name_changed)
        cut_diff.type_changed.connect(self.cut_diff_type_changed)
        # Use a lower case key, as shot names we retrieve from EDLs
        # can be upper cases, but actual SG shots be lower cases
        shot_key = shot_name.lower() if shot_name else "_no_shot_name_"
        if shot_key in self._cut_diffs:
            self._cut_diffs[shot_key].append(cut_diff)
            if len(self._cut_diffs[shot_key]) > 1:
                for cdiff in self._cut_diffs[shot_key]:
                    cdiff.set_repeated(True)
        else:
            self._cut_diffs[shot_key] = ShotCutDiffList(cut_diff)
            cut_diff.set_repeated(False)
        diff_type = cut_diff.diff_type
        # Some counts are per shot, some others per edits, so only update some
        # of them if the new entry is not repeated
        if diff_type not in [
            _DIFF_TYPES.NEW,
            _DIFF_TYPES.OMITTED,
            _DIFF_TYPES.REINSTATED,
            _DIFF_TYPES.RESCAN
        ] or not cut_diff.repeated:
            if diff_type in self._counts:
                self._counts[diff_type] += 1
            else:
                self._counts[diff_type] = 1

        self._recompute_counts()

        self.new_cut_diff.emit(cut_diff)
        return cut_diff

    @QtCore.Slot(CutDiff, str, str)
    def cut_diff_name_changed(self, cut_diff, old_name, new_name):
        """
        Handle cut diff (shot) name changes

        :param cut_diff: A CutDiff instance
        :param old_name: A string, the CutDiff previous name
        :param new_name: A string, the CutDiff new name
        """
        new_shot_key = new_name.lower() if new_name else "_no_shot_name_"
        old_shot_key = old_name.lower() if old_name else "_no_shot_name_"
        if new_shot_key == old_shot_key:
            return

        # Remove it from our internal shot / cut_diff dictionary
        if old_shot_key not in self._cut_diffs:
            raise RuntimeError("Can't retrieve shot %s in internal list" % old_shot_key)
        self._cut_diffs[old_shot_key].remove(cut_diff)
        count = len(self._cut_diffs[old_shot_key])
        if count == 0:
            self._logger.debug("No more entry for old shot key %s" % old_shot_key)
            # If we have a SG shot, it is now an omitted one
            if cut_diff.sg_shot:
                self._logger.debug("Adding omitted entry for old shot key %s" % old_shot_key)
                sg_shot = cut_diff.sg_shot
                sg_cut_item = cut_diff.sg_cut_item
                cdiff = self.add_cut_diff(
                        sg_shot["code"],
                        sg_shot=sg_shot,
                        edit=None,
                        sg_cut_item=sg_cut_item,
                    )
            else:
                self._logger.debug("Discarding list for old shot key %s" % old_shot_key)
                # We can discard the list for this shot
                del self._cut_diffs[old_shot_key]
        elif count == 1:
            self._logger.debug("Single entry for old shot key %s" % old_shot_key)
            # This guy is alone now, so not repeated
            self._cut_diffs[old_shot_key][0].set_repeated(False)

        # If the cut diff was repeated, default back to non repeated
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
            if count == 1 and not self._cut_diffs[new_shot_key][0].edit:
                self._logger.debug("Single omitted entry for new shot key %s" % new_shot_key)
                # If only one entry, that could be an omitted shot ( no edit )
                # in that case the shot is not omitted anymore
                cdiff = self._cut_diffs[new_shot_key].pop()
                self.delete_cut_diff.emit(cdiff)
                # Recompute totals with the removed cut diff
                self.cut_diff_type_changed(cdiff, cdiff.diff_type, None)
                cut_diff.set_sg_shot(cdiff.sg_shot)
                cut_diff.set_sg_cut_item(cdiff.sg_cut_item)
                self._cut_diffs[new_shot_key].append(cut_diff)
            else:
                self._logger.debug("Adding new entry for new shot key %s" % new_shot_key)
                # SG shot and cut item are shared by all entries in this list
                cdiff = self._cut_diffs[new_shot_key][0]
                cut_diff.set_sg_shot(cdiff.sg_shot)
                cut_diff.set_sg_cut_item(cdiff.sg_cut_item)
                # Append and flag everything as repeated
                self._cut_diffs[new_shot_key].append(cut_diff)
                for cdiff in self._cut_diffs[new_shot_key]:
                    cdiff.set_repeated(True)
        else:
            self._logger.debug("Creating single entry for new shot key %s" % new_shot_key)
            self._cut_diffs[new_shot_key] = ShotCutDiffList(cut_diff)
        cut_diff.check_changes()
        self._recompute_counts()

    @QtCore.Slot(CutDiff, int, int)
    def cut_diff_type_changed(self, cut_diff, old_type, new_type):
        """
        Recompute internal totals when a cut diff type changed
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
                "Couldn't retrieve cut diff type %s in counts (new type : %s)" % (
                    old_type, new_type,
                )
            )
        else:
            self._counts[old_type] -= 1
            if self._counts[old_type] == 0:
                del self._counts[old_type]
        if new_type is not None:  # None is used when some cut diff are deleted
            if new_type in self._counts:
                self._counts[new_type] += 1
            else:
                self._counts[new_type] = 1
        self.totals_changed.emit()

    @property
    def rescans_count(self):
        """
        Return the number of entries needing a rescan
        """
        return self._rescans_count

    @property
    def repeated_count(self):
        """
        Return the number of entries which share their shot with another entry
        """
        return sum([len(self._cut_diffs[x]) for x in self._cut_diffs if len(self._cut_diffs[x]) > 1])

    def count_for_type(self, diff_type):
        """
        Return the number of entries for the given CutDiffType

        :param diff_type: A CutDiffType
        """
        return self._counts.get(diff_type, 0)

    def edits_for_type(self, diff_type, just_earliest=False):
        """
        Return the CutDiff instances for the given CutDiffType

        :param diff_type: A CutDiffType
        :param just_earliest: Whether or not all matching CutDiff should be
                              returned or just the earliest(s)
        """
        for name, items in self._cut_diffs.iteritems():
            for item in items:
                if item.interpreted_diff_type == diff_type and (not just_earliest or item.is_earliest()):
                    yield item

    def has_shot(self, shot_name):
        """
        Return True if there is already an entry in this summary for the given shot

        :param shot_name: A shot name, as a string
        """
        return shot_name.lower() in self._cut_diffs

    def diffs_for_shot(self, shot_name):
        """
        Return the CutDiff(s) list for the given shot, if any.

        :param shot_name: A shot name, as a string
        """
        return self._cut_diffs.get(shot_name.lower())

    def _recompute_counts(self):
        """
        Recompute internal counts from Cut differences
        """
        self._counts = {}
        for k, v in self._cut_diffs.iteritems():
            _, _, _, _, shot_diff_type = v.get_shot_values()
            if shot_diff_type in [
                _DIFF_TYPES.NEW,
                _DIFF_TYPES.OMITTED,
                _DIFF_TYPES.REINSTATED,
                _DIFF_TYPES.RESCAN
            ]:
                # We count these per shots
                if shot_diff_type in self._counts:
                    self._counts[shot_diff_type] += 1
                else:
                    self._counts[shot_diff_type] = 1
            else:
                # We count others per entries
                for cut_diff in v:
                    # We don't use cut_diff.interpreted_type here, as it will
                    # loop over all siblings, repeated shots cases are handled
                    # with the shot_diff_type
                    diff_type = self._interpreted_diff_type(cut_diff.diff_type)
                    if diff_type in self._counts:
                        self._counts[diff_type] += 1
                    else:
                        self._counts[diff_type] = 1
        # Legacy thing : rescan count was once not handled with a diff type
        # so keep updating it until all references to it is removed from the
        # code
        self._rescans_count = self._counts.get(_DIFF_TYPES.RESCAN, 0)
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
        Return the total number of entries in this summary
        """
        return sum([len(self._cut_diffs[k]) for k in self._cut_diffs], 0)

    def __iter__(self):
        """
        Iterate other shots for this summary
        """
        for name in self._cut_diffs.keys():
            yield name

    def __getitem__(self, key):
        """
        Return CutDiffs list for a given shot
        """
        return self._cut_diffs.get(key.lower())

    def iteritems(self):
        """
        Iterate over shot names for this summary, yielding (name, CutDiffs list)
        tuple
        """
        for name, items in self._cut_diffs.iteritems():
            yield (name, items)

    def get_report(self, title, sg_links):
        """
        Build a text report for this summary, highlighting changes

        :param title: A title for the report
        :param sg_links: Shotgun URLs to display in the report as links
        :return: A subject, body tuple, as strings
        """
        # Body should look like that :
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

        subject = "Sequence Cut Summary changes on %s" % title

        cut_changes_details = [
            "%s - %s" % (
                edit.name, ",".join(edit.reasons)
            ) for edit in sorted(
                self.edits_for_type(_DIFF_TYPES.CUT_CHANGE),
                key=lambda x: x.new_cut_order
            )
        ]
        rescan_details = [
            "%s - %s" % (
                edit.name, ",".join(edit.reasons)
            ) for edit in sorted(
                self.edits_for_type(_DIFF_TYPES.RESCAN),
                key=lambda x: x.new_cut_order
            )
        ]
        no_link_details = [
            edit.version_name for edit in sorted(
                self.edits_for_type(_DIFF_TYPES.NO_LINK),
                key=lambda x: x.new_cut_order
            )
        ]
        body = _BODY_REPORT_FORMAT % (
            # Let the user know that something is potentially wrong
            "WARNING, following edits couldn't be linked to any shot :\n%s\n" % (
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
