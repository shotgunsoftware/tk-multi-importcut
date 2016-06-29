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
import tempfile
import os

from .ui.cut_diff_card import Ui_CutDiffCard
from .cut_diff import CutDiff, _DIFF_TYPES
from .downloader import DownloadRunner
from .constants import _COLORS

# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
from sgtk.platform.qt import QtCore, QtGui
edl = sgtk.platform.import_framework("tk-framework-editorial", "edl")

# diff_type property values which are set on the widget
# and can be use in a style sheet
_DIFF_TYPES_PROPERTIES = {
    _DIFF_TYPES.NEW: "new",
    _DIFF_TYPES.OMITTED: "omitted",
    _DIFF_TYPES.REINSTATED: "reinstated",
    _DIFF_TYPES.RESCAN: "rescan_needed",
    _DIFF_TYPES.CUT_CHANGE: "cut_change",
    _DIFF_TYPES.NO_CHANGE: "no_change",
    _DIFF_TYPES.NO_LINK: "no_link",
    _DIFF_TYPES.NEW_IN_CUT: "new_in_cut",
    _DIFF_TYPES.OMITTED_IN_CUT: "omitted",
}

# Format string for tooltips
_TOOL_TIP_FORMAT = """
Shot :
\t%s
Version :
\t%s
Cut Item :
\t%s
Edit :
\t%s
"""


