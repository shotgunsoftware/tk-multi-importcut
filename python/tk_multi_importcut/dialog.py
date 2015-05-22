# Copyright (c) 2014 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk
import os
import sys
import logging
import tempfile

# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
from sgtk.platform.qt import QtCore, QtGui
# Import needed Framework
widgets = sgtk.platform.import_framework("tk-framework-wb", "widgets")
# Rename the drop area label to the name we chose in Designer when promoting our label
DropAreaLabel = widgets.drop_area_label.DropAreaLabel
AnimatedStackedWidget = widgets.animated_stacked_widget.AnimatedStackedWidget
from .search_widget import SearchWidget
from .entity_line_widget import EntityLineWidget

# Custom widgets must be imported before importing the UI
from .ui.dialog import Ui_Dialog

from .processor import Processor
from .logger import BundleLogHandler, get_logger
from .sequences_view import SequencesView
from .cuts_view import CutsView
from .cut_diff import _DIFF_TYPES
from .cut_diffs_view import CutDiffsView
from .submit_dialog import SubmitDialog
from .downloader import DownloadRunner

def show_dialog(app_instance):
    """
    Shows the main dialog window.
    """
    # in order to handle UIs seamlessly, each toolkit engine has methods for launching
    # different types of windows. By using these methods, your windows will be correctly
    # decorated and handled in a consistent fashion by the system. 
    
    # we pass the dialog class to this method and leave the actual construction
    # to be carried out by toolkit.
    app_instance.engine.show_dialog("Import Cut", app_instance, AppDialog)
    


