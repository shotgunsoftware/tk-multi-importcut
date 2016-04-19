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
import os
import sys
import sgtk
import logging
import logging.handlers
import tempfile
import ast

# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
from sgtk.platform.qt import QtCore, QtGui

from .widgets import DropAreaFrame, AnimatedStackedWidget
from .search_widget import SearchWidget
from .entity_line_widget import EntityLineWidget
from .extended_thumbnail import ExtendedThumbnail

# Custom widgets must be imported before importing the UI
from .ui.dialog import Ui_Dialog

from .processor import Processor
from .logger import BundleLogHandler, get_logger, ShortNameFilter
from .entity_types_view import EntityTypesView
from .projects_view import ProjectsView
from .entities_view import EntitiesView
from .cuts_view import CutsView
from .cut_diff import _DIFF_TYPES, CutDiff
from .cut_diffs_view import CutDiffsView
from .submit_dialog import SubmitDialog
from .settings_dialog import SettingsDialog
from .create_entity_dialog import CreateEntityDialog
from .downloader import DownloadRunner

# Different steps in the process
from .constants import _DROP_STEP, _PROJECT_STEP, _ENTITY_TYPE_STEP, _ENTITY_STEP
from .constants import _CUT_STEP, _SUMMARY_STEP, _PROGRESS_STEP, _LAST_STEP

# Supported movie file extensions
from .constants import _VIDEO_EXTS

# Different frame mapping modes
from .constants import _ABSOLUTE_MODE, _AUTOMATIC_MODE, _RELATIVE_MODE

settings = sgtk.platform.import_framework("tk-framework-shotgunutils", "settings")


def show_dialog(app_instance):
    """
    Shows the main dialog window.
    """
    # in order to handle UIs seamlessly, each toolkit engine has methods for launching
    # different types of windows. By using these methods, your windows will be correctly
    # decorated and handled in a consistent fashion by the system.

    # Create a settings manager where we can pull and push prefs later
    app_instance.user_settings = settings.UserSettings(sgtk.platform.current_bundle())

    # we pass the dialog class to this method and leave the actual construction
    # to be carried out by toolkit.
    app_instance.engine.show_dialog("Import Cut", app_instance, AppDialog)


def load_edl_for_entity(app_instance, edl_file_path, sg_entity, frame_rate):
    """
    Run the app with a pre-selected edl file and SG entity
    :param edl_file_path: Full path to an EDL file
    :param sg_entity: A SG entity dictionary as a string, e.g.
                      '{"code" : "001", "id" : 19, "type" : "Sequence"}'
    :param frame_rate: The frame rate for the EDL file
    """
    sg_entity_dict = None
    # Convert the string representation to a regular dict
    if sg_entity:
        sg_entity_dict = ast.literal_eval(sg_entity)
        if not isinstance(sg_entity_dict, dict):
            raise ValueError("Invalid SG entity %s" % sg_entity)

    app_instance.engine.show_dialog(
        "Import Cut",
        app_instance,
        AppDialog,
        edl_file_path=edl_file_path,
        sg_entity=sg_entity_dict,
        frame_rate=int(frame_rate),
    )