class CutDiffCard(QtGui.QFrame):
    """
    A widget showing cut differences
    """
    # Emitted when the CutDiff instance changed its type
    type_changed = QtCore.Signal()
    # A Signal to discard pending download
    discard_download = QtCore.Signal()

    def __init__(self, parent, cut_diff):
        """
        Instantiate a new cut diff card for the given CutDiff instance
        :param parent: A parent QWidget for this widget
        :param cut_diff: A CutDiff instance
        """
        super(CutDiffCard, self).__init__(parent)
        self._cut_diff = cut_diff
        self.ui = Ui_CutDiffCard()
        self.ui.setupUi(self)

        self._thumbnail_requested = False
        cut_diff.type_changed.connect(self.diff_type_changed)
        cut_diff.repeated_changed.connect(self.repeated_changed)
        self._set_ui_values()

    def set_property(self, name, value):
        """
        Set the given property to the given value and ensure styling
        is refreshed so the property is taken into account from the
        style sheet
        :param name: An arbitrary property
        :param value: An arbitrary value
        """
        self.setProperty(name, value)
        # We need to refresh ourself and a couple of children
        # widgets
        widgets = [
            self,
            self.ui.shot_name_line,
            self.ui.icon_label,
            self.ui.version_name_label,
            self.ui.status_label
        ]
        for w in widgets:
            self.style().unpolish(w)
            self.style().polish(w)

    def _set_ui_values(self):
        """
        Set UI values, colors, etc ... from the CutDiff instance being displayed
        """
        self.set_property("diff_type", _DIFF_TYPES_PROPERTIES[self._cut_diff.diff_type])
        self.set_property("repeated", self._cut_diff.repeated)
        # Shot name widget
        shot_name_tooltip = []
        if self._cut_diff.name:
            self.ui.shot_name_line.set_property("valid", True)
            self.ui.shot_name_line.setText("%s" % self._cut_diff.name)
        else:
            self.ui.shot_name_line.set_property("valid", False)
            self.ui.shot_name_line.setText("")
        self.ui.shot_name_line.value_changed.connect(self.shot_name_edited)
        if not self._cut_diff.is_name_editable:
            shot_name_tooltip.append("Shot name is not editable")
            self.ui.shot_name_line.setReadOnly(True)
        else:
            self.ui.shot_name_line.setReadOnly(False)
        if self._cut_diff.repeated:
            shot_name_tooltip.append("Shot is repeated")
        self.ui.shot_name_line.setToolTip("\n".join(shot_name_tooltip))
        # Cut order
        new_cut_order = self._cut_diff.new_cut_order or 0
        old_cut_order = self._cut_diff.cut_order or 0
        cut_order = new_cut_order or old_cut_order
        # note: leaving this in here in case we decide to switch back to the old behavior
        # self.set_property("cut_order_changed", bool(old_cut_order != new_cut_order))
        self.set_property("cut_order_changed", False)

        self.ui.icon_label.set_text(
            cut_order,
            None,  # use default color from styling
            bool(self._cut_diff.diff_type == _DIFF_TYPES.OMITTED)
        )
        # Difference and reasons
        diff_type_label = self._cut_diff.diff_type_label
        reasons = ", ".join(self._cut_diff.reasons)
        if diff_type_label:
            if reasons:
                self.ui.status_label.setText("<b>%s :</b> %s" % (diff_type_label, reasons))
            else:
                self.ui.status_label.setText("<b>%s</b>" % diff_type_label)
        else:
            self.ui.status_label.setText("%s" % reasons)

        sg_version = self._cut_diff.sg_version
        self.ui.version_name_label.setToolTip(None)
        if not sg_version:
            # No Version
            self.ui.version_name_label.setText(self._cut_diff.version_name or "No Version")
        elif sg_version.get("entity.Shot.code") != self._cut_diff.name:
            # Version linked to another shot
            self.ui.version_name_label.setText("<font color=%s>%s</font>" % (
                _COLORS["sg_red"],
                self._cut_diff.version_name,
            ))
            self.ui.version_name_label.setToolTip(
                "Version %s is linked to Shot %s, instead of %s" % (
                    self._cut_diff.version_name,
                    sg_version.get("entity.Shot.code"),
                    self._cut_diff.name,
                )
            )
        else:
            self.ui.version_name_label.setText(self._cut_diff.version_name)

        value = self._cut_diff.shot_head_in
        new_value = self._cut_diff.new_head_in
        self.display_values(self.ui.shot_head_in_label, new_value, value)

        value = self._cut_diff.shot_tail_out
        new_value = self._cut_diff.new_tail_out
        self.display_values(self.ui.shot_tail_out_label, new_value, value)

        value = self._cut_diff.cut_in
        new_value = self._cut_diff.new_cut_in
        self.display_values(self.ui.cut_in_label, new_value, value)

        value = self._cut_diff.cut_out
        new_value = self._cut_diff.new_cut_out
        self.display_values(self.ui.cut_out_label, new_value, value)

        value = self._cut_diff.head_duration
        new_value = self._cut_diff.new_head_duration
        self.display_values(self.ui.head_duration_label, new_value, value)

        value = self._cut_diff.duration
        new_value = self._cut_diff.new_duration
        self.display_values(self.ui.cut_duration_label, new_value, value)

        value = self._cut_diff.tail_duration
        new_value = self._cut_diff.new_tail_duration
        self.display_values(self.ui.tail_duration_label, new_value, value)

        self.set_tool_tip()

        self.set_thumbnail(":/tk_multi_importcut/sg_shot_thumbnail.png")

    @QtCore.Slot(str)
    def new_thumbnail(self, path):
        """
        Called when a new thumbnail is available for this card
        """
        self.set_thumbnail(path)

    @QtCore.Slot(CutDiff, int, int)
    def diff_type_changed(self, cut_diff, old_type, new_type):
        """
        Called when the diff type changed for the CutDiff being displayed

        Some parameter are ignored as we have the CutDiff instance as member
        of our class.

        :param cut_diff: A CutDiff instance
        :param old_type: The old type for the CutDiff instance
        :param new_type: The new type for the CutDiff instance
        """
        self._set_ui_values()
        self.type_changed.emit()
        # The linked sg version might have changed so blindly ask for a thumbnail
        # even if it actually didn't change. This is asynchronous so it shouldn't
        # harm to request the same thumbnail again. If it is, then sg version
        # changes should be handled in a dedicated slot and thumbnail requests
        # issued from it
        self.retrieve_thumbnail()

    @QtCore.Slot(CutDiff, int, int)
    def repeated_changed(self, cut_diff, old_repeated, new_repeated):
        """
        Called when the repeated changed for the CutDiff being displayed

        Some parameter are ignored as we have the CutDiff instance as member
        of our class.
        :param cut_diff: A CutDiff instance
        :param old_repeated: The old repeated value for the CutDiff instance
        :param new_type: The new repeated value for the CutDiff instance
        """
        self._set_ui_values()

    @QtCore.Slot(str)
    def shot_name_edited(self, value):
        """
        Called when the shot name was edited
        :param value: The value from the widget
        """
        if value != self._cut_diff.name:
            self._cut_diff.set_name(value)
        if not self._cut_diff.name:
            self.ui.shot_name_line.set_property("valid", False)

    @property
    def cut_order(self):
        """
        Return a cut order that can be used to sort cards together
        :returns: An integer
        """
        if self._cut_diff.new_cut_order is not None:
            return int(self._cut_diff.new_cut_order)
        if self._cut_diff.cut_order is not None:
            return int(self._cut_diff.cut_order)
        return -1

    @property
    def cut_diff(self):
        """
        Return the CutDiff instance this widget is showing
        :returns: A CutDiff instance
        """
        return self._cut_diff

    def __getattr__(self, attr_name):
        """
        Allow access to attached cut diff, it will be called by Python only
        if the requested attribute is not available on this instance

        :param attr_name: An attribute name, as a string
        """
        return getattr(self._cut_diff, attr_name)

    def display_values(self, widget, new_value, old_value):
        """
        Format the text for the given widget ( typically a QLabel ), comparing
        the old value to the new one, displaying only one of them if the two values
        are equal, coloring them otherwise

        :param widget: The widget used to display the values, typically a QLabel
        :param new_value: New value retrieved from the cut being imported
        :param old_value: Previous value retrieved from a former cut import
        """
        if self._cut_diff.diff_type in [_DIFF_TYPES.NEW]:
            widget.setText("<font color=%s>%s</font>" % (_COLORS["lgrey"], new_value))
        elif self._cut_diff.diff_type in [_DIFF_TYPES.OMITTED, _DIFF_TYPES.OMITTED_IN_CUT]:
            if old_value is not None:
                widget.setText("<font color=%s>%s</font>" % (_COLORS["lgrey"], old_value))
            else:
                # Old values are retrieved from cut items,
                # we can have omitted shots without cut items
                widget.setText("<font color=%s>%s</font>" % (_COLORS["lgrey"], ""))
        else:
            if new_value != old_value:
                if old_value is not None:
                    widget.setText("<font color=%s>%s</font> <font color=%s>(%s)</font>" % (
                        _COLORS["sg_red"], new_value,
                        _COLORS["lgrey"], old_value
                    ))
                else:
                    widget.setText(str(new_value))
            else:
                widget.setText("<font color=%s>%s</font>" % (_COLORS["lgrey"], new_value))

    def set_tool_tip(self):
        """
        Build a toolitp displaying details about this cut difference and attach
        it to the icon widget
        """
        shot_details, cut_item_details, version_details, edit_details = self._cut_diff.summary()
        msg = _TOOL_TIP_FORMAT % (
            shot_details,
            version_details,
            cut_item_details,
            edit_details
        )
        self.ui.icon_label.setToolTip(msg)

    def showEvent(self, event):
        """
        Request an async thumbnail download on first expose, if a thumbnail is
        avalaible in SG.
        """
        if self._thumbnail_requested:
            event.ignore()
            return

        self._thumbnail_requested = True
        self.retrieve_thumbnail()
        event.ignore()

    def closeEvent(self, evt):
        """
        Discard downloads when the widget is removed
        """
        self.discard_download.emit()
        evt.accept()

    def retrieve_thumbnail(self):
        """
        Check if a SG version can be retrieved from the CutDiff, request an
        asynchronous thumbnail download if it is the case
        """
        thumb_url = None
        if self._cut_diff.sg_version and self._cut_diff.sg_version.get("image"):
            thumb_url = self._cut_diff.sg_version["image"]
        elif self._cut_diff.sg_shot and self._cut_diff.sg_shot.get("image"):
            thumb_url = self._cut_diff.sg_shot["image"]
        if thumb_url:
            f, path = tempfile.mkstemp()
            os.close(f)
            downloader = DownloadRunner(
                sg_attachment=thumb_url,
                path=path,
            )
            downloader.file_downloaded.connect(self.new_thumbnail)
            self.discard_download.connect(downloader.abort)
            downloader.queue()

    def set_thumbnail(self, thumb_path):
        """
        Build a pixmap from the given file path and use it as icon, resizing it to
        fit into the widget icon size

        :param thumb_path: Full path to an image to use as thumbnail
        """
        size = self.ui.icon_label.size()
        ratio = size.width() / float(size.height())
        pixmap = QtGui.QPixmap(thumb_path)
        if pixmap.isNull():
            return
        psize = pixmap.size()
        pratio = psize.width() / float(psize.height())
        if pratio > ratio:
            self.ui.icon_label.setPixmap(
                pixmap.scaledToWidth(size.width(), mode=QtCore.Qt.SmoothTransformation)
            )
        else:
            self.ui.icon_label.setPixmap(
                pixmap.scaledToHeight(size.height(), mode=QtCore.Qt.SmoothTransformation)
            )
