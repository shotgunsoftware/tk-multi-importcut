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
        self._logger=get_logger()
        self._min_cut_in = None
        self._max_cut_out = None
        self._min_cut_order = None
        self._min_tc_cut_in = None
        self._max_tc_cut_out = None
        self._earliest_entry = None
        self._latest_entry = None
        # Values above are populated in the append call below
        self.append(cut_diff)

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
        self._min_cut_in = None
        self._max_cut_out = None
        self._min_cut_order = None
        self._min_tc_cut_in = None
        self._max_tc_cut_out = None
        self._earliest_entry = None
        self._latest_entry = None
        # And recompute them from what is left
        for cdiff in self:
            self._update_min_and_max(cdiff)

    @property
    def earliest(self):
        """
        Return the entry with the earliest tc cut in from our list

        :returns: A CutDiff instance, or None
        """
        return self._earliest_entry

    @property
    def latest(self):
        """
        Return the entry with latest tc cut out from out list

        :returns: A CutDiff instance, or None
        """
        return self._latest_entry

    def _update_min_and_max(self, cut_diff):
        """
        Update min and max values from the given cut diffence

        :param cut_diff: A CutDiff instance
        """
        tc_cut_in = cut_diff.new_tc_cut_in
        if tc_cut_in is not None and (self._min_tc_cut_in is None or tc_cut_in.to_frame() < self._min_tc_cut_in.to_frame()):
            self._min_tc_cut_in = tc_cut_in
            old_earliest_entry = self._earliest_entry
            self._earliest_entry = cut_diff
        tc_cut_out = cut_diff.new_tc_cut_out
        if tc_cut_out is not None and (self._max_tc_cut_out is None or tc_cut_out.to_frame() > self._max_tc_cut_out.to_frame()):
            self._max_tc_cut_out = tc_cut_out
            self._latest_entry = cut_diff
        self._logger.info("Min tc cut in is %s" % self._min_tc_cut_in)
        self._logger.info("Max tc cut out is %s" % self._max_tc_cut_out)
        if cut_diff.new_cut_order is not None and (self._min_cut_order is None or cut_diff.new_cut_order < self._min_cut_order):
            self._min_cut_order = cut_diff.new_cut_order
        if cut_diff.new_cut_in is not None and ( self._min_cut_in is None or cut_diff.new_cut_in < self._min_cut_in):
            self._min_cut_in = cut_diff.new_cut_in
        if cut_diff.new_cut_out is not None and ( self._max_cut_out is None or cut_diff.new_cut_out > self._max_cut_out):
            self._max_cut_out = cut_diff.new_cut_out

