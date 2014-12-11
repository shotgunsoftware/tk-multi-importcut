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

from .cut_diff import CutDiff, _DIFF_TYPES

_BODY_REPORT_FORMAT = """

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

class CutSummary(QtCore.QObject):
    """
    A list of cut differences, stored in CutDiff instances
    """
    new_cut_diff = QtCore.Signal(CutDiff)
    def __init__(self):
        """
        Create a new empty CutSummary
        """
        super(CutSummary,self).__init__()
        self._cut_diffs = {}
        self._counts = {}
        self._rescans_count = 0
        self._repeated_count = 0

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
        diff_type = cut_diff.diff_type
        if diff_type in self._counts:
            self._counts[diff_type] += 1
        else:
            self._counts[diff_type] = 1

        if cut_diff.need_rescan:
            self._rescans_count += 1
        # Use a lower case key, as shot names we retrieve from EDLs
        # can be upper cases, but actual SG shots be lower cases
        shot_key = shot_name.lower()
        if shot_key in self._cut_diffs:
            self._repeated_count += 1
            self._cut_diffs[shot_key].append(cut_diff)
            for cdiff in self._cut_diffs[shot_key]:
                cdiff.set_repeated(True)
        else:
            self._cut_diffs[shot_key] = [cut_diff]
        self.new_cut_diff.emit(cut_diff)
        return cut_diff

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

        cut_changes_details = ["%s - %s" % ( edit.name, ",".join(edit.reasons)) for edit in self.edits_for_type(_DIFF_TYPES.CUT_CHANGE)]
        rescan_details = ["%s - %s" % ( edit.name, ",".join(edit.reasons)) for edit in self.edits_for_type(_DIFF_TYPES.RESCAN)]
        body = _BODY_REPORT_FORMAT % (
            " , ".join(sg_links),
            title,
            self.count_for_type(_DIFF_TYPES.NEW),
            "\n".join([edit.name for edit in self.edits_for_type(_DIFF_TYPES.NEW)]),
            self.count_for_type(_DIFF_TYPES.OMITTED),
            "\n".join([edit.name for edit in self.edits_for_type(_DIFF_TYPES.OMITTED)]),
            self.count_for_type(_DIFF_TYPES.REINSTATED),
            "\n".join([edit.name for edit in self.edits_for_type(_DIFF_TYPES.REINSTATED)]),
            self.count_for_type(_DIFF_TYPES.CUT_CHANGE),
            "\n".join(cut_changes_details),
            self.count_for_type(_DIFF_TYPES.RESCAN),
            "\n".join(rescan_details),
        )
        return subject, body


