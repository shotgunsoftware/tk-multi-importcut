# Copyright (c) 2021 Autodesk, Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the ShotGrid Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the ShotGrid Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk, Inc.

from .ui.cut_card import Ui_CutCard
from .constants import _COLORS, _STATUS_COLORS
from .card_widget import CardWidget


class CutCard(CardWidget):
    """
    Widget displaying a Flow Production Tracking Cut
    """

    def __init__(self, parent, sg_cut):
        """
        Instantiate a new CutCard for the given Flow Production Tracking Cut

        :param parent: A parent QWidget
        :param sg_cut: A Flow Production Tracking cut, as a dictionary, to display
        """
        super().__init__(parent, sg_cut, Ui_CutCard)

        revision_number = self.sg_cut["revision_number"]
        if revision_number:
            self.ui.title_label.setText(
                "<big><b>%s_%03d</b></big>" % (self.sg_cut["code"], revision_number)
            )
        else:
            self.ui.title_label.setText(
                "<big><b>%s</b></big> (No Revision Number)" % (self.sg_cut["code"])
            )
        if self.sg_cut["_display_status"]:
            self.ui.status_label.setText(
                "<b><font color=%s>%s</font></b>"
                % (
                    _STATUS_COLORS.get(self.sg_cut["sg_status_list"], _COLORS["lgrey"]),
                    self.sg_cut["_display_status"]["name"].upper(),
                )
            )
        else:
            self.ui.status_label.setText(self.sg_cut["sg_status_list"])

        self.ui.date_label.setText(
            self.sg_cut["created_at"].strftime("%m/%d/%y %I:%M %p")
        )
        if self.sg_cut["description"]:
            self.setToolTip(self.sg_cut["description"])
        self.ui.details_label.setVisible(False)
        self.set_thumbnail(":/tk_multi_importcut/sg_sequence_thumbnail.png")

    @property
    def sg_cut(self):
        """
        Returns the PTR cut attached to this card

        :returns: A PTR Cut dictionary
        """
        return self._sg_entity
