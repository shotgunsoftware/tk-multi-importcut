# Copyright (c) 2021 Autodesk, Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the ShotGrid Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the ShotGrid Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk, Inc.

# Different steps in the wizard process
(
    _DROP_STEP,
    _PROJECT_STEP,
    _ENTITY_TYPE_STEP,
    _ENTITY_STEP,
    _CUT_STEP,
    _SUMMARY_STEP,
    _PROGRESS_STEP,
    _LAST_STEP,
) = range(8)

# Different timecode mapping mode
# Three mapping modes are available, which are only relevant for first
# imports:
# - Automatic: On first import, the timecode in is mapped to the Shot head in.
# - Absolute: On first import, timecode in is converted to an absolute frame
#             number.
# - Relative: On first import, timecode in is converted to an arbitrary frame
#             number specified through settings.
_ABSOLUTE_MODE, _AUTOMATIC_MODE, _RELATIVE_MODE = range(3)

# List of supported extensions for movies.
_VIDEO_EXTS = [".avi", ".m4v", ".mov", ".mp4", ".qt", ".webm"]

# List of supported extensions for Versions.
_VERSION_EXTS = _VIDEO_EXTS + [
    ".jpg",
    ".jpeg",
    ".mxf",
    ".omf",
    ".png",
    ".psd",
    ".tif",
    ".tiff",
]

# EDL file extension
_EDL_EXT = ".edl"

# Url that links to Import Cut documentation.
_DOCUMENTATION_URL = "https://help.autodesk.com/view/SGSUB/ENU/?guid=SG_Editorial_ed_import_cut_depth_html"

# Some colors used in various places
_COLORS = {
    "sg_blue": "#2C93E2",
    "sg_red": "#FC6246",
    "mid_blue": "#1B82D1",
    "green": "#57B510",
    "yellow": "#A1A51A",
    "lgrey": "#A5A5A5",
    "dgrey": "#666666",
    "dgreen": "#377500",
}
# Colors associated with some PTR statuses
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
    "image",
]
