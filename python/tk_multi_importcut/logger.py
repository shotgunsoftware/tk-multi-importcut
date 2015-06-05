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
import logging
import traceback
from sgtk.platform.qt import QtCore

def get_logger():
    """
    Return a logger for this app
    """
    logger_parts = __name__.split(".")
    if len(logger_parts) > 1:
        # Remove the last part which should be this file
        # name
        logger_name = ".".join(logger_parts[:-1])
    else:
        logger_name = logger_parts[0]
    return logging.getLogger(logger_name)

class ShortNameFilter(logging.Filter):
    """
    A logging filter which add a short_name and a base_name to records,
    which can be used in formatting string, e.g. "%(short_name)s %(msg)s"

    The short_name strip the two first parts in the logger path, allowing
    to not print the <uuid>.<app name> part in logs.
    
    The base_name is the last part in the splitted path
    """

    def __init__(self, name=""):
        super(ShortNameFilter, self).__init__(name)

    def filter(self, record):
        """
        Filter the given record, adding short_name and base_name properties.
        :return: True
        """
        record.short_name = ""
        parts = record.name.split(".")
        if len(parts) > 2:
            record.short_name = ".".join(parts[2:])
        record.base_name = parts[-1]
        return True

class BundleLogHandler(logging.StreamHandler):
    """
    A logging Handler to log messages with the app log_xxxx methods
    """
    class _QtEmitter(QtCore.QObject):
        # Emitted when some new message is available
        # First parameter is the logging level
        # the second is the new message
        new_message = QtCore.Signal(int,str)
        # Emitted when an error was reported with some exc_info
        new_error_with_exc_info = QtCore.Signal(str,list)

        def __init__(self):
            QtCore.QObject.__init__(self)
    
    def __init__(self, bundle, *args, **kwargs):
        """
        Instantiante a new handler for the given Framework
        
        :param framework: A Toolkit framework
        """
        super(BundleLogHandler, self).__init__(*args, **kwargs)
        self._bundle = bundle
        self._qt_emitter = self._QtEmitter()
        
    @property
    def new_message(self):
        return self._qt_emitter.new_message

    @property
    def new_error_with_exc_info(self):
        return self._qt_emitter.new_error_with_exc_info

    def emit(self, record):
        """
        Emit the given record
        """
        if record.exc_info is not None:
            self.new_error_with_exc_info.emit(
                record.getMessage(),
                traceback.format_tb(record.exc_info[2])
            )
        self.new_message.emit(record.levelno, record.getMessage())
        if self._bundle:
            # Pick up the right framework method, given the record level
            if record.levelno == logging.INFO:
                self._bundle.log_info(record.getMessage())
            elif record.levelno == logging.INFO:
                self._bundle.log_debug(record.getMessage())
            elif record.levelno == logging.WARNING:
                self._bundle.log_warning(record.getMessage())
            elif record.levelno in [logging.ERROR, logging.CRITICAL]:
                self._bundle.log_error(record.getMessage())

