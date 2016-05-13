// Copyright (c) 2015 Shotgun Software Inc.

// CONFIDENTIAL AND PROPRIETARY

// This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
// Source Code License included in this distribution package. See LICENSE.
// By accessing, using, copying or modifying this work you indicate your
// agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
// not expressly granted therein are reserved by Shotgun Software Inc.

#ifndef Py_TRANSLATE_FILE_REFERENCE_MODULE_H
#define Py_TRANSLATE_FILE_REFERENCE_MODULE_H

#ifdef __cplusplus
extern "C" {
#endif

// Structure for the C API
//
// Put anything accessible to other modules at the C level
// into this structure.
typedef struct {
    char filler; // Need to have at least one member
} Py_TRANSLATE_FILE_REFERENCE_CAPI;


#ifdef TRANSLATE_FILE_REFERENCE_MODULE
// Used when building the module

/*******************************************************************************
 * @brief Translate a given url into the real file path
 *
 * @param module The python object for the current module
 * @param url The url to translate
 *
 * @return translated url
 ******************************************************************************/
PyObject *translate_url(PyObject *module, const char *url);

#else // #ifdef TRANSLATE_FILE_REFERENCE_MODULE

// Used when including outside the module
static Py_TRANSLATE_FILE_REFERENCE_CAPI *Py_TRANSLATE_FILE_REFERENCEAPI;

// Macro to pull the c api out of the module
#define Py_TRANSLATE_FILE_REFERENCE_IMPORT \
    Py_TRANSLATE_FILE_REFERENCE_API = (Py_TRANSLATE_FILE_REFERENCE_CAPI *)PyCObject_Import("translate_file_reference", "translate_file_reference_CAPI")

#endif // TRANSLATE_FILE_REFERENCE_MODULE

#ifdef __cplusplus
}
#endif

#endif // Py_TRANSLATE_FILE_REFERENCE_MODULE_H
