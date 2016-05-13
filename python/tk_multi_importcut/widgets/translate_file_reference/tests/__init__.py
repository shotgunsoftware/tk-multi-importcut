# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import sys
import translate_file_reference

from PySide import QtGui


class View(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, e):
        urls = e.mimeData().urls()
        print urls
        print translate_file_reference.translate_url(urls[0].toString())

app = QtGui.QApplication(sys.argv)
view = View()
view.show()
app.exec_()
