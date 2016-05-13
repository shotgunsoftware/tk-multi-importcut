// Copyright (c) 2015 Shotgun Software Inc.

// CONFIDENTIAL AND PROPRIETARY

// This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
// Source Code License included in this distribution package. See LICENSE.
// By accessing, using, copying or modifying this work you indicate your
// agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
// not expressly granted therein are reserved by Shotgun Software Inc.

#include <Python.h>
#include <Carbon/Carbon.h>
#include <AppKit/NSApplication.h>

BOOL
is_valid_url(NSString *url)
{
    NSUInteger length = [url length];
    // Empty strings should return NO
    if (length > 0) {
        NSError *error = nil;
        NSDataDetector *dataDetector = [NSDataDetector dataDetectorWithTypes:NSTextCheckingTypeLink error:&error];
        if (dataDetector && !error) {
            NSRange range = NSMakeRange(0, length);
            NSRange notFoundRange = (NSRange){NSNotFound, 0};
            NSRange linkRange = [dataDetector rangeOfFirstMatchInString:url options:0 range:range];
            if (!NSEqualRanges(notFoundRange, linkRange) && NSEqualRanges(range, linkRange)) {
                return true;
            }
        } else {
            NSLog(@"Could not create link data detector: %@ %@", [error localizedDescription], [error userInfo]);
        }
    }
    return false;
}

/* register_global_hotkey *****************************************************/
PyObject *
translate_url(PyObject *module, const char *url)
{

    NSURL *url_as_url = NULL;
    NSString *url_as_string = NULL;
    NSString *translated_string = NULL;
    const char *translation;

    PyObject *ret = NULL;

    url_as_string = [NSString stringWithUTF8String: url];
    if (!is_valid_url(url_as_string))
        return PyErr_Format(PyExc_ValueError, "malformed url: '%s'", url);

    // Convert the UTF-8 encoded url into an NSURL
    url_as_url = [NSURL URLWithString: url_as_string];

    // The string could not be turned into a URL
    if (url_as_url == nil)
        return PyErr_Format(PyExc_ValueError, "malformed url: '%s'", url);

    // Get the actual file path
    translated_string = [[url_as_url filePathURL] absoluteString];

    // Convert it into a python string
    translation = [translated_string UTF8String];

    // If there was no answer then return this
    if (translation == NULL)
        Py_RETURN_NONE;

    // We have a translation, return it
    ret = PyString_FromString(translation);
    Py_INCREF(ret);

    // Return the results
    return ret;
}
