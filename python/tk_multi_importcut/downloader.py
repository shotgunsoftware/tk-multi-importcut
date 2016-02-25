# Copyright (c) 2015 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import requests

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
        try :
            if isinstance(self._sg_attachment, str):
                download_url(sg, self._sg_attachment, self._path)
            else:
                # todo: test this code. But how do we create a situation
                # where the thumbnail (is it always a thumbnail?) an
                # attachment and not a string path to an aws bucket?
                attachment = sg.download_attachment(
                    attachment=self._sg_attachment,
                    file_path=self._path)
            self._notifier.file_downloaded.emit(self._path)
        except Exception,e:
            raise
        finally:
            pass


def download_url(self, url, location):
    """
    Downloads a file from a given url.
    This method will take into account any proxy settings which have
    been defined in the Shotgun connection parameters.
    
    :param url: url to download
    :param location: path on disk where the payload should be written.
                     this path needs to exists and the current user needs
                     to have write permissions
    :returns: nothing
    """

    proxies = {}
    if self.config.proxy_server:
        # handle proxy auth
        if self.config.proxy_user and self.config.proxy_pass:
            auth_string = "%s:%s@" % (self.config.proxy_user, self.config.proxy_pass)
        else:
            auth_string = ""
        proxy_addr = "http://%s%s:%d" % (auth_string, self.config.proxy_server, self.config.proxy_port)
        proxies["http"] = proxy_addr
        proxies["https"] = proxy_addr
    try:
        response = requests.get(url, proxies=proxies)
        response.raise_for_status()
        # Write out the content into the given file
        f = open(location, "wb")
        try:
            f.write(response.content)
        finally:
            f.close()
    except Exception, e:
        print "Could not download contents of url '%s'." % url
        raise e