class AppDialog(QtGui.QWidget):
    """
    Main application dialog window
    """
    new_edl = QtCore.Signal(str)
    new_movie = QtCore.Signal(str)
    get_projects = QtCore.Signal()
    get_entities = QtCore.Signal(str)
    show_cuts_for_sequence = QtCore.Signal(dict)
    show_cut_diff = QtCore.Signal(dict)

    def __init__(self, edl_file_path=None, sg_entity=None, frame_rate=None):
        """
        Constructor
        :param edl_file_path: Full path to an EDL file
        :param sg_entity: An SG entity dictionary
        :param frame_rate: Use a specific frame rate for the import
        """
        # first, call the base class and let it do its thing.
        QtGui.QWidget.__init__(self)

        # now load in the UI that was created in the UI designer
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # most of the useful accessors are available through the Application class instance
        # it is often handy to keep a reference to this. You can get it via the following method:
        self._app = sgtk.platform.current_bundle()
        self._sg = self._app.shotgun
        self._ctx = self._app.context
        self._user_settings = self._app.user_settings
        self._got_projects = False
        self.checked_entity_button = None

        # todo: this is a tmp workaround. In the future we should validate all settings
        # on app launch and reset only the settings that are broken, waiting on direction
        # before building out the complete solution.
        reset_settings = False
        if self._user_settings.retrieve("reset_settings"):
            reset_settings = True

        # set defaults, but don't override user settings.
        if reset_settings or self._user_settings.retrieve("update_shot_statuses") is None:
            self._user_settings.store("update_shot_statuses", True)
        if reset_settings or self._user_settings.retrieve("use_smart_fields") is None:
            self._user_settings.store("use_smart_fields", False)
        if reset_settings or self._user_settings.retrieve("email_groups") is None:
            self._user_settings.store("email_groups", [])
        if reset_settings or self._user_settings.retrieve("omit_status") is None:
            # todo: this will break if these statuses don't exist in Shotgun
            # waiting for a decision about how to handle the case of missing statuses
            self._user_settings.store("omit_status", "omt")
        if reset_settings or self._user_settings.retrieve("reinstate_shot_if_status_is") is None:
            # todo: same comment as above
            self._user_settings.store("reinstate_shot_if_status_is", ["omt", "hld"])
        if reset_settings or self._user_settings.retrieve("reinstate_status") is None:
            self._user_settings.store("reinstate_status", "Previous Status")
        if reset_settings or self._user_settings.retrieve("default_frame_rate") is None:
            self._user_settings.store("default_frame_rate", "24")
        if reset_settings or self._user_settings.retrieve("timecode_to_frame_mapping") is None:
            self._user_settings.store("timecode_to_frame_mapping", _ABSOLUTE_MODE)
        if reset_settings or self._user_settings.retrieve("timecode_mapping") is None:
            self._user_settings.store("timecode_mapping", "00:00:00:00")
        if reset_settings or self._user_settings.retrieve("frame_mapping") is None:
            self._user_settings.store("frame_mapping", "1000")
        if reset_settings or self._user_settings.retrieve("default_head_in") is None:
            self._user_settings.store("default_head_in", "1001")
        if reset_settings or self._user_settings.retrieve("default_head_duration") is None:
            self._user_settings.store("default_head_duration", "8")
        if reset_settings or self._user_settings.retrieve("default_tail_duration") is None:
            self._user_settings.store("default_tail_duration", "8")

        if reset_settings:
            self._user_settings.store("reset_settings", False)

        self._busy = False
        # Current step being displayed
        self._step = 0

        # Selected sg entity per step : selection only happen in steps 1 and 2
        # but we create entries for all steps allowing to index the list
        # with the current step and blindly disable the select button on the
        # value for each step
        self._selected_sg_entity = [None]*(_LAST_STEP+1)

        # via the self._app handle we can for example access:
        # - The engine, via self._app.engine
        # - A Shotgun API instance, via self._app.shotgun
        # - A tk API instance, via self._app.tk

        # lastly, set up our very basic UI
        self.set_custom_style()
        self.set_logger(logging.INFO)

        CutDiff.retrieve_default_timecode_frame_mapping()

        # Keep this thread for UI stuff
        # Handle data and processong in a separate thread
        self._processor = Processor(frame_rate)

        self.new_edl.connect(self._processor.new_edl)
        self.new_movie.connect(self._processor.new_movie)
        self.get_projects.connect(self._processor.retrieve_projects)
        self.get_entities.connect(self._processor.retrieve_entities)
        self.show_cuts_for_sequence.connect(self._processor.retrieve_cuts)
        self.show_cut_diff.connect(self._processor.show_cut_diff)

        self._processor.valid_edl.connect(self.valid_edl)
        self._processor.valid_movie.connect(self.valid_movie)

        self._processor.step_done.connect(self.step_done)
        self._processor.step_failed.connect(self.step_failed)
        self._processor.got_busy.connect(self.set_busy)
        self._processor.got_idle.connect(self.set_idle)
        self.ui.stackedWidget.first_page_reached.connect(self._processor.reset)

        # Let's do something when something is dropped
        self.ui.drop_area_frame.something_dropped.connect(self.process_drop)

        # Instantiate a projects view handler
        self._projects_view = ProjectsView(self.ui.project_grid)
        self._projects_view.project_chosen.connect(self.show_entity_types)
        self._projects_view.selection_changed.connect(self.selection_changed)
        self._projects_view.new_info_message.connect(self.display_info_message)
        self._processor.new_sg_project.connect(self._projects_view.new_sg_project)
        self.ui.projects_search_line_edit.search_edited.connect(self._projects_view.search)
        self.ui.projects_search_line_edit.search_changed.connect(self._projects_view.search)

        # Instantiate a entity type view handler
        self._entity_types_view = EntityTypesView(self.ui.entity_types_layout)
        self._entity_types_view.new_info_message.connect(self.display_info_message)
        self._entity_types_view.selection_changed.connect(self.selection_changed)
        self._entity_types_view.entity_type_chosen.connect(self.show_entities)

        # Instantiate a entities view handler
        self._entities_view = EntitiesView(self.ui.sequence_grid)
        self._entities_view.sequence_chosen.connect(self.show_entity)
        self._entities_view.selection_changed.connect(self.selection_changed)
        self._entities_view.new_info_message.connect(self.display_info_message)
        self._processor.new_sg_entity.connect(self._entities_view.new_sg_entity)
        self._processor.new_sg_entity.connect(self._change_entity_button)
        self.ui.sequences_search_line_edit.search_edited.connect(self._entities_view.search)
        self.ui.sequences_search_line_edit.search_changed.connect(self._entities_view.search)

        # Instantiate a cuts view handler
        self._cuts_view = CutsView(self.ui.cuts_grid, self.ui.cuts_sort_button)
        self._cuts_view.show_cut_diff.connect(self.show_cut)
        self._cuts_view.selection_changed.connect(self.selection_changed)
        self._cuts_view.new_info_message.connect(self.display_info_message)
        self._processor.new_sg_cut.connect(self._cuts_view.new_sg_cut)
        self.ui.search_line_edit.search_edited.connect(self._cuts_view.search)
        self.ui.search_line_edit.search_changed.connect(self._cuts_view.search)

        # Instantiate a cut differences view handler
        self._cut_diffs_view = CutDiffsView(self.ui.cutsummary_list)
        self._cut_diffs_view.totals_changed.connect(self.set_cut_summary_view_selectors)
        self._cut_diffs_view.new_info_message.connect(self.display_info_message)
        self._processor.totals_changed.connect(self.set_cut_summary_view_selectors)
        self._processor.new_cut_diff.connect(self._cut_diffs_view.new_cut_diff)
        self._processor.delete_cut_diff.connect(self._cut_diffs_view.delete_cut_diff)

        # Cut summary view selectors
        self.ui.new_select_button.toggled.connect(
            lambda x: self._cut_diffs_view.set_display_summary_mode(x, _DIFF_TYPES.NEW))
        self.ui.cut_change_select_button.toggled.connect(
            lambda x: self._cut_diffs_view.set_display_summary_mode(x, _DIFF_TYPES.CUT_CHANGE))
        self.ui.omitted_select_button.toggled.connect(
            lambda x: self._cut_diffs_view.set_display_summary_mode(x, _DIFF_TYPES.OMITTED))
        self.ui.reinstated_select_button.toggled.connect(
            lambda x: self._cut_diffs_view.set_display_summary_mode(x, _DIFF_TYPES.REINSTATED))
        self.ui.rescan_select_button.toggled.connect(
            lambda x: self._cut_diffs_view.set_display_summary_mode(x, 100))
        self.ui.total_button.toggled.connect(
            lambda x: self._cut_diffs_view.set_display_summary_mode(x, -1))
        self.ui.only_vfx_check_box.toggled.connect(self._cut_diffs_view.display_vfx_cuts)

        # Ensure we land on the startup screen
        self.ui.stackedWidget.set_current_index(_DROP_STEP)
        self.set_ui_for_step(_DROP_STEP)

        self.ui.back_button.clicked.connect(self.previous_page)
        self.ui.next_button.clicked.connect(self.process_edl_mov)
        self.ui.create_entity_button.clicked.connect(self.create_entity_dialog)
        self.ui.stackedWidget.first_page_reached.connect(self.reset)
        self.ui.stackedWidget.currentChanged.connect(self.set_ui_for_step)
        self.ui.cancel_button.clicked.connect(self.close_dialog)
        self.ui.select_button.clicked.connect(self.select_button_callback)
        self.ui.reset_button.clicked.connect(self.do_reset)
        self.ui.email_button.clicked.connect(self.email_cut_changes)
        self.ui.submit_button.clicked.connect(self.import_cut)
        # We have a different settings button on each page of the stacked widget
        num_pages = self.ui.stackedWidget.count()
        if num_pages > 0:
            for i in range(1, num_pages):
                try:
                    eval("self.ui.settings_page_%s_button.clicked.connect(\
                        self.show_settings_dialog)" % i)
                except:
                    pass
        # Here we're dynamically creating link buttons on the ENTITY_STEP page,
        # as well as adding a Project type button.
        cut_link_field = "entity"
        schema = self._sg.schema_field_read("Cut", cut_link_field)
        entity_types = schema[cut_link_field]["properties"]["valid_types"]["value"]
        self._preload_entity_type = self._user_settings.retrieve("preload_entity_type")
        self._logger.info(self._preload_entity_type)
        if self._preload_entity_type not in entity_types:
            if self._preload_entity_type != "Project":
                self._preload_entity_type = None
        inc = 1
        for entity_type in entity_types:
            # This is a bit arbitrary, since it only messes up the gui, but it's probably
            # possible to display more like eight types, depending on the char length of each type.
            if inc > 5:
                self._logger.warning("Sorry, we can only display five link Entities at a time.")
                break
            entity_name = self._sg.schema_entity_read(entity_type)[entity_type]["name"]["value"]
            entity_link_button = QtGui.QPushButton(entity_name)
            entity_link_button.setObjectName("dynamic_button_%s" % inc)
            entity_link_button.setFlat(True)
            entity_link_button.setAutoExclusive(True)
            entity_link_button.setCheckable(True)
            # self._set_button_size(entity_link_button)
            entity_link_button.setFont(QtGui.QFont("SansSerif", 20))
            width = entity_link_button.fontMetrics().boundingRect(entity_name).width() + 7
            entity_link_button.setMaximumWidth(width)
            entity_link_button.clicked.connect(self._get_link_cb(entity_type, entity_link_button))
            # entity_link_button.setFont(QtGui.QFont("SansSerif", 14))
            # width = entity_link_button.fontMetrics().boundingRect(entity_name).width() + 7
            # entity_link_button.setMaximumWidth(width)
            if inc == 1:
                if self._preload_entity_type is None:
                    self._preload_entity_type = entity_type
                self.checked_entity_button = entity_link_button
                self.ui.entity_buttons_layout.addWidget(self.checked_entity_button, inc, 0)
                self.checked_entity_button.setChecked(True)
                # self.ui.dynamic_button_1.setChecked(True)
            else:
                self.ui.entity_buttons_layout.addWidget(entity_link_button, inc, 0)
                if self._preload_entity_type == entity_type:
                    entity_link_button.setChecked(True)
                    # self._change_entity_button({"mode_change": self._preload_entity_type})
            inc += 1
        project_link_button = QtGui.QPushButton("Project")
        project_link_button.setObjectName("dynamic_button_project")
        project_link_button.setFlat(True)
        project_link_button.setAutoExclusive(True)
        project_link_button.setCheckable(True)
        project_link_button.setFont(QtGui.QFont("SansSerif", 20))
        width = project_link_button.fontMetrics().boundingRect(entity_name).width() + 7
        project_link_button.setMaximumWidth(width)
        project_link_button.clicked.connect(
            lambda: self.link_button_clicked("Project", project_link_button))
        self.ui.entity_buttons_layout.addWidget(project_link_button, inc, 0)
        if self._preload_entity_type == "Project":
            project_link_button.setChecked(True)

        self.ui.shotgun_button.clicked.connect(self.show_in_shotgun)
        self._processor.progress_changed.connect(self.ui.progress_bar.setValue)

        if edl_file_path:
            # Wait for the processor to be ready before doing anything
            self._processor.ready.connect(lambda: self._preselected_input(
                edl_file_path, sg_entity
            ))

        self._processor.start()

    # def _set_button_size(self, button):
    #     return lambda: self._set_button_size_B(button)

    # def _set_button_size_B(self, button):
    #     button.setFont(QtGui.QFont("SansSerif", 14))
    #     width = button.fontMetrics().boundingRect(button.text()).width() + 15
    #     button.setMaximumWidth(width)

    def _get_link_cb(self, entity_name, button):
        return lambda: self.link_button_clicked(entity_name, button)

    @QtCore.Slot(str, QtGui.QWidget)
    def link_button_clicked(self, entity_type, button):
        self._preload_entity_type = entity_type
        self.get_entities.emit(entity_type)

    def _preselected_input(self, edl_file_path, sg_entity):
        # Special mode for Premiere integration : load the given EDL
        # and select the given SG entity

        # There is not command line support yet for passing in a base layer
        # media file, so we set mov_file_path to None
        self.new_edl.emit(edl_file_path)
        if sg_entity:
            self._selected_sg_entity[_ENTITY_STEP] = sg_entity["type"]
            self.show_entities(sg_entity["type"])
            self._selected_sg_entity[_ENTITY_STEP] = sg_entity
            self.show_entity(sg_entity)
            self.goto_step(_CUT_STEP)

    @property
    def no_cut_for_entity(self):
        return self._processor.no_cut_for_entity

    @property
    def project_import(self):
        return self._processor.project_import

    @QtCore.Slot()
    def do_reset(self):
        """
        Reset callback, going back to the first page
        """
        # Omly ask confirmation if the cut was not yet imported
        if self._step != _LAST_STEP:
            msg_box = QtGui.QMessageBox(self)
            msg_box.setIcon(QtGui.QMessageBox.Warning)
            msg_box.setText("<big><b>Are you sure you want to Reset ?</b></big>")
            msg_box.setInformativeText("All Import Cut progress will be lost.")
            msg_box.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            msg_box.setDefaultButton(QtGui.QMessageBox.No)
            ret = msg_box.exec_()
        else:
            ret = QtGui.QMessageBox.Yes

        if ret == QtGui.QMessageBox.Yes:
            self._got_projects = False
            self.goto_step(_DROP_STEP)

    @QtCore.Slot()
    def reset(self):
        """
        Called when the first page is reached
        """
        self.set_ui_for_step(_DROP_STEP)

    @QtCore.Slot(int)
    def step_failed(self, which):
        """
        Called when a step failed, and going back to previous page
        should be allowed.
        """
        if which == _PROGRESS_STEP:
            self.ui.progress_screen_title_label.setText(
                "Import failed",
            )
            self.ui.back_button.show()

    @QtCore.Slot(int)
    def step_done(self, which):
        """
        Called when a step is done, and next page can be displayed
        """
        next_step = which + 1
        cur_step = self.ui.stackedWidget.currentIndex()
        if next_step < cur_step:
            return
        # Check if we can skip some intermediate screens
        if next_step == _PROJECT_STEP:
            # If we already have project from context, skip project chooser
            if self._ctx.project is not None:
                next_step = _ENTITY_STEP
            else:
                self.show_projects()
        if next_step == _ENTITY_STEP and self._entity_types_view.select_and_skip():
            # Skip single entity type screen, autoselecting the single entry
            next_step += 1
