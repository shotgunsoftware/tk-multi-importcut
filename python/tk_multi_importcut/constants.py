# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

# Different steps in the process
_DROP_STEP, _PROJECT_STEP, _ENTITY_TYPE_STEP, _ENTITY_STEP, _CUT_STEP, \
    _SUMMARY_STEP, _PROGRESS_STEP, _LAST_STEP = range(8)

# Different timecode mapping mode
_ABSOLUTE_MODE, _AUTOMATIC_MODE, _RELATIVE_MODE = range(3)

# List of supported extensions for movies
_VIDEO_EXTS = [".avi", ".m4v", ".mov", ".mp4", ".qt", ".webm"]

# Some colors used in various places
_COLORS = {
    "sg_blue" : "#2C93E2",
    "sg_red"  : "#FC6246",
    "mid_blue": "#1B82D1",
    "green"   : "#57B510",
    "yellow"  : "#A1A51A",
    "lgrey"   : "#A5A5A5",
    "dgrey"   : "#666666",
    "dgreen"  : "#377500",
}
# Colors associated with some SG statuses
_STATUS_COLORS = {
    "omt": _COLORS["sg_red"],
    "hld": _COLORS["sg_red"],
    "apr": _COLORS["green"],
    "fin": _COLORS["green"],
}
# Fields we need to retrieve on Shots
_SHOT_FIELDS = [
    "code",
    "sg_status_list",
    "sg_head_in",
    "sg_tail_out",
    "sg_cut_in",
    "sg_cut_out",
    "smart_head_in",
    "smart_tail_out",
    "smart_cut_in",
    "smart_cut_out",
    "sg_cut_order",
    "image"
]
