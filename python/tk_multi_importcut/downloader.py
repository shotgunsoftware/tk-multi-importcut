# Copyright (c) 2014 Shotgun Software Inc.
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
from .safe_shotgun import ThreadSafeShotgun
class DownloadRunner(QtCore.QRunnable):
    """
    """
    class _Notifier(QtCore.QObject):
        """
        QRunnable does not derive from QObject, so we need to have a small
        class to be able to emit signals
        """
        file_downloaded = QtCore.Signal(str)

    def __init__(self, sg_attachment, path):
        """
        """
        super(DownloadRunner, self).__init__()
        self._sg = ThreadSafeShotgun(sgtk.platform.current_bundle().shotgun)
        self._sg_attachment = sg_attachment
        self._path = path
        self._thread = None
        self._notifier = self._Notifier()

    @property
    def file_downloaded(self):
        return self._notifier.file_downloaded

    def run(self):
        """
        Actually run the runner
        """
        # Capture the thread we are running on
        self._thread = QtCore.QThread.currentThread()
        try :
            if isinstance(self._sg_attachment, str):
                self._sg.download_url(self._sg_attachment, self._path)
            else:
                attachment = self._sg.download_attachment(
                    attachment=self._sg_attachment,
                    file_path=self._path)
            self._notifier.file_downloaded.emit(self._path)
        except Exception,e:
            raise
        finally:
            pass