#        if next_step == _ENTITY_STEP and self._entities_view.select_and_skip():
#            next_step += 1
        if next_step == _ENTITY_STEP:
            self.get_entities.emit(self._preload_entity_type)
        self.goto_step(next_step)

    @QtCore.Slot()
    def process_edl_mov(self):
        """
        After EDL and optional MOV file paths have been set by process_drop
        The next button is activated and this code is run when Next is clicked.
        """
        # We're done with the drop step
        self.step_done(_DROP_STEP)

    @QtCore.Slot(list)
    def process_drop(self, paths):
        """
        Process a drop event, paths can either be
        local filesystem paths or SG urls
        """
        num_paths = len(paths)
        if num_paths > 2:
            QtGui.QMessageBox.warning(
                self,
                "Can't process drop",
                "Please drop maximum of two files at a time (EDL + MOV).",
            )
            return
        
        path = paths[0]
        _, ext = os.path.splitext(path)
        if ext.lower() == ".edl":
            # Reset things if an EDL was previously dropped
            self.ui.edl_added_icon.hide()
            self.ui.next_button.setEnabled(False)
            self.ui.file_added_label.setText("")
            self.new_edl.emit(path)
        elif ext.lower() in _VIDEO_EXTS:
            self.new_movie.emit(path)
        else:
            self._logger.error(
                "'%s' is not a supported file type. Supported types are .edl and movie types: %s." % (
                    os.path.basename(path),
                    str(_VIDEO_EXTS)
            ))
            return

        if num_paths == 2:
            path = paths[1]
            _, ext_2 = os.path.splitext(path)
            if ext_2.lower() == ext.lower():
                self._logger.error(
                    "An EDL file and a movie should be dropped, not two %s files." % (
                        # Strip leading ".", we can assume it is not empty, otherwise
                        # it would have been caught in 1st path handling
                        ext[1:],
                ))
                return
            elif ext_2.lower() == ".edl":
                # Reset things if an EDL was previously dropped
                self.ui.edl_added_icon.hide()
                self.ui.next_button.setEnabled(False)
                self.ui.file_added_label.setText("")
                self.new_edl.emit(path)
            elif ext_2.lower() in _VIDEO_EXTS:
                self.new_movie.emit(path)
            else:
                self._logger.error(
                    "'%s' is not a supported file type. Supported types are .edl and movie types: %s." % (
                        os.path.basename(path),
                        str(_VIDEO_EXTS)
                ))
                return

    @QtCore.Slot(str)
    def valid_edl(self, file_name):
        """
        Called when an EDL file has been validated and can be used

        :param file_name: Short EDL file name
        """
        self.ui.edl_added_icon.show()
        self.ui.file_added_label.setText(
            os.path.basename(file_name)
        )
        # Update a small information label in various screens we will later see
        import_message = "Importing %s" % file_name
        self.ui.importing_edl_label_2.setText(import_message)
        # Allow the user to go ahead without a movie
        self.ui.next_button.setEnabled(True)

    @QtCore.Slot(str)
    def valid_movie(self, file_name):
        """
        Called when a movie file has been validated and can be used

        :param file_name: Short movie file name
        """
        self.ui.mov_added_icon.show()
        self.ui.file_added_label.setText(
            os.path.basename(file_name)
        )

    @QtCore.Slot(int, str)
    def new_message(self, levelno, message):
        """
        Display a new message in the feedback widget
        """

        if levelno == logging.ERROR or levelno == logging.CRITICAL:
            self.ui.feedback_label.setProperty("level", "error")
            self.ui.progress_bar_label.setProperty("level", "error")
        else:
            self.ui.feedback_label.setProperty("level", "info")
            self.ui.progress_bar_label.setProperty("level", "info")

        self.style().unpolish(self.ui.feedback_label)
        self.style().polish(self.ui.feedback_label)
        self.style().unpolish(self.ui.progress_bar_label)
        self.style().polish(self.ui.progress_bar_label)
        self.ui.feedback_label.setText(message)
        self.ui.progress_bar_label.setText(message)

    @QtCore.Slot(str)
    def display_info_message(self, message):
        self.ui.feedback_label.setProperty("level", "info")
        self.style().unpolish(self.ui.feedback_label)
        self.style().polish(self.ui.feedback_label)
        self.ui.feedback_label.setText(message)

    @QtCore.Slot()
    def close_dialog(self):
        """
        Close this app
        """
        self.close()

    @property
    def hide_tk_title_bar(self):
        return False

    def is_busy(self):
        """
        Return True if the app is busy doing something,
        False if idle
        """
        return self._busy

    @QtCore.Slot()
    @QtCore.Slot(int)
    def set_busy(self, maximum=None):
        """
        Set the app as busy, disabling some widgets
        Display a progress bar if a maximum is given
        """
        self._busy = True
        # Prevent some buttons to be used
        self.ui.back_button.setEnabled(False)
        self.ui.reset_button.setEnabled(False)
        self.ui.email_button.setEnabled(False)
        self.ui.submit_button.setEnabled(False)
        self.ui.select_button.setEnabled(False)
        # Show the progress bar if a maximum was given
        if maximum:
            self.ui.progress_bar.setValue(0)
            self.ui.progress_bar.setMaximum(maximum)
            self.ui.progress_bar.show()

    @QtCore.Slot()
    def set_idle(self):
        """
        Set the app as idle, hide the progress bar if shown,
        enable back some widgets.
        """
        self._busy = False
        # Allow all buttons to be used
        self.ui.back_button.setEnabled(True)
        self.ui.reset_button.setEnabled(True)
        self.ui.email_button.setEnabled(True)
        self.ui.submit_button.setEnabled(True)
        self.ui.select_button.setEnabled(bool(self._selected_sg_entity[self._step]))
        self.ui.progress_bar.hide()

    def goto_step(self, which):
        """
        Go to a particular step
        """
        self.set_ui_for_step(which)
        self.ui.stackedWidget.goto_page(which)

    @QtCore.Slot()
    def previous_page(self):
        """
        Go back to previous page
        Skip intermediate screens if needed
        """
        current_page = self.ui.stackedWidget.currentIndex()
        previous_page = current_page - 1

        if previous_page == _CUT_STEP and self.no_cut_for_entity:
            # Skip cut selection screen
            previous_page = _ENTITY_STEP

        if previous_page == _ENTITY_STEP and self.project_import:
            # Skip project selection
            previous_page = _PROJECT_STEP

        if previous_page == _ENTITY_TYPE_STEP:
            previous_page = _PROJECT_STEP

        if previous_page == _ENTITY_STEP and self._entity_types_view.count() < 2:
            # If only one entity is available, no need to choose it
            previous_page = _PROJECT_STEP

        # todo: leaving this in here because it seems like we may want to
        # go back to this behavior.
        # if previous_page == _PROJECT_STEP:
        #     # Skip Project chooser page if we have a project from
        #     # current context
        #     if self._ctx.project:
        #         previous_page = _DROP_STEP

        if previous_page < 0:
            previous_page = _DROP_STEP

        if previous_page == _PROJECT_STEP:
            self.show_projects()

        self.ui.stackedWidget.goto_page(previous_page)

    def _change_entity_button(self, entity):
        entity_type = entity.get("type") or entity.get("mode_change")
        self._user_settings.store("preload_entity_type", entity_type)
        if entity_type == "Project":
            self.ui.create_entity_button.hide()
        elif entity_type:
            self.ui.create_entity_button.show()
            self.ui.create_entity_button.setText("New %s" % entity_type)
            self._selected_entity_tab = entity_type

    @QtCore.Slot(int)
    def set_ui_for_step(self, step):
        """
        Set the UI for the given step
        """
        self._step = step
        # 0 : drag and drop
        # 1 : project select
        # 2 : sequence select
        # 3 : cut select
        # 4 : cut summary
        # 5 : import completed
        if step == _DROP_STEP:
            # Clear various things when we hit the first screen
            # doing a reset
            self.ui.back_button.hide()
            self.ui.reset_button.hide()
            self._selected_sg_entity[_ENTITY_STEP] = None
            self.ui.edl_added_icon.hide()
            self.ui.mov_added_icon.hide()
            self.ui.file_added_label.setText("")
            self.ui.next_button.show()
            self.ui.next_button.setEnabled(False)
        else:
            # Allow reset and back from screens > 0
            self.ui.next_button.hide()
            self.ui.reset_button.show()
            self.ui.back_button.show()

        # if step == _ENTITY_TYPE_STEP:
        #     for i in range(2):
        #         btn = QtGui.QPushButton("test %s" % str(i))
        #         self.ui.entity_buttons_layout.addWidget(btn, i, 0)
                # btn.clicked.connect(self.buttonClicked)

        if step == _ENTITY_STEP:
            self.ui.create_entity_button.show()
        else:
            self.ui.create_entity_button.hide()

        if step < _PROJECT_STEP:
            self.ui.projects_search_line_edit.clear()
            self.clear_project_view()
            self._selected_sg_entity[_PROJECT_STEP] = None

        if step < _ENTITY_STEP:
            self.ui.sequences_search_line_edit.clear()
            self.clear_sequence_view()
            self._selected_sg_entity[_ENTITY_STEP] = None

        if step < _CUT_STEP:
            # todo: this line looks like a duplicate, cut?
            self._selected_sg_entity[_CUT_STEP] = None
            # Reset the cut view
            self.clear_cuts_view()
            self.ui.search_line_edit.clear()
            self._selected_sg_entity[_CUT_STEP] = None

        if step < _SUMMARY_STEP:
            # Reset the summary view
            self.clear_cut_summary_view()
            # Too early to submit anything
            self.ui.email_button.hide()
            self.ui.submit_button.hide()

        # We can select things on intermediate screens
        if step in [_PROJECT_STEP, _ENTITY_STEP, _CUT_STEP]:
            self.ui.select_button.show()
            # Only enable it if there is a selection for this step
            self.ui.select_button.setEnabled(bool(self._selected_sg_entity[step]))
        else:
            self.ui.select_button.hide()

        # Display info message in feedback line and other special things
        # based on the current step
        if step == _ENTITY_STEP:
            self.display_info_message(self._entity_types_view.info_message)
        elif step == _PROJECT_STEP:
            self.display_info_message(self._entity_types_view.info_message)
        elif step == _ENTITY_STEP:
            self.display_info_message(self._entities_view.info_message)
        elif step == _CUT_STEP:
            self.display_info_message(self._cuts_view.info_message)
        elif step == _SUMMARY_STEP:
            self.ui.email_button.show()
            self.ui.submit_button.show()
            self.display_info_message(self._cut_diffs_view.info_message)
            if self._processor.sg_cut:
                self.ui.cut_summary_title_label.setText(
                    "Comparing %s and <b>%s</b> for %s <b>%s</b>" % (
                        os.path.basename(self._processor.edl_file_path),
                        self._processor.sg_cut["code"],
                        self._processor.entity_type_name,
                        self._processor.entity_name,
                    )
                )
            else:
                self.ui.cut_summary_title_label.setText(
                    "Showing %s for %s <b>%s</b>" % (
                        os.path.basename(self._processor.edl_file_path),
                        self._processor.entity_type_name,
                        self._processor.entity_name,
                    )
                )
        elif step == _PROGRESS_STEP:
            self.ui.progress_screen_title_label.setText(
                "Importing %s..." % os.path.basename(self._processor.edl_file_path),
            )
            self.ui.email_button.hide()
            self.ui.submit_button.hide()
        elif step == _LAST_STEP:
            self.ui.edl_imported_label.setText(self._processor.sg_new_cut["code"])
            self.ui.back_button.hide()
            self.ui.email_button.hide()
            self.ui.submit_button.hide()
            # Clear info message
            self.display_info_message("")

    @QtCore.Slot(dict)
    def selection_changed(self, sg_entity):
        """
        Called when selection changes in intermediate screens
        :param sg_entity: The SG entity which was selected for the current step
        """
        # Keep track of what is selected in different views
        # so the select button at the bottom of the window can
        # trigger next step with current selection
        self._selected_sg_entity[self._step] = sg_entity
        self.ui.select_button.setEnabled(True)

    @QtCore.Slot()
    def select_button_callback(self):
        """
        Callback for the select button
        :raises: RuntimeError in cases of inconsistencies
        """
        if not self._selected_sg_entity[self._step]:
            raise RuntimeError("No selection for current step %d" % self._step)
        # if self._step == _ENTITY_STEP:
        #     self.show_entities(self._selected_sg_entity[self._step])
        elif self._step == _PROJECT_STEP:
            self._processor.set_project(self._selected_sg_entity[self._step])
            self._processor.half_reset.emit()
            self.show_entities(self._preload_entity_type)
            self.goto_step(_ENTITY_STEP)
        elif self._step == _ENTITY_STEP:
            self.show_entity(self._selected_sg_entity[self._step])
        elif self._step == _CUT_STEP:
            self.show_cut(self._selected_sg_entity[self._step])
        else:
            # Should never happen
            raise RuntimeError("Invalid step %d for selection callback" % self._step)

    @QtCore.Slot(str)
    def show_entities(self, sg_entity_type):
        """
        Called when cuts needs to be shown for a particular sequence
        """
        # Retrieve the nice name instead of CustomEntity04
        sg_entity_type_name = sgtk.util.get_entity_type_display_name(
            sgtk.platform.current_bundle().sgtk,
            sg_entity_type,
        )
        self._logger.info("Retrieving %s(s)" % sg_entity_type_name)
        self.ui.sequences_search_line_edit.setPlaceholderText("Search %s" % sg_entity_type_name)
        self.get_entities.emit(sg_entity_type)

    @QtCore.Slot(str)
    def show_projects(self):
        """
        Called when projects need to be shown
        """
        self._logger.info("Retrieving Project(s)")
        if not self._got_projects:
            self.get_projects.emit()
        self._got_projects = True

    @QtCore.Slot()
    def show_entity_types(self, sg_project):
        """
        Called when entities needs to be shown for a project

        :param sg_project: The Shotgun Project dict to check for entities with
        """
        self._processor.set_project(sg_project)
        self._processor.half_reset.emit()
        self.show_entities(self._preload_entity_type)
        self._logger.info("types!")
        # Here we don't need the worker to retrieve additional data from SG
        # so we don't emit any signal like in other show_xxxx slots and move
        # directly to the entity type screen
        self.goto_step(_ENTITY_STEP)

    @QtCore.Slot(dict)
    def show_entity(self, sg_entity):
        """
        Called when cuts needs to be shown for an entity
        """
        name = sg_entity.get("code",
                             sg_entity.get("name",
                                           sg_entity.get("title", "????")
                                           )
                             )
        type_name = sgtk.util.get_entity_type_display_name(
            sgtk.platform.current_bundle().sgtk,
            sg_entity["type"],
        )
        self._logger.info("Retrieving cuts for %s" % name)
        self.ui.selected_sequence_label.setText(
            "%s : <big><b>%s</big></b>" % (
                sg_entity["type"],
                name,
            )
        )
        self.show_cuts_for_sequence.emit(sg_entity)

    @QtCore.Slot(dict)
    def show_cut(self, sg_cut):
        """
        Called when cut changes needs to be shown for a particular sequence/cut
        :param sg_cut: A Cut dictionary as retrieved from Shotgun
        """
        self._logger.info("Retrieving cut information for %s" % sg_cut["code"])
        self.show_cut_diff.emit(sg_cut)

    @QtCore.Slot()
    def set_cut_summary_view_selectors(self):
        """
        Set labels on top views selectors in Cut summary view, from the current
        cut summary
        """
        summary = self._processor.summary
        self.ui.new_select_button.setText("New : %d" % summary.count_for_type(_DIFF_TYPES.NEW))
        self.ui.cut_change_select_button.setText(
            "Cut Changes : %d" % summary.count_for_type(_DIFF_TYPES.CUT_CHANGE))
        self.ui.omitted_select_button.setText(
            "Omitted : %d" % summary.count_for_type(_DIFF_TYPES.OMITTED))
        self.ui.reinstated_select_button.setText(
            "Reinstated : %d" % summary.count_for_type(_DIFF_TYPES.REINSTATED))
        self.ui.rescan_select_button.setText("Rescan Needed : %d" % summary.rescans_count)
        self.ui.total_button.setText("Total : %d" % len(summary))

    def clear_sequence_view(self):
        """
        Reset the page displaying available sequences
        """
        self._entities_view.clear()

    def clear_project_view(self):
        """
        Reset the page displaying available projects
        """
        self._projects_view.clear()

    def clear_cuts_view(self):
        """
        Reset the page displaying available cuts
        """
        self._cuts_view.clear()

    def clear_cut_summary_view(self):
        """
        Reset the cut summary view page
        """
        self._cut_diffs_view.clear()
        # Go back into "Show everything mode"
        wsize = self.ui.total_button.size()
        self.ui.total_button.setChecked(True)
        self.ui.total_button.resize(wsize.width(), 100)
        self.ui.only_vfx_check_box.setChecked(False)

    @QtCore.Slot()
    def import_cut(self):
        """
        Called when a the cut needs to be imported in Shotgun. Show a dialog where the
        user can review changes before importing the cut.
        """
        dialog = SubmitDialog(
            parent=self,
            title=self._processor.title,
            summary=self._processor.summary)
        dialog.submit.connect(self._processor.import_cut)
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()

    @QtCore.Slot()
    def show_settings_dialog(self):
        """
        Called when the settings dialog needs to be presented to the user. This can
        happen on almost every page of the animated stacked widget.
        """
        show_settings_dialog = SettingsDialog(parent=self)
        show_settings_dialog.show()
        show_settings_dialog.raise_()
        show_settings_dialog.activateWindow()

    def create_entity(self, entity_type, fields):
        """
        Creates an entity of the specified type and
        moves to the next screen with that entity selected.

        :param entity_type: String, the entity type to create.
        :param fields: Dict, fields to set on the new Entity, specified by
        the user in the create_entity dialog.
        """
        try:
            new_entity = self._sg.create(entity_type, fields)
            self.show_cuts_for_sequence.emit(new_entity)
        except Exception, e:
            msg_box = QtGui.QMessageBox(
                parent=self,
                icon=QtGui.QMessageBox.Critical
            )
            msg_box.setIconPixmap(QtGui.QPixmap(":/tk_multi_importcut/error_64px.png"))
            msg_box.setText("The following error was reported:")
            msg_box.setInformativeText(
                "It's possible you do not have permission to create new %ss. Please select another \
%s or ask your Shotgun Admin to adjust your permissions in Shotgun." % (
                    entity_type,
                    entity_type
                )
            )
            msg_box.setDetailedText("%s" % e)
            msg_box.setStandardButtons(QtGui.QMessageBox.Ok)
            msg_box.show()
            msg_box.raise_()
            msg_box.activateWindow()

    @QtCore.Slot()
    def create_entity_dialog(self):
        """
        Called on the Select [Entity] page, the user is presented with a dialog
        where s/he can choose to create a new Entity of the selected type.
        """
        show_create_entity_dialog = CreateEntityDialog(
            self._selected_entity_tab,
            self._processor.sg_project,
            parent=self
        )
        show_create_entity_dialog.create_entity.connect(self.create_entity)
        show_create_entity_dialog.show()
        show_create_entity_dialog.raise_()
        show_create_entity_dialog.activateWindow()

    @QtCore.Slot()
    def email_cut_changes(self):
        """
        Called when the user click on the "Email Summary" button. Forge a mailto:
        url and open it up.
        """
        if not self._processor.sg_entity:
            self._logger.warning("No selected sequence ...")
            return
        links = ["%s/detail/%s/%s" % (
            self._app.shotgun.base_url,
            self._processor.sg_entity["type"],
            self._processor.sg_entity["id"],
        )]
        subject, body = self._processor.summary.get_report(self._processor.title, links)
        mail_url = QtCore.QUrl("mailto:?subject=%s&body=%s" % (subject, body))
        self._logger.debug("Opening up %s" % mail_url)
        QtGui.QDesktopServices.openUrl(mail_url)

    @QtCore.Slot()
    def show_in_shotgun(self):
        sg_url = QtCore.QUrl(self._processor.sg_new_cut_url)
        QtGui.QDesktopServices.openUrl(sg_url)
        self.close()

    @QtCore.Slot(str, list)
    def display_exception(self, msg, exec_info):
        """
        Display a popup window with the error message
        and the exec_info in the "details"
        """
        msg_box = QtGui.QMessageBox(
            parent=self,
            icon=QtGui.QMessageBox.Critical
            )
        msg_box.setText("The following error was reported :")
        msg_box.setInformativeText(msg)
        msg_box.setDetailedText("\n".join(exec_info))
        msg_box.setStandardButtons(QtGui.QMessageBox.Ok)
        msg_box.show()
        msg_box.raise_()
        msg_box.activateWindow()

    def closeEvent(self, evt):
        """
        closeEvent handler

        Warn the user if it's not safe to quit,
        and leave the decision to him
        """
        if self.is_busy():
            answer = QtGui.QMessageBox.warning(
                self,
                "Quit anyway ?",
                "Busy, quit anyway ?",
                QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok)
            if answer != QtGui.QMessageBox.Ok:
                evt.ignore()  # For close event, ignore stop them to be processed
                return
        self._processor.quit()
        self._processor.wait()
        # Wait for the global ThreadPool to be done with all downloads
        # problem is we don't have a way to tell the ThreadPool to stop
        # processing queued request, so it takes a while to get all threads
        # done. We need a way to abort all queued downloaded, through their
        # abort slot
        QtCore.QThreadPool.globalInstance().waitForDone()
        # Let the close happen
        evt.accept()

    def set_logger(self, level=logging.INFO):
        """
        Retrieve a logger
        """
        self._logger = get_logger()
        handler = BundleLogHandler(self._app)
        handler.new_message.connect(self.new_message)
        handler.new_error_with_exc_info.connect(self.display_exception)
        self._logger.addHandler(handler)

        # Copied over from tk-desktop and tk-multi-ingestdelivery
        if sys.platform == "darwin":
            fname = os.path.join(
                os.path.expanduser("~"), "Library", "Logs", "Shotgun", "%s.log" % self._app.name)
        elif sys.platform == "win32":
            fname = os.path.join(
                os.environ.get("APPDATA", "APPDATA_NOT_SET"), "Shotgun", "%s.log" % self._app.name)
        elif sys.platform.startswith("linux"):
            fname = os.path.join(
                os.path.expanduser("~"), ".shotgun", "logs", "%s.log" % self._app.name)
        else:
            raise NotImplementedError("Unknown platform: %s" % sys.platform)

        handler = logging.handlers.RotatingFileHandler(fname, maxBytes=1024*1024, backupCount=5)
        handler.addFilter(ShortNameFilter())
        handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s %(short_name)s %(message)s"
        ))
        self._logger.addHandler(handler)

        self._logger.setLevel(level)

    def set_custom_style(self):
        """
        Append our custom style to the inherited style sheet
        """
        self._css_watcher = None
        this_folder = self._app.disk_location  # os.path.abspath(os.path.dirname(__file__))
        css_file = os.path.join(this_folder, "style.qss")
        if os.path.exists(css_file):
            self._load_css(css_file)
            # Add a watcher to pickup changes only if the app was started from tk-shell
            # usually clients use tk-desktop or tk-shotgun, so it should be safe to
            # assume that this will cause any harm in production
            if self._app.get_setting("css_watcher"):
                self._css_watcher = QtCore.QFileSystemWatcher([css_file], self)
                self._css_watcher.fileChanged.connect(self.reload_css)

    def _load_css(self, css_file):
        self.setStyleSheet("")
        if os.path.exists(css_file):
            try:
                # todo: changing the default font to OpenSans should really
                # happen in Toolkit, so app Studio apps inherit the font, instead
                # of having to manually change it like this for each app
                # getting the path to fonts relative to this file
                font_path = self._app.disk_location
                font_path = os.path.join(font_path, "resources", "fonts")
                # load custom font
                QtGui.QFontDatabase.addApplicationFont(
                    os.path.join(font_path, "OpenSans-Bold.ttf"))
                QtGui.QFontDatabase.addApplicationFont(
                    os.path.join(font_path, "OpenSans-Regular.ttf"))
                QtGui.QFontDatabase.addApplicationFont(
                    os.path.join(font_path, "OpenSans-CondLight.ttf"))
                QtGui.QFontDatabase.addApplicationFont(
                    os.path.join(font_path, "OpenSans-Light.ttf"))
                # Read css file
                f = open(css_file)
                css_data = f.read()
                f.close()
                # Append our add ons to current sytle sheet at the top widget
                # level, children will inherit from it, without us affecting
                # other apps for this engine
                self.setStyleSheet(css_data)
            except Exception, e:
                self._app.log_warning("Unable to read style sheet %s" % css_file)

    @QtCore.Slot(str)
    def reload_css(self, path):
        self._logger.info("Reloading %s" % path)
        self._load_css(path)
        # Some code editors rename files on save, so the watcher will
        # stop watching it. Check if the file watched, re-attach it if not
        if self._css_watcher and path not in self._css_watcher.files():
            self._css_watcher.addPath(path)
        self._logger.info("%s loaded" % path)
        self.update()
