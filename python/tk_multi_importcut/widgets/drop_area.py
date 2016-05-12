# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import sys

from tank.platform.qt import QtCore, QtGui


def drop_area(cls):
    """
    A class decorator which add needed overrides to any QWidget
    so it can behave like a drop area and emit something_dropped signals
    """
    class WrappedClass(cls):
        """
        Wrapping class
        """
        # Emitted when something is dropped on the widget
        something_dropped = QtCore.Signal(list)
        def __init__(self, *args, **kargs):
            """
            Instantiate the class and enable drops
            """
            super(WrappedClass, self).__init__(*args, **kargs)
            self.setAcceptDrops(True)
            self._set_property("dragging", False)
            self._supported_extensions = []

        def set_supported_extensions(self, ext_list):
            self._supported_extensions = ext_list

        # Override dragEnterEvent
        def dragEnterEvent( self, e):
            """
            Check if we can handle the drop, basically if we will receive local file path
            """
            # Set a property which can used to change the look of the widget
            # in a style sheet using a pseudo state, e.g. :
            # DropAreaLabel[dragging="true"] {
            #     border: 2px solid white;
            # }
            self._set_property("dragging", True)

            if e.mimeData().hasFormat("text/plain") :
                e.accept()
            elif e.mimeData().hasFormat("text/uri-list") :
                for url in e.mimeData().urls() :
                    _, ext = os.path.splitext(url.path())
                    if self._supported_extensions and ext.lower() in self._supported_extensions:
                        print "Do something here."
                    # Accept if there is at least one local file
                    if url.isLocalFile() :
                        e.accept()
                        break
                else :
                    e.ignore()
            else:
                e.ignore() 

        # Override dragLeaveEvent
        def dragLeaveEvent( self, e):
            """
            Just unset our dragging property
            """
            self._set_property("dragging", False)

        # Override dropEvent
        def dropEvent(self, e):
            """
            Process a drop event, build a list of local files and emit somethingDropped if not empty
            """
            self._set_property("dragging", False)
            if e.mimeData().hasFormat("text/plain") :
                contents = [ e.mimeData().text() ]
            else :
                urls = e.mimeData().urls()
                if sys.platform == "darwin":
                    # Fix for Yosemite and later, file paths are not actual file paths
                    # but weird /.file/id=6571367.18855673 values
                    # https://bugreports.qt-project.org/browse/QTBUG-24379
                    # https://gist.github.com/wedesoft/3216298
                    try:
                        # Custom Python (e.g. brewed ones) might not be able to
                        # import Foundation. In that case we do nothing and keep
                        # urls as they are, assuming the problem should be fixed
                        # in custom Python / PyQt / PySide
                        import Foundation
                        fixed_urls = []
                        for url in urls:
                            # It is fine to pass a regular file url to this method
                            # e.g. file:///foo/bar/blah.ext
                            fu = Foundation.NSURL.URLWithString_(url.toString()).filePathURL()
                            fixed_urls.append(QtCore.QUrl(str(fu)))
                        urls = fixed_urls
                    except:
                        pass
                contents = [ x.toLocalFile() for x in urls if x.isLocalFile() ]
            if contents :
                e.accept()
                self.something_dropped.emit( contents )
            else :
                e.ignore()

        def _set_property(self, name, value):
            """
            Helper to set custom properties which can be used in style sheets
            Set the value and do a unpolish / polish to force an update
            :param name: A property name
            :param value: A value for this property
            """
            self.setProperty(name, value)
            # We are using a custom property in style sheets
            # we need to force a style sheet re-computation with
            # unpolish / polish
            self.style().unpolish(self);
            self.style().polish(self);
            
    return WrappedClass

@drop_area
class DropAreaLabel(QtGui.QLabel):
    """
    Custom label widget so we can override drop callback and add a somethingDropped signal
    """
    pass

@drop_area
class DropAreaFrame(QtGui.QFrame):
    """
    Custom frame widget so we can override drop callback and add a somethingDropped signal
    """
    pass

@drop_area
class DropAreaTableView(QtGui.QTableView):
    """
    Custom table view so we can override drop callback and add a somethingDropped signal
    """
    pass

@drop_area
class DropAreaScrollArea(QtGui.QScrollArea):
    """
    Custom scroll area widget so we can override drop callback and add a somethingDropped signal
    """
    pass

