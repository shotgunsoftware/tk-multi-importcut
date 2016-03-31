# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.

from sgtk.platform.qt import QtCore
import sgtk


class DownloadRunner(QtCore.QRunnable):
    """
    A runner to download things from Shotgun
    """
    class _Notifier(QtCore.QObject):
        """
        QRunnable does not derive from QObject, so we need to have a small
        class to be able to emit signals
        """
        file_downloaded = QtCore.Signal(str)

    def __init__(self, sg_attachment, path):
        """
        Instantiate a new download runner

        :param sg_attachment: Either a Shotgun URL or an attachment dictionary
        :param path: Full file path to save the downloaded data
        """
        super(DownloadRunner, self).__init__()
        self._sg_attachment = sg_attachment
        self._path = path
        self._thread = None
        self._notifier = self._Notifier()

    @property
    def file_downloaded(self):
        """
        Return the signal from the _notifier worker instance
        """
        return self._notifier.file_downloaded

    def run(self):
        """
        Actually run the runner
        """
        sg = sgtk.platform.current_bundle().shotgun
        try:
            if isinstance(self._sg_attachment, str):
                sgtk.util.download_url(sg, self._sg_attachment, self._path)
            else:
                # todo: test this code. But how do we create a situation
                # where the thumbnail (is it always a thumbnail?) an
                # attachment and not a string path to an aws bucket?
                attachment = sg.download_attachment(
                    attachment=self._sg_attachment,
                    file_path=self._path)
            self._notifier.file_downloaded.emit(self._path)
        except Exception, e:
            raise
        finally:
            pass
