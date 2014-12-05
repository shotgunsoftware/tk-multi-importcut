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

class CutSummary(QtCore.QObject):
    new_cut_diff = QtCore.Signal(CutDiff)
    def __init__(self):
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
        return self._rescans_count

    @property
    def repeated_count(self):
        return self._repeated_count

    def count_for_type(self, diff_type):
        return self._counts.get(diff_type, 0)

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
        return sum([len(self._cut_diffs[k]) for k in self._cut_diffs], 0)

    def __iter__(self):
        for name in self._cut_diffs.keys():
            yield name

    def __getitem__(self, key):
        return self._cut_diffs.get(key.lower())

    def iteritems(self):
        for name, items in self._cut_diffs.iteritems():
            yield (name, items)


