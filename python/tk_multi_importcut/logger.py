# Copyright (c) 2021 Autodesk, Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the ShotGrid Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the ShotGrid Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk, Inc.
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
        # Remove the last part which should be this file name
        logger_name = ".".join(logger_parts[:-1])
    else:
        logger_name = logger_parts[0]
    return logging.getLogger(logger_name)


class ShortNameFilter(logging.Filter):
    """
    A logging filter which adds a short_name and a base_name to records,
    which can be used in formatting string, e.g. "%(short_name)s %(msg)s"

    The short_name strips the two first parts of the logger path, allowing
    to not print the <uuid>.<app name> part in logs.

    The base_name is the last part in the split path
    """

    def __init__(self, name=""):
        super().__init__(name)

    def filter(self, record):
        """
        Filter the given record, adding short_name and base_name properties.

        :param record: A standard logging record
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
    A logging Handler to log messages with the app log_xxxx methods and emit
    messages through Qt Signals
    """

    class _QtEmitter(QtCore.QObject):
        """
        As BundleLogHandler does not derive from a QObject, we need a small
        class to emit Qt Signals
        """

        # Emitted when some new message is available
        # First parameter is the logging level
        # the second is the new message
        new_message = QtCore.Signal(int, str)
        # Emitted when an error was reported with some exc_info
        new_error_with_exc_info = QtCore.Signal(str, list)

        def __init__(self):
            QtCore.QObject.__init__(self)

    def __init__(self, bundle, *args, **kwargs):
        """
        Instantiate a new handler for the given bundle

        :param framework: A Toolkit Bundle
        :param args: Arbitrary list of parameters used in base class init
        :param kwargs: Arbitrary dictionary of parameters used in base class init
        """
        super(BundleLogHandler, self).__init__(*args, **kwargs)
        self._bundle = bundle
        self._qt_emitter = self._QtEmitter()

    @property
    def new_message(self):
        """
        Returns the new_message signal
        :returns: A Qt Signal
        """
        return self._qt_emitter.new_message

    @property
    def new_error_with_exc_info(self):
        """
        Returns the new_error_with_exc_info signal
        :returns: A Qt Signal
        """
        return self._qt_emitter.new_error_with_exc_info

    def emit(self, record):
        """
        Emit the given record

        If the record has some exec info, the new_error_with_exc_info signal will
        be emitted. If not, new_message will be emitted.

        :param record: A standard logging record
        """
        # Emit one of our signals, depending on if we have a traceback or not, so
        # listeners can log or display the message
        if record.exc_info is not None:
            self.new_error_with_exc_info.emit(
                record.getMessage(), traceback.format_tb(record.exc_info[2])
            )
            return
        self.new_message.emit(record.levelno, record.getMessage())
        if self._bundle:
            # Dispatch message to standard TK log_xxxx methods, except when the
            # current engine is tk-shotgun or tk-desktop:
            # - tk-shotgun : messages are displayed in a pop up window after
            #                the app is closed, which is confusing
            # - tk-desktop : messages are sent through a pipe to the desktop server
            #                and are logged in the tk-desktop log. We have our own
            #                logging file and sometimes tk-desktop will hang when
            #                writing data, so don't log anything
            engine_name = sgtk.platform.current_engine().name
            if engine_name == "tk-shotgun" or engine_name == "tk-desktop":
                return
            # Pick up the right framework method, given the record level
            if record.levelno == logging.INFO:
                self._bundle.log_info(record.getMessage())
            elif record.levelno == logging.INFO:
                self._bundle.log_debug(record.getMessage())
            elif record.levelno == logging.WARNING:
                self._bundle.log_warning(record.getMessage())
            elif record.levelno in [logging.ERROR, logging.CRITICAL]:
                self._bundle.log_error(record.getMessage())