class AppDialog(QtGui.QWidget):
    """
    Main application dialog window
    """
    new_edl = QtCore.Signal(str)
    get_sequences = QtCore.Signal()
    show_cuts_for_sequence = QtCore.Signal(dict)
    show_cut_diff = QtCore.Signal(dict)
    def __init__(self):
        """
        Constructor
        """
        # first, call the base class and let it do its thing.
        QtGui.QWidget.__init__(self)
        
        # now load in the UI that was created in the UI designer
        self.ui = Ui_Dialog() 
        self.ui.setupUi(self)
        
        # most of the useful accessors are available through the Application class instance
        # it is often handy to keep a reference to this. You can get it via the following method:
        self._app = sgtk.platform.current_bundle()
        
        self._busy = False

        # via the self._app handle we can for example access:
        # - The engine, via self._app.engine
        # - A Shotgun API instance, via self._app.shotgun
        # - A tk API instance, via self._app.tk 
        
        # lastly, set up our very basic UI
        self.set_custom_style()
        self.set_logger()
        # Keep this thread for UI stuff
        # Handle data and processong in a separate thread
        self._processor = Processor()
        self.new_edl.connect(self._processor.new_edl)
        self.get_sequences.connect(self._processor.retrieve_sequences)
        self.show_cuts_for_sequence.connect(self._processor.retrieve_cuts)
        self.show_cut_diff.connect(self._processor.show_cut_diff)
        self._processor.step_done.connect(self.step_done)
        self._processor.got_busy.connect(self.set_busy)
        self._processor.got_idle.connect(self.set_idle)
        self.ui.stackedWidget.first_page_reached.connect(self._processor.reset)
        self._processor.start()
        
        # Let's do something when something is dropped
        self.ui.drop_area_label.something_dropped.connect(self.process_drop)

        # Instantiate a sequences view handler
        self._sequences_view = SequencesView(self.ui.sequence_grid)
        self._sequences_view.sequence_chosen.connect(self.show_sequence)
        self._processor.new_sg_sequence.connect(self._sequences_view.new_sg_sequence)
        self.ui.sequences_search_line_edit.search_edited.connect(self._sequences_view.search)
        self.ui.sequences_search_line_edit.search_changed.connect(self._sequences_view.search)

        # Instantiate a cuts view handler
        self._cuts_view = CutsView(self.ui.cuts_grid, self.ui.cuts_sort_button)
        self._cuts_view.show_cut_diff.connect(self.show_cut)
        self._processor.new_sg_cut.connect(self._cuts_view.new_sg_cut)
        self.ui.search_line_edit.search_edited.connect(self._cuts_view.search)
        self.ui.search_line_edit.search_changed.connect(self._cuts_view.search)

        # Instantiate a cut differences view handler
        self._cut_diffs_view = CutDiffsView(self.ui.cutsummary_list)
        self._cut_diffs_view.totals_changed.connect(self.set_cut_summary_view_selectors)
        self._processor.totals_changed.connect(self.set_cut_summary_view_selectors)
        self._processor.new_cut_diff.connect(self._cut_diffs_view.new_cut_diff)
        self._processor.delete_cut_diff.connect(self._cut_diffs_view.delete_cut_diff)

        # Cut summary view selectors
        self.ui.new_select_button.toggled.connect( lambda x : self._cut_diffs_view.set_display_summary_mode(x, _DIFF_TYPES.NEW))
        self.ui.cut_change_select_button.toggled.connect( lambda x : self._cut_diffs_view.set_display_summary_mode(x, _DIFF_TYPES.CUT_CHANGE))
        self.ui.omitted_select_button.toggled.connect( lambda x : self._cut_diffs_view.set_display_summary_mode(x, _DIFF_TYPES.OMITTED))
        self.ui.reinstated_select_button.toggled.connect( lambda x : self._cut_diffs_view.set_display_summary_mode(x, _DIFF_TYPES.REINSTATED))
        self.ui.rescan_select_button.toggled.connect( lambda x : self._cut_diffs_view.set_display_summary_mode(x, 100))
        self.ui.total_button.toggled.connect( lambda x : self._cut_diffs_view.set_display_summary_mode(x, -1))
        self.ui.only_vfx_check_box.toggled.connect(self._cut_diffs_view.display_vfx_cuts)

        self.set_ui_for_step(0)
        self.ui.back_button.clicked.connect(self.previous_page)
        self.ui.stackedWidget.first_page_reached.connect(self.reset)
        self.ui.stackedWidget.currentChanged.connect(self.set_ui_for_step)
        self.ui.cancel_button.clicked.connect(self.close_dialog)
        self.ui.reset_button.clicked.connect(self.do_reset)
        self.ui.email_button.clicked.connect(self.email_cut_changes)
        self.ui.submit_button.clicked.connect(self.import_cut)
        self.ui.shotgun_button.clicked.connect(self.show_in_shotgun)

        self._processor.progress_changed.connect(self.ui.progress_bar.setValue)
        self.ui.progress_bar.hide()

    @property
    def no_cut_for_sequence(self):
        return self._processor.no_cut_for_sequence

    @QtCore.Slot()
    def do_reset(self):
        """
        Reset callback, going back to the first page
        """
        self.goto_step(0)

    @QtCore.Slot()
    def reset(self):
        """
        Called when the first page is reached
        """
        self.set_ui_for_step(0)

    @QtCore.Slot(int)
    def step_done(self, which):
        """
        Called when a step is done, and next page can be displayed
        """
        self.goto_step(which+1)

    @QtCore.Slot(list)
    def process_drop(self, paths):
        """
        Process a drop event, paths can either be
        local filesystem paths or SG urls
        """
        if len(paths) != 1:
            QtGui.QMessageBox.warning(
                self,
                "Can't process drop",
                "Please drop only on file at a time",
            )
            return
        self.new_edl.emit(paths[0])
        self.ui.sequences_label.setText("Importing %s" % os.path.basename(paths[0]))
        #self._logger.info( "Processing %s" % (paths[0] ))

    @QtCore.Slot(int, str)
    def new_message(self, levelno, message):
        """
        Display a new message in the feedback widget
        """
        if levelno == logging.ERROR or levelno == logging.CRITICAL:
            self.ui.feedback_label.setStyleSheet( "color: #FC6246")
        else:
            self.ui.feedback_label.setStyleSheet("")
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
        Skip the cuts view page if needed
        """
        current_page = self.ui.stackedWidget.currentIndex()
        if current_page == 3 and self.no_cut_for_sequence:
            self.ui.stackedWidget.goto_page(1)
        else:
            self.ui.stackedWidget.prev_page()

    @QtCore.Slot(int)
    def set_ui_for_step(self, step):
        """
        Set the UI for the given step
        """
        # 0 : drag and drop
        # 1 : sequence select
        # 2 : cut select
        # 3 : cut summary
        # 4 : import completed
        if step < 1:
            self.ui.back_button.hide()
            self.ui.reset_button.hide()
            self.ui.sequences_search_line_edit.clear()
            self.clear_sequence_view()
        else:
            self.ui.reset_button.show()
            self.ui.back_button.show()

        if step < 2:
            self.clear_cuts_view()
            self.ui.search_line_edit.clear()

        if step < 3:
            self.clear_cut_summary_view()
            self.ui.email_button.hide()
            self.ui.submit_button.hide()
        else:
            self.ui.email_button.show()
            self.ui.submit_button.show()

        if step == 4:
            self.ui.success_label.setText(
                "<big>Cut %s successfully imported</big>" % self._processor.sg_new_cut["code"]
            )
            self.ui.back_button.hide()
            self.ui.email_button.hide()
            self.ui.submit_button.hide()


    @QtCore.Slot(dict)
    def show_sequence(self, sg_entity):
        """
        Called when cuts needs to be shown for a particular sequence
        """
        self._logger.info("Retrieving cuts for %s" % sg_entity["code"] )
        self.ui.selected_sequence_label.setText("Showing cuts for Sequence <big><b>%s</big></b>" % sg_entity["code"] )
        self.show_cuts_for_sequence.emit(sg_entity)

    @QtCore.Slot(dict)
    def show_cut(self, sg_cut):
        """
        Called when cut changes needs to be shown for a particular sequence/cut
        """
        self._logger.info("Retrieving cut information for %s" % sg_cut["code"] )
        self.show_cut_diff.emit(sg_cut)


    @QtCore.Slot()
    def set_cut_summary_view_selectors(self):
        """
        Set labels on top views selectors in Cut summary view, from the current 
        cut summary
        """
        summary = self._processor.summary
        self.ui.new_select_button.setText("New : %d" % summary.count_for_type(_DIFF_TYPES.NEW))
        self.ui.cut_change_select_button.setText("Cut Changes : %d" % summary.count_for_type(_DIFF_TYPES.CUT_CHANGE))
        self.ui.omitted_select_button.setText("Omitted : %d" % summary.count_for_type(_DIFF_TYPES.OMITTED))
        self.ui.reinstated_select_button.setText("Reinstated : %d" % summary.count_for_type(_DIFF_TYPES.REINSTATED))
        self.ui.rescan_select_button.setText("Rescan Needed : %d" % summary.rescans_count)
        self.ui.total_button.setText("Total : %d" % len(summary))

    def clear_sequence_view(self):
        """
        Reset the page displaying available sequences
        """
        self._sequences_view.clear()

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
        #self.generate_report()
        dialog = SubmitDialog(
            parent=self,
            title=self._processor.title,
            summary=self._processor.summary)
        dialog.submit.connect(self._processor.import_cut)
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()

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
        self._logger.debug("Opening up %s" % mail_url )
        QtGui.QDesktopServices.openUrl(mail_url)

    @QtCore.Slot()
    def show_in_shotgun(self):
        sg_url = QtCore.QUrl(self._processor.sg_new_cut_url)
        QtGui.QDesktopServices.openUrl(sg_url)
        self.close()

    def generate_report(self):
#        Could be used to generate a report ?
#
#        pixmap = QtGui.QPixmap.grabWidget(self.ui.cut_summary_widgets)
#        pixmap.save("/tmp/cut_report.svg", format="SVG")

        #First render the widget to a QPicture, which stores QPainter commands.
        pic = QtGui.QPicture(formatVersion=7)
        picPainter = QtGui.QPainter()
        picPainter.begin(pic)
        for i in range(0, self.ui.cutsummary_list.count()-1):
            witem = self.ui.cutsummary_list.itemAt(i)
            widget = witem.widget()
            widget.ui.icon_label.render(picPainter, QtCore.QPoint())
            #picPainter.drawText(QtCore.QPoint(), widget.ui.shot_name_label.text())
        picPainter.end()
        #pic.save("/tmp/cut_grab.pic")
        pic_size = pic.boundingRect()
        # Set up the printer
        printer = QtGui.QPrinter(QtGui.QPrinter.ScreenResolution)
        #printer.setOutputFormat(QtGui.QPrinter.PdfFormat)
        printer.setOutputFileName("/tmp/cut_summary_report.pdf")
        printer.setOutputFormat(QtGui.QPrinter.NativeFormat)
        #printer.setOutputFormat(QtGui.QPrinter.PdfFormat)
        page_rect = printer.pageRect()
        printer.newPage()
        print_size = printer.pageRect(QtGui.QPrinter.DevicePixel)
        try:
            # Finally, draw the QPicture to your printer
            painter = QtGui.QPainter()
            painter.begin(printer)
            
#            painter.scale(
#                print_size.width()/float(pic_size.width()), print_size.width()/float(pic_size.width())
#                )
            painter.drawPicture(QtCore.QPointF(0, 0), pic);
            #painter.drawText(0,0, "HELLO WORLD")
        finally:
            painter.end()

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
                evt.ignore() # For close event, ignore stop them to be processed
                return
        self._processor.quit()
        self._processor.wait()
        # Let the close happen
        evt.accept()

    def set_logger(self, level=logging.INFO):
        """
        Retrieve a logger
        """
        self._logger = get_logger()
        handler = BundleLogHandler(self._app)
        handler.new_message.connect(self.new_message)
        self._logger.addHandler(handler)
        self._logger.setLevel(level)

    def set_custom_style(self):
        """
        Append our custom style to the inherited style sheet
        """
        this_folder = os.path.abspath(os.path.dirname(__file__))
        css_file = os.path.join(this_folder, "ui", "style_sheet.css")
        if os.path.exists(css_file):
            try:
                # Read css file
                f = open(css_file)
                css_data = f.read()
                f.close()
                # Append our add ons to current sytle sheet at the top widget
                # level, children will inherit from it, without us affecting
                # other apps for this engine
                self.setStyleSheet(css_data)
            except Exception,e:
                self._app.log_warning( "Unable to read style sheet %s" % css_file )

        