class CutSummary(QtCore.QObject):
    """
    A list of cut differences, stored in CutDiff instances
    """
    new_cut_diff = QtCore.Signal(CutDiff)
    totals_changed = QtCore.Signal()
    delete_cut_diff = QtCore.Signal(CutDiff)

    def __init__(self):
        """
        Create a new empty CutSummary
        """
        super(CutSummary,self).__init__()
        self._cut_diffs = {}
        self._counts = {}
        self._rescans_count = 0
        self._repeated_count = 0
        self._logger=get_logger()

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
        diff_type = cut_diff.diff_type
        if diff_type in self._counts:
            self._counts[diff_type] += 1
        else:
            self._counts[diff_type] = 1

        if cut_diff.need_rescan:
            self._rescans_count += 1
        # Use a lower case key, as shot names we retrieve from EDLs
        # can be upper cases, but actual SG shots be lower cases
        shot_key = shot_name.lower() if shot_name else "_no_shot_name_"
        if shot_key in self._cut_diffs:
            self._repeated_count += 1
            self._cut_diffs[shot_key].append(cut_diff)
            for cdiff in self._cut_diffs[shot_key]:
                cdiff.set_repeated(True)
        else:
            self._cut_diffs[shot_key] = ShotCutDiffList(cut_diff)
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
        new_shot_key=new_name.lower() if new_name else "_no_shot_name_"
        old_shot_key=old_name.lower() if old_name else "_no_shot_name_"
        if new_shot_key == old_shot_key:
            return

        # Remove it from our internal shot / cut_diff dictionary
        if old_shot_key not in self._cut_diffs:
            raise RuntimeError("Can't retrieve shot %s in internal list" % old_shot_key)
        self._cut_diffs[old_shot_key].remove(cut_diff)
        count=len(self._cut_diffs[old_shot_key])
        if count==0:
            self._logger.debug("No more entry for old shot key %s" % old_shot_key)
            # If we have a SG shot, it is now an omitted one
            if cut_diff.sg_shot:
                self._logger.debug("Adding omitted entry for old shot key %s" % old_shot_key)
                sg_shot=cut_diff.sg_shot
                sg_cut_item=cut_diff.sg_cut_item
                self.add_cut_diff(
                        sg_shot["code"],
                        sg_shot=sg_shot,
                        edit=None,
                        sg_cut_item=sg_cut_item,
                    )
            else:
                self._logger.debug("Discarding list for old shot key %s" % old_shot_key)
                # We can discard the list for this shot
                del self._cut_diffs[old_shot_key]
        elif count==1:
            self._logger.debug("Single entry for old shot key %s" % old_shot_key)
            # This guy is alone now, so not repeated
            self._cut_diffs[old_shot_key][0].set_repeated(False)

        # If the cut diff was repeated, default back to non repeated
        if cut_diff.repeated:
            self._repeated_count -= 1
            cut_diff.set_repeated(False)

        # These are not valid anymore
        cut_diff.set_sg_shot(None)
        cut_diff.set_sg_cut_item(None)

        # Add it back with the new name
        if new_shot_key in self._cut_diffs:
            for cdiff in self._cut_diffs[new_shot_key]:
                self._logger.debug("%s %s %s %s" % cdiff.summary())
            count=len(self._cut_diffs[new_shot_key])
            self._logger.debug("%d Entries for new shot key %s" % (count, new_shot_key))
            if count == 1 and not self._cut_diffs[new_shot_key][0].edit:
                self._logger.debug("Single omitted entry for new shot key %s" % new_shot_key)
                # If only one entry, that could be an omitted shot ( no edit )
                # in that case the shot is not omitted anymore
                cdiff=self._cut_diffs[new_shot_key].pop()
                self.delete_cut_diff.emit(cdiff)
                # Recompute totals with the removed cut diff
                self.cut_diff_type_changed(cdiff, cdiff.diff_type, None)
                cut_diff.set_sg_shot(cdiff.sg_shot)
                cut_diff.set_sg_cut_item(cdiff.sg_cut_item)
                self._cut_diffs[new_shot_key].append(cut_diff)
            else:
                self._logger.debug("Adding new entry for new shot key %s" % new_shot_key)
                # SG shot and cut item are shared by all entries in this list
                cdiff=self._cut_diffs[new_shot_key][0]
                cut_diff.set_sg_shot(cdiff.sg_shot)
                cut_diff.set_sg_cut_item(cdiff.sg_cut_item)
                # Append and flag everything as repeated
                self._repeated_count += 1
                self._cut_diffs[new_shot_key].append(cut_diff)
                for cdiff in self._cut_diffs[new_shot_key]:
                    cdiff.set_repeated(True)
        else:
            self._logger.debug("Creating single entry for new shot key %s" % new_shot_key)
            self._cut_diffs[new_shot_key] = ShotCutDiffList(cut_diff)
        cut_diff.check_changes()

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
        if old_type==new_type:
            return
        if old_type not in self._counts:
            raise RuntimeError("Couldn't retrieve cut diff type %s in counts" % old_type)
        self._counts[old_type] -= 1
        if self._counts[old_type]==0:
            del self._counts[old_type]
        if new_type is not None: # None is used when some cut diff are deleted
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
        return self._repeated_count

    def count_for_type(self, diff_type):
        """
        Return the number of entries for the given CutDiffType
        
        :param diff_type: A CutDiffType
        """
        return self._counts.get(diff_type, 0)

    def edits_for_type(self, diff_type):
        """
        Return the CutDiff instances for the given CutDiffType

        :param diff_type: A CutDiffType
        """
        for name, items in self._cut_diffs.iteritems():
            for item in items:
                if item.diff_type == diff_type:
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
        Iterate over shot names for this summary, yielding (name, CutDiffs list )
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
        #The changes in {Name of Cut/EDL} are as follows:
        #
        #5 New Shots
        #HT0500
        #HT0510
        #HT0520
        #HT0530
        #HT0540
        #
        #2 Omitted Shots
        #HT0050
        #HT0060
        #
        #1 Reinstated Shot
        #HT0110
        #
        #4 Cut Changes
        #HT0070 - Head extended 2 frs 
        #HT0080 - Tail extended 6 frs
        #HT0090 - Tail trimmed 5 frs
        #HT0100 - Head extended 5 frs
        #
        #1 Rescan Needed
        #HT0120 - Head extended 15 frs

        subject = "Sequence Cut Summary changes on %s" % title

        cut_changes_details = [
            "%s - %s" % (
                edit.name, ",".join(edit.reasons)
            ) for edit in sorted(
                self.edits_for_type(_DIFF_TYPES.CUT_CHANGE),
                key=lambda x : x.new_cut_order
            )
        ]
        rescan_details = [
            "%s - %s" % (
                edit.name, ",".join(edit.reasons)
            ) for edit in sorted(
                self.edits_for_type(_DIFF_TYPES.RESCAN),
                key=lambda x : x.new_cut_order
            )
        ]
        no_link_details = [
            edit.version_name for edit in sorted(
                self.edits_for_type(_DIFF_TYPES.NO_LINK),
                key=lambda x : x.new_cut_order
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
                    self.edits_for_type(_DIFF_TYPES.NEW),
                    key=lambda x : x.new_cut_order
                )
            ]),
            self.count_for_type(_DIFF_TYPES.OMITTED),
            "\n".join([
                edit.name for edit in sorted(
                    self.edits_for_type(_DIFF_TYPES.OMITTED),
                    key=lambda x : x.cut_order or -1
                )
            ]),
            self.count_for_type(_DIFF_TYPES.REINSTATED),
            "\n".join([
                edit.name for edit in sorted(
                    self.edits_for_type(_DIFF_TYPES.REINSTATED),
                    key=lambda x : x.new_cut_order
                )
            ]),
            self.count_for_type(_DIFF_TYPES.CUT_CHANGE),
            "\n".join(cut_changes_details),
            self.count_for_type(_DIFF_TYPES.RESCAN),
            "\n".join(rescan_details),
        )
        return subject, body


