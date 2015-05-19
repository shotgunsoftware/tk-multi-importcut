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
from sgtk.platform.qt import QtCore, QtGui

class EntityLineEdit(QtGui.QLabel):
    """
    A Widget allowing to edit SG entity names with some helpers
    """
    def __init__(self, *args, **kwargs):
        super(EntityLineEdit, self).__init__(*args, **kwargs)