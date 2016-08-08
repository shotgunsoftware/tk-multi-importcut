# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import re
import sgtk

from .ui.create_entity_dialog import Ui_create_entity_dialog
# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
from sgtk.platform.qt import QtCore, QtGui
from .logger import get_logger


class CreateEntityDialog(QtGui.QDialog):
    """
    This dialog is available by clicking the "New [Entity]" button on the select
    entities page. A user can enter an entity name with a description. On submit
    the entity is created and the stacked widget moves to the next page.
    """
    create_entity = QtCore.Signal(str, dict)

    def __init__(self, entity_type, sg_project, parent=None):
        """
        Instantiate a new dialog
        :param parent: a QWidget
        """
        super(CreateEntityDialog, self).__init__(parent)
        self._logger = get_logger()
        self.ui = Ui_create_entity_dialog()
        self.ui.setupUi(self)
        self.setModal(True)
        self._app = sgtk.platform.current_bundle()
        self._sg = self._app.shotgun
        self._ctx = self._app.context
        self._entity_type = entity_type
        self._project = sg_project

        entity_type_name = sgtk.util.get_entity_type_display_name(
            self._app.sgtk, entity_type,
        )
        self.setWindowTitle("Create %s" % entity_type_name)

        # Set text on labels and buttons
        self.ui.create_new_entity_label.setText("%s" % entity_type_name)
        self.ui.create_entity_button.setText("Create %s" % entity_type_name)
        self.ui.entity_name_label.setText("%s name" % entity_type_name)
        self.ui.cancel_button.clicked.connect(self.close_dialog)
        self.ui.create_entity_button.clicked.connect(self.emit_create_entity)

        self.entity_statuses = self._app.shotgun.schema_field_read(entity_type)[
                "sg_status_list"]["properties"]["valid_values"]["value"]
        self.ui.status_combo_box.addItem("")
        for status in self.entity_statuses:
            self.ui.status_combo_box.addItem(status)

        self.ui.project_name_label.setText(sg_project["name"])

    def emit_create_entity(self):
        """
        Send out request to create entity, then close the dialog.
        """
        entity_name = self.ui.entity_name_line_edit.text().encode("utf-8")
        entity_description = self.ui.description_line_edit.text().encode("utf-8")
        status_index = self.ui.status_combo_box.currentIndex()
        field_data = {
            "project": self._project,
            "code": entity_name,
            "description": entity_description
        }
        # if the status_index is 0, create the entity without specifying the
        # sg_status_list, and so use whatever the default status in Shogun is,
        # otherwise set sg_status_list to the currently selected status.
        if status_index:
            # -1 here to account for the empty item added to the status_combo_box.
            field_data["sg_status_list"] = self.entity_statuses[status_index - 1]
        self.create_entity.emit(
            self._entity_type,
            field_data
        )
        self.close_dialog()

    @QtCore.Slot()
    def close_dialog(self):
        """
        Close the dialog on Create [Entity] or Cancel.
        """
        self.close()
