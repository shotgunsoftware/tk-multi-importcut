// Copyright (c) 2015 Shotgun Software Inc.

// CONFIDENTIAL AND PROPRIETARY

// This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
// Source Code License included in this distribution package. See LICENSE.
// By accessing, using, copying or modifying this work you indicate your
// agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
// not expressly granted therein are reserved by Shotgun Software Inc.

#include <Python.h>

#define TRANSLATE_FILE_REFERENCE_MODULE
#include "translate_file_reference_module.h"

/*******************************************************************************
 * @file translate_file_reference_module.c
 * @brief Python bindings for translating file references
 ******************************************************************************/

const char docstring[] =
"Translate urls to file paths\n" \
"\n" \
"translate_file_reference.translate_url(url)\n" \
"  Translate the given URL to a filesystem path.";

static PyObject *module;

/* translate_file_reference_translate_url *****************************************************/
static PyObject *
translate_file_reference_translate_url(PyObject *self, PyObject *args)
{
    int results;
    PyObject *translation;

    // Required arguments
    const char *url;

    // Parse arguments
    results = PyArg_ParseTuple(args, "s", &url);
    if (!results)
        return NULL;

    // Call the implementation
    translation = translate_url(module, url);

    return translation;
}

/* module *********************************************************************/
static PyMethodDef translate_file_reference_methods[] = {
    /* {name, meth, flags, doc} */
    {"translate_url", (PyCFunction)translate_file_reference_translate_url, METH_VARARGS, "Translate a url"},
    {NULL}
};

#ifndef PyMODINIT_FUNC
#define PyMODINIT_FUNC void
#endif

PyMODINIT_FUNC
inittranslate_file_reference(void)
{
    PyObject *docs;
    PyObject *c_api_object;
    static Py_TRANSLATE_FILE_REFERENCE_CAPI Py_translate_file_reference_api;

    // Initialize the module
    module = Py_InitModule3("translate_file_reference", translate_file_reference_methods, "Translate file paths");
    if (module == NULL)
        return;

    // Create the c object for the C API
    c_api_object = PyCObject_FromVoidPtrAndDesc((void *)&Py_translate_file_reference_api, "translate_file_reference.translate_file_reference_CAPI", NULL);
    if (c_api_object != NULL)
        PyModule_AddObject(module, "translate_file_reference_CAPI", c_api_object);

    // Add docstring
    docs = PyString_FromString(docstring);
    Py_INCREF(docs);
    PyModule_AddObject(module, "__doc__", docs);
}
