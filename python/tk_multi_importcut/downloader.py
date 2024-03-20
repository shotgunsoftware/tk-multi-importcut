# Copyright (c) 2021 Autodesk, Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the ShotGrid Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the ShotGrid Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk, Inc.

# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.

from sgtk.platform.qt import QtCore
import sgtk


class DownloadThreadPool(QtCore.QThreadPool):
    """
    Thin wrapper around QThreadPool allowing to shut it down
    """

    abort = QtCore.Signal()

    def shutdown(self):
        """
        Shutdown this thread pool
        """
        self.abort.emit()

    def queue(self, runner):
        """
        Queue the given runner

        :param runner: A DownloadRunner instance
        """
        self.abort.connect(runner.abort)
        self.start(runner)


# We use a single download thread pool for all downloads
_download_thread_pool = DownloadThreadPool()


class DownloadRunner(QtCore.QRunnable):
    """
    A runner to download things from Flow Production Tracking
    """

    class _Notifier(QtCore.QObject):
        """
        QRunnable does not derive from QObject, so we need to have a small
        class to be able to emit signals
        """

        file_downloaded = QtCore.Signal(str)

        def __init__(self, *args, **kwargs):
            """
            Instantiate a new _Notifier
            :param args: Arbitrary list of parameters to send to base class init
            :param kwargs: Arbitrary dictionary of parameters to send to base class init
            """
            QtCore.QObject.__init__(self, *args, **kwargs)
            self._aborted = False

        @QtCore.Slot()
        def abort(self):
            """
            Allow to signal that the download should be aborted
            """
            self._aborted = True

    def __init__(self, sg_attachment, path):
        """
        Instantiate a new download runner

        :param sg_attachment: Either a URL or an attachment dictionary
        :param path: Full file path to save the downloaded data
        """
        super(DownloadRunner, self).__init__()
        self._sg_attachment = sg_attachment
        self._path = path
        self._thread = None
        self._notifier = self._Notifier()

    @classmethod
    def get_thread_pool(cls):
        """
        Return the download thread pool used by all downloaders

        :returns: A QThreadPool
        """
        return _download_thread_pool

    @property
    def file_downloaded(self):
        """
        Return the signal from the _notifier worker instance

        :returns: A QSignal
        """
        return self._notifier.file_downloaded

    @property
    def abort(self):
        """
        Pass through to access the _Notifier slot

        :returns: A QSignal
        """
        return self._notifier.abort

    def queue(self):
        """
        Queue this runner on the shared download thread pool
        """
        _download_thread_pool.queue(self)

    def run(self):
        """
        Actually run the runner
        """
        # Return immediately if the download was aborted
        if self._notifier._aborted:
            return
        sg = sgtk.platform.current_bundle().shotgun
        try:
            if isinstance(self._sg_attachment, str):
                sgtk.util.download_url(sg, self._sg_attachment, self._path)
            else:
                attachment = sg.download_attachment(
                    attachment=self._sg_attachment, file_path=self._path
                )
            self._notifier.file_downloaded.emit(self._path)
        except Exception:
            raise
        finally:
            pass
