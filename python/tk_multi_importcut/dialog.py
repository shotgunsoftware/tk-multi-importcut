# Copyright (c) 2021 Autodesk, Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the ShotGrid Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the ShotGrid Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk, Inc.

import os
import sys
import sgtk
import logging
import logging.handlers
import ast
from operator import itemgetter

elided_label = sgtk.platform.import_framework("tk-framework-qtwidgets", "elided_label")
ElidedLabel = elided_label.ElidedLabel
# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
from sgtk.platform.qt import QtCore, QtGui

from .user_settings import UserSettings
from .widgets import DropAreaFrame, AnimatedStackedWidget
from .search_widget import SearchWidget
from .entity_line_widget import EntityLineWidget
from .extended_thumbnail import ExtendedThumbnail

try:
    from tank_vendor import sgutils
except ImportError:
    from tank_vendor import six as sgutils


class SelectorButton(QtGui.QPushButton):
    """
    Thin wrapping class for our selector buttons so styling can be done in the
    style sheet for all of them, using the class name
    """

    pass


# Custom widgets must be imported or defined before importing the UI
from .ui.dialog import Ui_Dialog

from .processor import Processor
from .logger import BundleLogHandler, get_logger, ShortNameFilter
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
from .constants import _VIDEO_EXTS, _EDL_EXT

# Documentation url
from .constants import _DOCUMENTATION_URL

settings = sgtk.platform.import_framework("tk-framework-shotgunutils", "settings")

_BAD_PERMISSIONS_MSG = "The following error was reported:\n\nIt's possible you \
do not have permission to create new %ss. Please select another %s or ask your \
Flow Production Tracking Admin to adjust your permissions in Flow Production Tracking."

_TRANSITIONS_PRESENT_MSG = (
    "This EDL contains a transition.\n\nFlow Production Tracking "
    "does not support transitions when viewing the Cut, but the EDL can still be \
imported. The transition frames will be included in the Cut Duration for the \
Shots, and frame handles will be calculated outside of the transition."
)


def show_dialog(app_instance):
    """
    Shows the main dialog window.

    :param app_instance: An Import Cut TK app instance
    """
    # In order to handle UIs seamlessly, each Toolkit engine has methods for launching
    # different types of windows. By using these methods, your windows will be correctly
    # decorated and handled in a consistent fashion by the system.

    # Create a settings manager where we can pull and push prefs later
    app_instance.user_settings = settings.UserSettings(sgtk.platform.current_bundle())

    # We pass the dialog class to this method and leave the actual construction
    # to be carried out by toolkit.
    app_instance.engine.show_dialog("Import Cut", app_instance, AppDialog)


def load_edl_for_entity(app_instance, edl_file_path, sg_entity, frame_rate):
    """
    Run the app with a pre-selected edl file and PTR entity, typically from
    command line arguments.

    :param app_instance: An Import Cut TK app instance
    :param edl_file_path: Full path to an EDL file
    :param sg_entity: A PTR Entity dictionary as a string, e.g.
                      '{"code" : "001", "id" : 19, "type" : "Sequence"}'
    :param frame_rate: The frame rate for the EDL file, as a float.
                       For example 24.0, 29.997 or 60.0
    """
    sg_entity_dict = None
    # Convert the string representation to a regular dict
    if sg_entity:
        sg_entity_dict = ast.literal_eval(sg_entity)
        if not isinstance(sg_entity_dict, dict):
            raise ValueError("Invalid PTR Entity %s" % sg_entity)

    app_instance.engine.show_dialog(
        "Import Cut",
        app_instance,
        AppDialog,
        edl_file_path=edl_file_path,
        sg_entity=sg_entity_dict,
        frame_rate=frame_rate,
    )


