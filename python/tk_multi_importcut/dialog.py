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

# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
from sgtk.platform.qt import QtCore, QtGui
# Import needed Framework
widgets = sgtk.platform.import_framework("tk-framework-wb", "widgets")
# Rename the drop area label to the name we chose in Designer when promoting our label
DropAreaLabel = widgets.drop_area_label.DropAreaLabel
AnimatedStackedWidget = widgets.animated_stacked_widget.AnimatedStackedWidget
from .ui.dialog import Ui_Dialog

from .processor import Processor
from .logger import BundleLogHandler, get_logger
from .sequence_widget import SequenceCard
from .cut_diff import CutDiff
from .cut_diff_widget import CutDiffCard
from .submit_dialog import SubmitDialog
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
    show_cut_for_sequence = QtCore.Signal(dict)
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
        self.show_cut_for_sequence.connect(self._processor.show_cut_for_sequence)
        self._processor.step_done.connect(self.step_done)
        self._processor.new_sg_sequence.connect(self.new_sg_sequence)
        self._processor.new_cut_diff.connect(self.new_cut_diff)
        self._processor.got_busy.connect(self.set_busy)
        self._processor.got_idle.connect(self.set_idle)
        self.ui.stackedWidget.first_page_reached.connect(self._processor.reset)
        self._processor.start()
        
        # Let's do something when something is dropped
        self.ui.drop_area_label.something_dropped.connect(self.process_drop)
    
        self.set_ui_for_step(0)
        self.ui.back_button.clicked.connect(self.ui.stackedWidget.prev_page)
        self.ui.stackedWidget.first_page_reached.connect(self.reset)
        self.ui.stackedWidget.currentChanged.connect(self.set_ui_for_step)
        self.ui.cancel_button.clicked.connect(self.close_dialog)
        self.ui.reset_button.clicked.connect(self.do_reset)
        self.ui.submit_button.clicked.connect(self.import_cut)

    @QtCore.Slot()
    def do_reset(self):
        self.goto_step(0)

    @QtCore.Slot()
    def reset(self):
        self.set_ui_for_step(0)

    @QtCore.Slot(int)
    def step_done(self, which):
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
        #self._logger.info( "Processing %s" % (paths[0] ))

    @QtCore.Slot(int, str)
    def new_message(self, levelno, message):
        if levelno == logging.ERROR or levelno == logging.CRITICAL:
            self.ui.feedback_label.setStyleSheet( "color: #FC6246")
        else:
            self.ui.feedback_label.setStyleSheet("")
        self.ui.feedback_label.setText(message)

    @QtCore.Slot()
    def close_dialog(self):
        self.close()

    @property
    def hide_tk_title_bar(self):
        return False

    def is_busy(self):
        return self._busy

    @QtCore.Slot()
    def set_busy(self):
        self._busy = True
        # Prevent some buttons to be used
        self.ui.back_button.setEnabled(False)
        self.ui.reset_button.setEnabled(False)
        self.ui.email_button.setEnabled(False)
        self.ui.submit_button.setEnabled(False)

    @QtCore.Slot()
    def set_idle(self):
        self._busy = False
        # Allow all buttons to be used
        self.ui.back_button.setEnabled(True)
        self.ui.reset_button.setEnabled(True)
        self.ui.email_button.setEnabled(True)
        self.ui.submit_button.setEnabled(True)

    def goto_step(self, which):
        self.set_ui_for_step(which)
        self.ui.stackedWidget.goto_page(which)

        if which == 1: # Ask the processor to retrieve sequences
            self.get_sequences.emit()

    @QtCore.Slot(int)
    def set_ui_for_step(self, step):
        """
        Set the UI for the given step
        """
        # 0 : drag and drop
        # 1 : sequence select
        # 2 : cut summary
        # 3 : import completed
        if step < 1:
            self.ui.back_button.hide()
            self.ui.reset_button.hide()
            self.clear_sequence_view()
        else:
            self.ui.reset_button.show()
            self.ui.back_button.show()

        if step < 2:
            self.clear_cut_summary_view()
            self.ui.email_button.hide()
            self.ui.submit_button.hide()
        else:
            self.ui.email_button.show()
            self.ui.submit_button.show()

        if step == 3:
            self.ui.email_button.hide()
            self.ui.submit_button.hide()

    @QtCore.Slot(dict)
    def new_sg_sequence(self, sg_entity):
        i = self.ui.sequence_grid.count() -1 # We have a stretcher
        # Remove it
        spacer = self.ui.sequence_grid.takeAt(i)
        row = i / 2
        column = i % 2
        self._logger.debug("Adding %s at %d %d %d" % ( sg_entity, i, row, column))
        widget = SequenceCard(None, sg_entity)
        widget.selected.connect(self.sequence_selected)
        self.ui.sequence_grid.addWidget(widget, row, column, )
        self.ui.sequence_grid.setRowStretch(row, 0)
        self.ui.sequence_grid.addItem(spacer, row+1, 0, colSpan=2 )
        self.ui.sequence_grid.setRowStretch(row+1, 1)

    @QtCore.Slot(dict)
    def sequence_selected(self, sg_entity):
        self._logger.info("Retrieving cut information for %s" % sg_entity["code"] )
        self.show_cut_for_sequence.emit(sg_entity)
        self.step_done(1)

    @QtCore.Slot(CutDiff)
    def new_cut_diff(self, cut_diff):
        self._logger.debug("Adding %s" % cut_diff.name)
        widget = CutDiffCard(parent=None, cut_diff=cut_diff)
        # Retrieve where we should insert it
        # Last widget is a stretcher, so we stop at self.ui.cutsummary_list.count()-2
        cut_order = widget.cut_order
        for i in range(0, self.ui.cutsummary_list.count()-1):
            witem = self.ui.cutsummary_list.itemAt(i)
            if witem.widget().cut_order > cut_order:
                self.ui.cutsummary_list.insertWidget(i, widget)
                break
        else:
            self.ui.cutsummary_list.insertWidget(self.ui.cutsummary_list.count()-1, widget)

    def clear_sequence_view(self):
        count = self.ui.sequence_grid.count() -1 # We have stretcher
        for i in range(count-1, -1, -1):
            witem = self.ui.sequence_grid.takeAt(i)
            widget = witem.widget()
            widget.close()
        # print self.ui.sequence_grid.count()

    def clear_cut_summary_view(self):
        count = self.ui.cutsummary_list.count() -1 # We have stretcher
        for i in range(count-1, -1, -1):
            witem = self.ui.cutsummary_list.takeAt(i)
            widget = witem.widget()
            widget.close()

    @QtCore.Slot()
    def import_cut(self):
        #self.generate_report()
        dialog = SubmitDialog(parent=self, title=self._processor.title)
        dialog.submit.connect(self._processor.import_cut)
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()

    def generate_report(self):
#        Could be used to generate a report ?
#
#        pixmap = QtGui.QPixmap.grabWidget(self.ui.cut_summary_widgets)
#        pixmap.save("/tmp/cut_report.png", format="PNG")

        #First render the widget to a QPicture, which stores QPainter commands.
        pic = QtGui.QPicture()
        picPainter = QtGui.QPainter(pic)
        self.ui.cut_summary_widgets.render(picPainter, QtCore.QPoint())
        picPainter.end()
     
        # Set up the printer
        printer = QtGui.QPrinter(QtGui.QPrinter.HighResolution)
        printer.setOutputFormat(QtGui.QPrinter.PdfFormat)
        printer.setOutputFileName("/tmp/cut_summary_report.pdf")
     
        # Finally, draw the QPicture to your printer
        painter = QtGui.QPainter()
        painter.begin(printer)
        painter.drawPicture(QtCore.QPointF(0, 0), pic);
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

        
