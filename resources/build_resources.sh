#!/usr/bin/env bash
# 
# Copyright (c) 2021 Autodesk, Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the ShotGrid Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the ShotGrid Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Autodesk, Inc.

# The path to output all built .py files to: 
UI_PYTHON_PATH=../python/tk_multi_importcut/ui
PYTHON_BASE="/Applications/Shotgun.app/Contents/Resources/Python"

# Helper functions to build UI files
function build_qt {
    echo " > Building " $2
    
    # compile ui to python
    $1 $2 > $UI_PYTHON_PATH/$3.py
    
    # replace PySide imports with tank.platform.qt and remove line containing Created by date
    sed -i $UI_PYTHON_PATH/$3.py -e "s/from PySide import/from tank.platform.qt import/g" -e "/# Created:/d"
}

function build_ui {
    build_qt "${PYTHON_BASE}/bin/python ${PYTHON_BASE}/bin/pyside-uic --from-imports" "$1.ui" "$1"
}

function build_res {
    build_qt "${PYTHON_BASE}/bin/pyside-rcc -py3" "$1.qrc" "$1_rc"
}


# build UI's:
echo "building user interfaces..."
build_ui dialog
# add any additional .ui files you want converted here!
build_ui project_card
build_ui entity_card
build_ui cut_card
build_ui cut_diff_card
build_ui submit_dialog
build_ui settings_dialog
build_ui create_entity_dialog

# build resources
echo "building resources..."
build_res resources