class AppDialog(QtGui.QWidget):
    """
    Main application dialog window

    All data is handled on a dedicated thread started with a Processor instance.
    Data is allocated in the dedicated Processor running thread, so slots are
    honored in this thread. Pass through signals are used to communicate between
    this thread, the Processor and the EdlCut data which is not available when the
    app is started, but only after the Processor was started.

    This app follows a wizard style approach: some steps are defined, signals are
    emitted to ask the data manager to retrieve data needed for the next step. The
    data manager validates that the current step is done, so the UI can move to the
    next one.

    Each step has a dedicated screen, except for the Entity Type / Entity steps
    which are combined in a single screen. Therefore, the Entity Type step is a
    'virtual' step which, when done, does not move the UI to the next screen.

    Intermediate screens are views displaying cards for various PTR Entities. The
    user selects one of them, we ask the data manager to retrieve data linked to
    this Entity, and move forward to next step when the data is retrieved.
    """

    # Emitted when a new EDL file should be loaded
    new_edl = QtCore.Signal(str)
    # Emitted when a new movie file should be considered
    new_movie = QtCore.Signal(str)
    # Emitted to ask the data manager to retrieve PTR projects
    get_projects = QtCore.Signal()
    # Emitted to ask the data manager to retrieve PTR entities
    get_entities = QtCore.Signal(str)
    # Emitted when the current PTR Project should be set
    set_active_project = QtCore.Signal(dict)
    # Emitted to ask the data manager to retrieve PTR Cuts for a given PTR Entity
    get_cuts_for_entity = QtCore.Signal(dict)
    # Emitted to ask the data manager to retrieve PTR CutItems for a given PTR Cut
    # and CutDiffs with edit entries / Cut items
    get_cut_diff = QtCore.Signal(dict)
    # Emitted when data for a particular step should be reloaded/rebuilt by the
    # data manager
    reload_step = QtCore.Signal(int)

    def __init__(self, edl_file_path=None, sg_entity=None, frame_rate=None):
        """
        Create a new app instance. Optional parameters can be given to skip
        the first screens.

        :param edl_file_path: Full path to an EDL file
        :param sg_entity: An PTR Entity dictionary
        :param frame_rate: Optional float, use a specific frame rate for the import,
                           e.g. 24.0, 29.997 or 60.0, potentially different from
                           the frame rate stored in user settings
        """
        # first, call the base class and let it do its thing.
        QtGui.QWidget.__init__(self)

        # now load in the UI that was created in the UI designer
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # most of the useful accessors are available through the Application class instance
        # it is often handy to keep a reference to this. You can get it via the following method:
        self._app = sgtk.platform.current_bundle()
        self._ctx = self._app.context

        # Grab user settings class and check for updates.
        self._user_settings = UserSettings()
        self._user_settings.update()

        self.checked_entity_button = None

        self._busy = False
        # Current import step being displayed
        self._step = 0

        # PTR Entity that is selected at each step. Selection only happen in the first steps
        # but we create entries for all the steps which allows us to index the list
        # with the current step and blindly disable the select button on the
        # value for each step
        self._selected_sg_entity = [None] * (_LAST_STEP + 1)

        # Load styling and build our main logger
        self.set_custom_style()
        self.set_logger(logging.INFO)

        # Load the Entity type we should show in Entities screen from user
        # preferences
        self._preload_entity_type = self._user_settings.get("preload_entity_type")
        self._logger.debug("Preferred Entity type %s" % self._preload_entity_type)

        # Keep this thread for UI stuff
        # Handle data and processing in a separate thread
        self._processor = Processor(frame_rate)

        # Connect signal which will allow us to communicate with the data
        # manager
        # Let the data manager know that we have a new EDL or new movie
        self.new_edl.connect(self._processor.new_edl)
        self.new_movie.connect(self._processor.new_movie)
        self.reload_step.connect(self._processor.reload_step)
        # Validating the EDL / movie is left to the data manager so we need to
        # know if it considered them valid
        self._processor.valid_edl.connect(self.set_edl_validity)
        self._processor.has_transitions.connect(self.has_transitions)
        self._processor.valid_movie.connect(self.valid_movie)

        # Let the data manager know that we need it to retrieve data from PTR
        self.get_projects.connect(self._processor.retrieve_projects)
        self.set_active_project.connect(self._processor.set_sg_project)
        self.get_entities.connect(self._processor.retrieve_entities)
        self.get_cuts_for_entity.connect(self._processor.retrieve_cuts)
        self.get_cut_diff.connect(self._processor.show_cut_diff)

        # The data manager will let us know if we can move the UI to the next step
        # or if the current step failed
        self._processor.step_done.connect(self.step_done)
        self._processor.step_failed.connect(self.step_failed)

        # When the data manager is busy, we want to highlight it in the UI,
        # preventing user interactions
        self._processor.got_busy.connect(self.set_busy)
        self._processor.got_idle.connect(self.set_idle)

        # Ensure all data is cleared when we reach back the first screen
        self.ui.stackedWidget.first_page_reached.connect(self._processor.reset)

        # Let's do something when something is dropped
        self.ui.drop_area_frame.something_dropped.connect(self.process_drop)
        self.ui.drop_area_frame.set_restrict_to_ext(_VIDEO_EXTS + [_EDL_EXT])

        # Build views and connect them to the data manager

        # Instantiate a Projects view handler
        self._projects_view = ProjectsView(self.ui.project_grid)
        # The view will let us know when a Project was picked up
        self._projects_view.project_chosen.connect(self.project_chosen)
        # We need to know the current selection for the "Select" button
        self._projects_view.selection_changed.connect(self.selection_changed)
        # Display messages from the view
        self._projects_view.new_info_message.connect(self.display_info_message)
        # When PTR Projects are retrieved by the data manager, let the view know
        # that new cards should be build for them
        self._processor.new_sg_project.connect(self._projects_view.new_sg_project)
        self.ui.projects_search_line_edit.search_edited.connect(
            self._projects_view.search
        )
        self.ui.projects_search_line_edit.search_changed.connect(
            self._projects_view.search
        )

        # Instantiate an empty entities views handler. This will be populated later
        # and we will have one view per Entity type
        self._entities_views = []

        # Instantiate a Cuts view handler
        self._cuts_view = CutsView(self.ui.cuts_grid, self.ui.cuts_sort_button)
        # Show Cut differences when a PTR Cut is picked up
        self._cuts_view.cut_chosen.connect(self.show_cut_diff)
        # We need to know the current selection for the "Select" button
        self._cuts_view.selection_changed.connect(self.selection_changed)
        # Display messages from the view
        self._cuts_view.new_info_message.connect(self.display_info_message)
        # When PTR Cuts are retrieved by the data manager, let the view know
        # that new cards should be build for them
        self._processor.new_sg_cut.connect(self._cuts_view.new_sg_cut)
        self.ui.search_line_edit.search_edited.connect(self._cuts_view.search)
        self.ui.search_line_edit.search_changed.connect(self._cuts_view.search)

        # Instantiate a Cut differences view handler
        self._cut_diffs_view = CutDiffsView(self.ui.cutsummary_list)
        # We display some totals per Cut Diff type above the CutDiffsView, we need
        # to know when we should update them
        self._cut_diffs_view.totals_changed.connect(self.set_cut_summary_view_selectors)
        self._processor.totals_changed.connect(self.set_cut_summary_view_selectors)
        # Display messages from the view
        self._cut_diffs_view.new_info_message.connect(self.display_info_message)
        # When CutDiffs are retrieved by the data manager, let the view know
        # that new cards should be build for them
        self._processor.new_cut_diff.connect(self._cut_diffs_view.new_cut_diff)
        # and when some should be discarded
        self._processor.delete_cut_diff.connect(self._cut_diffs_view.delete_cut_diff)

        # Cut summary view selectors, displaying totals per type and allowing to
        # show only a particular type of Cut differences
        self.ui.new_select_button.toggled.connect(
            lambda x: self._cut_diffs_view.set_display_summary_mode(x, _DIFF_TYPES.NEW)
        )
        self.ui.cut_change_select_button.toggled.connect(
            lambda x: self._cut_diffs_view.set_display_summary_mode(
                x, _DIFF_TYPES.CUT_CHANGE
            )
        )
        self.ui.omitted_select_button.toggled.connect(
            lambda x: self._cut_diffs_view.set_display_summary_mode(
                x, _DIFF_TYPES.OMITTED
            )
        )
        self.ui.reinstated_select_button.toggled.connect(
            lambda x: self._cut_diffs_view.set_display_summary_mode(
                x, _DIFF_TYPES.REINSTATED
            )
        )
        self.ui.rescan_select_button.toggled.connect(
            lambda x: self._cut_diffs_view.set_display_summary_mode(x, 100)
        )
        self.ui.total_button.toggled.connect(
            lambda x: self._cut_diffs_view.set_display_summary_mode(x, -1)
        )
        self.ui.only_vfx_check_box.toggled.connect(
            self._cut_diffs_view.display_vfx_cuts
        )

        # Ensure we land on the startup screen
        self.ui.stackedWidget.set_current_index(_DROP_STEP)
        self.set_ui_for_step(_DROP_STEP)

        # Callbacks for buttons at the bottom of the app UI
        self.ui.back_button.clicked.connect(self.previous_page)
        self.ui.next_button.clicked.connect(self.process_edl_mov)
        self.ui.create_entity_button.clicked.connect(self.create_entity_dialog)
        self.ui.stackedWidget.first_page_reached.connect(self.reset)
        self.ui.stackedWidget.currentChanged.connect(self.set_ui_for_step)
        self.ui.cancel_button.clicked.connect(self.close_dialog)
        self.ui.select_button.clicked.connect(self.select_button_callback)
        self.ui.skip_button.clicked.connect(self.skip_button_callback)
        self.ui.reset_button.clicked.connect(self.do_reset)
        self.ui.email_button.clicked.connect(self.email_cut_changes)
        self.ui.submit_button.clicked.connect(self.import_cut)

        # We have a different settings button on different pages of the stacked widget
        # Connect them, making the settings dialog aware of the step it was started
        # from, so later we will be able to check if the settings changes neeed a
        # a restart or not, based on the step they were changed at
        for step, button in {
            _DROP_STEP: self.ui.drop_page_settings_button,
            _PROJECT_STEP: self.ui.project_page_settings_button,
            _ENTITY_STEP: self.ui.entities_page_settings_button,
            _CUT_STEP: self.ui.cut_list_page_settings_button,
            _SUMMARY_STEP: self.ui.cut_summary_page_settings_button,
        }.items():
            button.clicked.connect(lambda x=step: self.show_settings_dialog(x))

        # The Entities page allows selecting different Entity types, dynamically
        # create these buttons. A Project button is always added
        self._create_entity_type_buttons()

        # A button to see the import result in Flow Production Tracking
        self.ui.shotgun_button.clicked.connect(self.show_in_shotgun)
        # A button that opens user-facing documentation in a browser.
        self.ui.help_button.clicked.connect(self.show_help)
        # Report import progress
        self._processor.progress_changed.connect(self.ui.progress_bar.setValue)

        # If we had some preselected input, wait for the processor to be ready
        # before doing anything
        if edl_file_path:
            self._processor.ready.connect(
                lambda: self._preselected_input(edl_file_path, sg_entity)
            )
        # Start the data manager thread
        self._processor.start()

    def _create_entity_type_buttons(self):
        """
        Create buttons allowing to choose which Entity type the Cut
        will be imported against.

        The list of valid Entity types that Cuts can be linked to is derived
        from the Flow Production Tracking schema field setting for Cut.entity.

        The current UI can only handle displaying a limited number of entity
        types correctly. Any more than that and they would not be displayed
        correctly.
        """
        # Retrieve the stack widget used to display the lists of entities
        entity_type_stacked_widget = self.ui.entities_type_stacked_widget
        # Retrieve the maximum number of Entity types we can handle
        max_count = entity_type_stacked_widget.count()

        schema = self._app.shotgun.schema_field_read("Cut", "entity")
        schema_entity_types = schema["entity"]["properties"]["valid_types"]["value"]

        # Validate and potentially reset current value retrieved from user
        # preferences.
        # Project is systematically added so is always valid
        if (
            self._preload_entity_type is not None
            and self._preload_entity_type != "Project"
            and self._preload_entity_type not in schema_entity_types
        ):
            self._logger.warning(
                "Resetting invalid Entity type preference %s"
                % self._preload_entity_type
            )
            self._preload_entity_type = None

        # Build a list of Entity type / Entity type name tuple
        entity_types = []
        for entity_type in schema_entity_types:
            entity_types.append(
                (
                    entity_type,
                    self._app.shotgun.schema_entity_read(entity_type)[entity_type][
                        "name"
                    ]["value"],
                )
            )
        # Sort by the display name
        entity_types.sort(key=itemgetter(1))
        count = len(entity_types)
        # This is a bit arbitrary, since it only messes up the gui, but it's probably
        # possible to display more like eight types, depending on the char length of each type.
        # We always add Project to the list of Entity types, so we reserve one slot
        # for it
        if count > max_count - 1:
            self._logger.warning(
                "Sorry, we can only display %d link Entity Types at a time." % max_count
            )
            entity_types = entity_types[: max_count - 1]
        # We always want to be able to import against the Project. We want Project
        # to always be the last button, so we append it after sorting is done, and
        # after trimming is done.
        entity_types.append(
            (
                "Project",
                "Project",
            )
        )
        # Preselect 1st entry, we will always have at the very least one Project entry
        if self._preload_entity_type is None:
            self._preload_entity_type = entity_types[0][0]
            self._logger.debug(
                "Preselecting %s Entity type" % self._preload_entity_type
            )

        for entity_type in entity_types:
            button = self._create_entity_type_button(entity_type[0], entity_type[1])
            self.ui.entity_buttons_layout.addWidget(button)
            if entity_type[0] == self._preload_entity_type:
                button.setChecked(True)

    def _create_entity_type_view(self, sg_entity_type, grid_layout):
        """
        Create a view for the given PTR Entity type

        :param sg_entity_type: A PTR Entity type as a string, e.g. 'Shot'
        :param grid_layout: A QGridLayout used to layout Entity Cards
        """
        self._entities_views.append(EntitiesView(sg_entity_type, grid_layout))
        # Show Cuts for the chosen Entity once it is picked up
        self._entities_views[-1].entity_chosen.connect(self.show_cuts)
        # We need to know the current selection for the "Select" button
        self._entities_views[-1].selection_changed.connect(self.selection_changed)
        # Display messages from the view
        self._entities_views[-1].new_info_message.connect(self.display_info_message)
        # When PTR Entities are retrieved by the data manager, let the view know
        # that new cards should be build for them
        self._processor.new_sg_entity.connect(self._entities_views[-1].new_sg_entity)
        self.ui.entities_search_line_edit.search_edited.connect(
            self._entities_views[-1].search
        )
        self.ui.entities_search_line_edit.search_changed.connect(
            self._entities_views[-1].search
        )

    def _create_entity_type_button(self, entity_type, entity_type_name):
        """
        Create a button allowing to select an Entity Type

        :param entity_type: A PTR Entity type
        :param entity_type_name: A nice name for this Entity type
        :returns: A QPushButton
        """
        entity_link_button = SelectorButton(entity_type_name)
        entity_link_button.setObjectName("dynamic_button_%s" % entity_type_name)
        entity_link_button.setFlat(True)
        entity_link_button.setAutoExclusive(True)
        entity_link_button.setCheckable(True)
        entity_link_button.setFont(QtGui.QFont("SansSerif", 20))
        width = (
            entity_link_button.fontMetrics().boundingRect(entity_type_name).width() + 7
        )
        entity_link_button.setMaximumWidth(width)
        entity_link_button.clicked.connect(
            lambda: self.activate_entity_type_view(entity_type)
        )
        return entity_link_button

    @QtCore.Slot(str)
    def activate_entity_type_view(self, u_entity_type):
        """
        Called when an Entity Type button is clicked, activate the Entity type
        in the Entities view

        :param u_entity_type: A PTR Entity type, as a unicode string
        """
        entity_type = sgutils.ensure_str(u_entity_type)
        # Show the view for the Entity type
        self.show_entities(entity_type)
        # The UI can change based on the entity_type, so call a refresh.
        # In some cases, this is not actually needed (for example when
        # the Entity type view is created). So we might refresh the UI twice
        # instead of only once, but this is not a huge deal as it is not heavy.
        self.set_ui_for_step(self._step)

    def _preselected_input(self, edl_file_path, sg_entity):
        """
        Special mode when the app is launched with command line parameters,
        e.g. for Premiere integration: load the given EDL and select the given
        PTR Entity

        :param edl_file_path: Full path to EDL file
        :param sg_entity: A PTR Entity dictionary
        """

        # There is no command line support yet for passing in a base layer
        # media file, so we set mov_file_path to None
        self.new_edl.emit(edl_file_path)
        if sg_entity:
            self._selected_sg_entity[_PROJECT_STEP] = self._ctx.project
            self._selected_sg_entity[_ENTITY_TYPE_STEP] = sg_entity["type"]
            self.show_entities(sg_entity["type"])
            self._selected_sg_entity[_ENTITY_STEP] = sg_entity
            self.show_cuts(sg_entity)
            self.goto_step(_CUT_STEP)

    @property
    def no_cut_for_entity(self):
        """
        Returns True if there is no Cut associated with the current PTR Entity

        :returns: False if there is a least one Cut available, True otherwise
        """
        return self._processor.no_cut_for_entity

    @QtCore.Slot()
    def do_reset(self):
        """
        Reset callback, going back to the first page
        """
        # Only ask confirmation if the Cut was not yet imported
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

        :param which: One of our wizard style steps
        """
        if which == _PROGRESS_STEP:
            self.ui.progress_screen_title_label.setText(
                "Import failed",
            )
            self.ui.back_button.show()

    @QtCore.Slot(int)
    def step_done(self, which):
        """
        Called when a step is done, and next page can be displayed. This is
        typically triggered by the data manager emitting a step_done signal.

        We determine what the next step is, ask the data manager to retrieve
        the data we need, and show the screen associated with the next step

        :param which: One of our wizard style steps
        """
        next_step = which + 1
        cur_step = self.ui.stackedWidget.currentIndex()
        if next_step < cur_step:
            return
        # Check if we can skip some intermediate screens
        if next_step == _PROJECT_STEP:
            # If we already have Project from context, skip Project chooser
            if self._ctx.project is not None:
                next_step = _ENTITY_TYPE_STEP
                # We don't show the Project screen when moving forward, but
                # do show it when moving backward, so we skip the step but ask
                # the data manager to retrieve projects
                self.show_projects()
                self.project_chosen(self._ctx.project)
            else:
                self.show_projects()
        if next_step == _ENTITY_TYPE_STEP:
            self._logger.debug(
                "Activating Entity type step for %s" % self._preload_entity_type
            )
            self.show_entities(self._preload_entity_type)
            # This is a "virtual" step, no UI is shown for it, so we skip it
            next_step = _ENTITY_STEP
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
        Process a drop event

        :param paths: A list of local paths on the file system, as unicode strings
        """
        num_paths = len(paths)
        if num_paths > 2:
            QtGui.QMessageBox.warning(
                self,
                "Can't process drop",
                "Please drop maximum of two files at a time (EDL + MOV).",
            )
            return

        path = sgutils.ensure_str(paths[0])
        _, ext = os.path.splitext(path)
        if not self._process_dropped_file(path, ext):
            return

        if num_paths == 2:
            path = sgutils.ensure_str(paths[1])
            _, ext_2 = os.path.splitext(path)
            if ext_2.lower() == ext.lower():
                self._logger.error(
                    "An EDL file and a movie should be dropped, not two %s files."
                    % (
                        # Strip leading ".", we can assume it is not empty, otherwise
                        # it would have been caught in 1st path handling
                        ext[1:],
                    )
                )
                return
            self._process_dropped_file(path, ext_2)

    def _process_dropped_file(self, path, ext):
        """
        Process the given dropped file

        :param path: Full file path
        :param ext: The file extension, as extracted with splitext, e.g. '.edl'
        :returns: True if the file is valid, False otherwise
        """
        if ext.lower() == _EDL_EXT:
            # Reset things if an EDL was previously dropped
            self.ui.edl_added_icon.hide()
            self.ui.next_button.setEnabled(False)
            self.ui.file_added_label.setText("")
            self.new_edl.emit(path)
        elif ext.lower() in _VIDEO_EXTS:
            self.new_movie.emit(path)
        else:
            self._logger.error(
                "'%s' is not a supported file type. Supported types are %s and movie types: %s."
                % (os.path.basename(path), _EDL_EXT, str(_VIDEO_EXTS))
            )
            return False
        return True

    @QtCore.Slot()
    def has_transitions(self):
        """
        Called when an EDL is dropped and contains transitions. Pop up message
        informing the user of current Cuts feature compatibility with Flow Production Tracking.
        """
        msg_box = QtGui.QMessageBox(parent=self, icon=QtGui.QMessageBox.Critical)
        msg_box.setIconPixmap(QtGui.QPixmap(":/tk_multi_importcut/clapboard.png"))
        msg_box.setText(_TRANSITIONS_PRESENT_MSG)
        msg_box.setStandardButtons(QtGui.QMessageBox.Ok)
        msg_box.show()
        msg_box.raise_()
        msg_box.activateWindow()

    @QtCore.Slot(str, bool)
    def set_edl_validity(self, u_file_name, is_valid):
        """
        Called when an EDL file has been validated or invalidated by the data
        manager.

        Set the UI to reflect the fact that we now have, or don't have anymore a
        valid EDL.

        :param u_file_name: Unicode short EDL file name
        :param is_valid: A boolean, True if the EDL file can be used
        """
        file_name = sgutils.ensure_str(u_file_name)
        if is_valid:
            self.ui.edl_added_icon.show()
            self.ui.file_added_label.setText(file_name)
            # Update a small information label in various screens we will later see
            import_message = "Importing %s" % file_name
            self.ui.importing_edl_label_2.setText(import_message)
            # Allow the user to go ahead without a movie
            self.ui.next_button.setEnabled(True)
        else:
            self.ui.edl_added_icon.hide()
            self.ui.file_added_label.setText("")
            self.ui.importing_edl_label_2.setText("")
            self.ui.next_button.setEnabled(False)
            self.goto_step(_DROP_STEP)

        self._logger.debug(
            "%s EDL is now %s" % (file_name, ["invalid", "valid"][is_valid])
        )

    @QtCore.Slot(str)
    def valid_movie(self, u_file_name):
        """
        Called when a movie file has been validated and can be used

        :param u_file_name: Unicode short movie file name
        """
        file_name = sgutils.ensure_str(u_file_name)
        self.ui.mov_added_icon.show()
        self.ui.file_added_label.setText(file_name)

    @QtCore.Slot(int, str)
    def new_message(self, levelno, u_message):
        """
        Display a message in the feedback widget

        :param levelno: A standard logging level
        :param u_message: A unicode string
        """
        message = sgutils.ensure_str(u_message)
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
    def display_info_message(self, u_message):
        """
        Display an information message in the feedback widget

        :param u_message: A unicode string
        """
        message = sgutils.ensure_str(u_message)
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

    def is_busy(self):
        """
        Return True if the app is busy doing something, False if idle

        :returns: A boolean
        """
        return self._busy

    @QtCore.Slot()
    @QtCore.Slot(int)
    def set_busy(self, maximum=None):
        """
        Set the app as busy, disabling some widgets
        Display a progress bar if a maximum is given

        :param maximum: An integer or None
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
        self.ui.select_button.setEnabled(self.has_valid_selection_for_step(self._step))
        self.ui.progress_bar.hide()

    def goto_step(self, which):
        """
        Move the UI to a particular step

        :param which: One of our wizard style steps
        """
        self.set_ui_for_step(which)
        self.ui.stackedWidget.goto_page(which)

    @QtCore.Slot()
    def previous_page(self):
        """
        Move the UI back to previous page, skipping intermediate screens if needed
        """
        current_page = self.ui.stackedWidget.currentIndex()
        previous_page = current_page - 1

        if previous_page == _CUT_STEP and self.no_cut_for_entity:
            # Skip Cut selection screen
            previous_page = _ENTITY_STEP

        if previous_page == _ENTITY_TYPE_STEP:
            # Pure virtual step, no UI for it, so we skip it
            previous_page = _PROJECT_STEP

        if previous_page < 0:
            previous_page = _DROP_STEP

        self.ui.stackedWidget.goto_page(previous_page)

    @QtCore.Slot(int)
    def set_ui_for_step(self, step):
        """
        Set the UI for the given step:
        - Show hide / buttons
        - Clear out views for steps bigger than the given one
        - Reset selection for steps bigger than the given one

        :param step: One of our known steps
        """
        self._step = step
        # 0: drag and drop
        # 1: Project select
        # 2: Entity type select (virtual, combined in Entity view)
        # 3: Entity select
        # 4: Cut select
        # 5: Cut summary
        # 6: import completed
        if step == _DROP_STEP:
            # Clear various things when we hit the first screen
            # doing a reset
            self.ui.back_button.hide()
            self.ui.reset_button.hide()
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

        if step == _CUT_STEP:
            self.ui.skip_button.show()
            self.ui.select_button.setText("Compare")
        else:
            self.ui.skip_button.hide()
            self.ui.select_button.setText("Select")

        if step < _PROJECT_STEP:
            self.ui.projects_search_line_edit.clear()
            self.clear_project_view()
            self._selected_sg_entity[_PROJECT_STEP] = None

        if step < _ENTITY_TYPE_STEP:
            self.clear_entities_view()

        if step < _ENTITY_STEP:
            self.ui.entities_search_line_edit.clear()
            self.ui.create_entity_button.hide()
            self._selected_sg_entity[_ENTITY_STEP] = None

        if step < _CUT_STEP:
            # Reset the Cut view
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
            self.ui.select_button.setEnabled(self.has_valid_selection_for_step(step))
        else:
            self.ui.select_button.hide()

        if step != _ENTITY_STEP:
            # Only visible for this step
            self.ui.create_entity_button.hide()

        if step == _PROGRESS_STEP:
            self.ui.feedback_label.hide()
        else:
            self.ui.feedback_label.show()

        # Display info message in feedback line and other special things
        # based on the current step
        if step == _PROJECT_STEP:
            self.display_info_message(self._projects_view.info_message)
        elif step == _ENTITY_STEP:
            sg_entity_type = self._preload_entity_type
            if not sg_entity_type:
                # Shouldn't happen, but...
                raise RuntimeError("Don't have a selected Entity type...")
            sg_entity_type_name = sgtk.util.get_entity_type_display_name(
                self._app.sgtk,
                sg_entity_type,
            )
            if sg_entity_type == "Project":
                self.ui.create_entity_button.hide()
            else:
                self.ui.create_entity_button.show()
                self.ui.create_entity_button.setText("New %s" % sg_entity_type_name)
            self._logger.info("Showing %s(s)" % sg_entity_type_name)
            self.ui.entities_search_line_edit.setPlaceholderText(
                "Search %s" % sg_entity_type_name
            )
            entity_type_stacked_widget = self.ui.entities_type_stacked_widget
            active_view = None
            # Retrieve the Entity type view we should activate
            for i, view in enumerate(self._entities_views):
                if view.sg_entity_type == sg_entity_type:
                    active_view = view
                    entity_type_stacked_widget.setCurrentIndex(i)
                    break
            else:
                raise RuntimeError(
                    "Don't have an Entity type view for %s" % sg_entity_type
                )
            # Change the selection to the one held by the active view
            self._selected_sg_entity[_ENTITY_STEP] = active_view.selected_sg_entity
            self.display_info_message(active_view.info_message)
        elif step == _CUT_STEP:
            self.display_info_message(self._cuts_view.info_message)
        elif step == _SUMMARY_STEP:
            self.ui.email_button.show()
            self.ui.submit_button.show()
            self.display_info_message(self._cut_diffs_view.info_message)
            if self._processor.sg_cut:
                revision_number_str = ""
                if self._processor.sg_cut["revision_number"] is not None:
                    revision_number_str = (
                        "_%03d" % self._processor.sg_cut["revision_number"]
                    )
                self.ui.cut_summary_title_label.setText(
                    "Comparing %s and <b>%s</b> for %s <b>%s</b>"
                    % (
                        os.path.basename(self._processor.edl_file_path),
                        "%s%s" % (self._processor.sg_cut["code"], revision_number_str),
                        self._processor.entity_type_name,
                        self._processor.entity_name,
                    )
                )
            else:
                self.ui.cut_summary_title_label.setText(
                    "Comparing %s to Flow Production Tracking Shot Data for %s <b>%s</b>"
                    % (
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

    def has_valid_selection_for_step(self, step):
        """
        Return True is a valid selection is held for the given step

        :param step: One of our wizard style steps
        :returns: A boolean
        """
        if not self._selected_sg_entity[step]:
            # Nothing selected
            return False
        if (
            step == _ENTITY_STEP
            and self._selected_sg_entity[step]["type"] != self._preload_entity_type
        ):
            # Selection does not correspond to selected Entity type
            return False
        return True

    @QtCore.Slot(dict)
    def selection_changed(self, sg_entity):
        """
        Called when selection changes in intermediate screens

        :param sg_entity: The PTR Entity which was selected for the current step
        """
        # Keep track of what is selected in different views
        # so the select button at the bottom of the window can
        # trigger next step with current selection
        self._selected_sg_entity[self._step] = sg_entity
        self.ui.select_button.setEnabled(True)

    @QtCore.Slot()
    def skip_button_callback(self):
        """
        Allow to skip Cut comparison, by asking for Cut differences with an
        empty Cut dictionary
        """
        self.show_cut_diff({})

    @QtCore.Slot()
    def select_button_callback(self):
        """
        Callback for the select button

        :raises: RuntimeError in cases of inconsistencies
        """
        if not self._selected_sg_entity[self._step]:
            raise RuntimeError("No selection for current step %d" % self._step)
        elif self._step == _PROJECT_STEP:
            self.project_chosen(self._selected_sg_entity[self._step])
        elif self._step == _ENTITY_STEP:
            self.show_cuts(self._selected_sg_entity[self._step])
        elif self._step == _CUT_STEP:
            self.show_cut_diff(self._selected_sg_entity[self._step])
        else:
            # Should never happen
            raise RuntimeError("Invalid step %d for selection callback" % self._step)

    @QtCore.Slot(str)
    def show_entities(self, u_sg_entity_type):
        """
        Called when Entities needs to be shown for a particular Entity type.

        Ensures we have a view for the given Entity type.
        If needed, ask the data manager to retrieve a list of entities for this
        Entity type.

        :param u_sg_entity_type: A PTR Entity type, as a unicode string, e.g. u'Sequence'
        """
        sg_entity_type = sgutils.ensure_str(u_sg_entity_type)
        self._preload_entity_type = sg_entity_type
        # Save the value in user settings so it will persist across
        # sessions
        self._user_settings.save({"preload_entity_type": sg_entity_type})
        entity_type_stacked_widget = self.ui.entities_type_stacked_widget
        # Retrieve the Entity type view we should activate
        for i, view in enumerate(self._entities_views):
            if view.sg_entity_type == sg_entity_type:
                # Here we don't need the worker to retrieve additional data from PTR
                # so we don't emit any signal like in other show_xxxx slots
                # if we already have a view for the given Entity type, we are already
                # on the right screen, so, basically, we don't have anything to do
                break
        else:
            self._logger.debug("Creating entities view for %s" % sg_entity_type)
            # Create the needed page
            page_i = len(self._entities_views)
            page = entity_type_stacked_widget.widget(page_i)
            self._create_entity_type_view(sg_entity_type, page.layout())
            # Ask our data manager to retrieve entries for the given Entity type
            # we will receive a _ENTITY_TYPE_STEP step done signal from the data
            # manager when the data is available
            self.get_entities.emit(sg_entity_type)

    @QtCore.Slot()
    def show_projects(self):
        """
        Called when Projects need to be shown, just ask the data manager to retrieve
        a list of Projects
        """
        self._logger.info("Retrieving Project(s)")
        self.get_projects.emit()

    @QtCore.Slot(dict)
    def project_chosen(self, sg_project):
        """
        Called when the given Project becomes the active one.

        Just tell the data manager that the current Project changed

        :param sg_project: A PTR Project dictionary
        """
        self._logger.info("Using Project %s" % sg_project["name"])
        self.set_active_project.emit(sg_project)

    @QtCore.Slot(dict)
    def show_cuts(self, sg_entity):
        """
        Called when a PTR Entity was chosen and Cuts need to be shown for it

        Asks the data manager to retrieve Cuts linked to this Entity

        :param sg_entity: A PTR Entity dictionary
        """
        name = sg_entity.get(
            "code", sg_entity.get("name", sg_entity.get("title", "????"))
        )
        type_name = sgtk.util.get_entity_type_display_name(
            sgtk.platform.current_bundle().sgtk,
            sg_entity["type"],
        )
        self._logger.info("Retrieving Cuts for %s %s" % (type_name, name))
        self.ui.selected_entity_label.setText(
            "%s: <big><b>%s</big></b>"
            % (
                type_name,
                name,
            )
        )
        self.get_cuts_for_entity.emit(sg_entity)

    @QtCore.Slot(dict)
    def show_cut_diff(self, sg_cut):
        """
        Called when a PTR Cut was chosen and Cut differences need to be shown for
        it.

        By passing an empty Cut dictionary, the comparison to a previous Cut is skipped

        :param sg_cut: A PTR Cut or an empty dictionary
        """
        if sg_cut != {}:
            self._logger.info("Retrieving Cut information for %s" % sg_cut["code"])
        self.get_cut_diff.emit(sg_cut)

    @QtCore.Slot()
    def set_cut_summary_view_selectors(self):
        """
        Set labels on top views selectors in Cut summary view, from the current
        Cut summary
        """
        # Here we are taking a shortcut and accessing values directly from some
        # data owned by another thread. But, we are only reading pre-computed
        # int values, so it should be alright. If not, those values should be
        # emitted in the signal, so real data access would not be needed
        summary = self._processor.summary
        self.ui.new_select_button.setText(
            "New : %d" % summary.count_for_type(_DIFF_TYPES.NEW)
        )
        self.ui.cut_change_select_button.setText(
            "Cut Changes : %d" % summary.count_for_type(_DIFF_TYPES.CUT_CHANGE)
        )
        self.ui.omitted_select_button.setText(
            "Omitted : %d" % summary.count_for_type(_DIFF_TYPES.OMITTED)
        )
        self.ui.reinstated_select_button.setText(
            "Reinstated : %d" % summary.count_for_type(_DIFF_TYPES.REINSTATED)
        )
        self.ui.rescan_select_button.setText(
            "Rescan Needed : %d" % summary.rescans_count
        )
        self.ui.total_button.setText("Total : %d" % summary.total_count)

    def clear_entities_view(self):
        """
        Reset the page displaying available entities
        """
        for page_i, view in enumerate(self._entities_views):
            view.clear()
        self._entities_views = []

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
        Reset the Cut summary view page
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
        Called when a the Cut needs to be imported in Flow Production Tracking. Show a dialog where the
        user can review changes before importing the cut.
        """
        dialog = SubmitDialog(
            parent=self, title=self._processor.title, summary=self._processor.summary
        )
        dialog.submit.connect(self._processor.import_cut)
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()

    @QtCore.Slot(int)
    def show_settings_dialog(self, wizard_step):
        """
        Called when the settings dialog needs to be presented to the user. This can
        happen on almost every page of the animated stacked widget.

        :param wizard_step: One of our wizard steps
        """
        self._logger.debug("Settings at step %d" % wizard_step)
        show_settings_dialog = SettingsDialog(parent=self, wizard_step=wizard_step)
        show_settings_dialog.reset_needed.connect(self.reload_steps)
        show_settings_dialog.show()
        show_settings_dialog.raise_()
        show_settings_dialog.activateWindow()

    @QtCore.Slot(list)
    def reload_steps(self, steps):
        """
        Reload the given list of steps

        Called when user settings are changed and some steps are invalidated by
        these changes. Ask the data manager to reload the data for these steps,
        reset views if needed.

        :param steps: A list of wizard steps to reload, e.g. [_DROP_STEP, _SUMMARY_STEP]
        """
        # With current user settings, only two steps can be potentially affected
        # so for the time being, only support them and raise an error for others
        for step in steps:
            if step == _DROP_STEP:
                self.reload_step.emit(step)
            elif step == _SUMMARY_STEP:
                self.clear_cut_summary_view()
                self.reload_step.emit(step)
            else:
                raise NotImplementedError("Reloading step %d is not supported" % step)

    def create_entity(self, entity_type, fields):
        """
        Creates an Entity of the specified type and
        moves to the next screen with that Entity selected.

        :param entity_type: String, the Entity type to create.
        :param fields: Dict, fields to set on the new Entity, specified by
        the user in the create_entity dialog.
        """
        try:
            new_entity = self._app.shotgun.create(entity_type, fields)
            self.get_cuts_for_entity.emit(new_entity)
        except Exception as e:
            msg_box = QtGui.QMessageBox(parent=self, icon=QtGui.QMessageBox.Critical)
            msg_box.setIconPixmap(QtGui.QPixmap(":/tk_multi_importcut/error_64px.png"))
            msg_box.setText(_BAD_PERMISSIONS_MSG % (entity_type, entity_type))
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
            self._preload_entity_type, self._processor.sg_project, parent=self
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
            self._logger.warning("No selected Entity ...")
            return
        links = [
            "%s/detail/%s/%s"
            % (
                self._app.shotgun.base_url,
                self._processor.sg_entity["type"],
                self._processor.sg_entity["id"],
            )
        ]
        subject, body = self._processor.summary.get_report(self._processor.title, links)
        # Qt will encode the url for us
        mail_url = QtCore.QUrl("mailto:?subject=%s&body=%s" % (subject, body))
        self._logger.debug("Opening up %s" % mail_url)
        QtGui.QDesktopServices.openUrl(mail_url)

    @QtCore.Slot()
    def show_in_shotgun(self):
        """
        Called at the end of the import if the user clicks on the 'Show in PTR'
        button: shows the new Cut in default web browser and closes the app
        """
        sg_url = QtCore.QUrl(self._processor.sg_new_cut_url)
        QtGui.QDesktopServices.openUrl(sg_url)
        self.close()

    @QtCore.Slot()
    def show_help(self):
        """
        Called at the start of the import if user clicks on the "?"
        button: shows the documentation in the default web browser.
        """
        help_url = QtCore.QUrl(_DOCUMENTATION_URL)
        QtGui.QDesktopServices.openUrl(help_url)

    @QtCore.Slot(str, list)
    def display_exception(self, u_msg, exec_info):
        """
        Display a popup window with the error message and the exec_info
        in the "details"

        :param u_msg: A unicode string
        :param exec_info: A list of strings
        """
        msg = sgutils.ensure_str(u_msg)
        msg_box = QtGui.QMessageBox(parent=self, icon=QtGui.QMessageBox.Critical)
        msg_box.setIconPixmap(QtGui.QPixmap(":/tk_multi_importcut/error_64px.png"))
        msg_box.setText(msg)
        msg_box.setDetailedText("\n".join(exec_info))
        msg_box.setStandardButtons(QtGui.QMessageBox.Ok)
        msg_box.show()
        msg_box.raise_()
        msg_box.activateWindow()

    def closeEvent(self, event):
        """
        closeEvent handler

        Warn the user if it's not safe to quit, and leave the decision to him
        :param event: A QEvent
        """
        if self.is_busy():
            answer = QtGui.QMessageBox.warning(
                self,
                "Quit anyway ?",
                "Busy, quit anyway ?",
                QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok,
            )
            if answer != QtGui.QMessageBox.Ok:
                # Ignore close event to stop it from being processed
                event.ignore()
                return
        self._processor.quit()
        self._processor.wait()
        # Shutdown the download thread pool
        pool = DownloadRunner.get_thread_pool()
        pool.shutdown()
        # And wait for all threads to be done
        pool.waitForDone()
        # Let the close happen
        event.accept()

    def set_logger(self, level=logging.INFO):
        """
        Set the logger for this app

        :param level: A standard logging level
        """
        self._logger = get_logger()
        handler = BundleLogHandler(self._app)
        handler.new_message.connect(self.new_message)
        handler.new_error_with_exc_info.connect(self.display_exception)
        self._logger.addHandler(handler)

        # Copied over from tk-desktop and tk-multi-ingestdelivery
        if sgtk.util.is_macos():
            fname = os.path.join(
                os.path.expanduser("~"),
                "Library",
                "Logs",
                "Shotgun",
                "%s.log" % self._app.name,
            )
        elif sgtk.util.is_windows():
            fname = os.path.join(
                os.environ.get("APPDATA", "APPDATA_NOT_SET"),
                "Shotgun",
                "%s.log" % self._app.name,
            )
        elif sgtk.util.is_linux():
            fname = os.path.join(
                os.path.expanduser("~"), ".shotgun", "logs", "%s.log" % self._app.name
            )
        else:
            raise NotImplementedError("Unknown platform: %s" % sys.platform)

        # Create log directory if it doesn't already exist.
        log_dir = os.path.dirname(fname)
        if not os.path.isdir(log_dir):
            os.makedirs(log_dir)
        handler = logging.handlers.RotatingFileHandler(
            fname, maxBytes=1024 * 1024, backupCount=5
        )
        handler.addFilter(ShortNameFilter())
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(short_name)s %(message)s")
        )
        self._logger.addHandler(handler)

        self._logger.setLevel(level)

    def set_custom_style(self):
        """
        Append our custom style to the inherited style sheet

        If the 'css_watcher' setting is on, set up a file watcher which will
        reload the app style sheet file on changes
        """
        self._css_watcher = None
        this_folder = (
            self._app.disk_location
        )  # os.path.abspath(os.path.dirname(__file__))
        css_file = os.path.join(this_folder, "style.qss")
        if os.path.exists(css_file):
            self._load_css(css_file)
            # Add a watcher if css_watcher optional setting is set
            if self._app.get_setting("css_watcher"):
                self._css_watcher = QtCore.QFileSystemWatcher([css_file], self)
                self._css_watcher.fileChanged.connect(self.reload_css)

    def _load_css(self, css_file):
        """
        Load the given style sheet file onto the UI

        :param css_file: Full path a to a css file
        """
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
                    os.path.join(font_path, "OpenSans-Bold.ttf")
                )
                QtGui.QFontDatabase.addApplicationFont(
                    os.path.join(font_path, "OpenSans-Regular.ttf")
                )
                QtGui.QFontDatabase.addApplicationFont(
                    os.path.join(font_path, "OpenSans-CondLight.ttf")
                )
                QtGui.QFontDatabase.addApplicationFont(
                    os.path.join(font_path, "OpenSans-Light.ttf")
                )
                # Read css file
                f = open(css_file)
                css_data = f.read()
                f.close()
                # Append our add-ons to current sytle sheet at the top widget
                # level, children will inherit from it, without us affecting
                # other apps for this engine
                self.setStyleSheet(css_data)
            except Exception:
                self._app.log_warning("Unable to read style sheet %s" % css_file)

    @QtCore.Slot(str)
    def reload_css(self, u_path):
        """
        Reload the given style sheet file onto the UI
        Re-position the style sheet file watcher if needed

        :param u_path: Full path a to a css file, as a unicode string
        """
        path = sgutils.ensure_str(u_path)
        self._logger.info("Reloading %s" % path)
        self._load_css(path)
        # Some code editors rename files on save, so the watcher will
        # stop watching it. Check if the file is watched, re-attach it if not
        if self._css_watcher and path not in self._css_watcher.files():
            self._css_watcher.addPath(path)
        self._logger.info("%s loaded" % path)
        self.update()
