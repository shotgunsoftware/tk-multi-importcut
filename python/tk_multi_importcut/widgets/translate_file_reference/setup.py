# Copyright (c) 2015 Shotgun Software Inc.
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

from distutils import log
from distutils.errors import DistutilsSetupError
from distutils.core import setup, Extension
from distutils.command.build_clib import build_clib


# need to override build_clib to build a shared library
class build_shared_clib(build_clib):
    def finalize_options(self):
        build_clib.finalize_options(self)

        # override default build_clib to be the build directory
        self.build_clib = None
        self.set_undefined_options('build', ("build_lib", "build_clib"))

    def build_libraries(self, libraries):
        for (lib_name, build_info) in libraries:
            sources = build_info.get('sources')
            if sources is None or not isinstance(sources, (list, tuple)):
                raise DistutilsSetupError, \
                      ("in 'libraries' option (library '%s'), " +
                       "'sources' must be present and must be " +
                       "a list of source filenames") % lib_name
            sources = list(sources)

            log.info("building '%s' library", lib_name)

            # First, compile the source code to object files in the library
            # directory.  (This should probably change to putting object
            # files in a temporary build directory.)
            macros = build_info.get('macros')
            include_dirs = build_info.get('include_dirs')
            objects = self.compiler.compile(sources,
                                            output_dir=self.build_temp,
                                            macros=macros,
                                            include_dirs=include_dirs,
                                            debug=self.debug,
            )

            # Now "link" the object files together into a shared library.
            # Make sure to add in the path for the python library by default
            self.compiler.link_shared_lib(objects, lib_name,
                library_dirs=[os.path.join(sys.exec_prefix, "libs")],
                libraries=build_info.get("libraries", []),
                output_dir=self.build_clib,
                debug=self.debug,
                extra_postargs=["/DELAYLOAD:python27.dll"],
            )

sources = ["translate_file_reference_module.c"]
modules = []
libraries = []
libarary_builds = []

if sys.platform == "darwin":
    os.environ["LDFLAGS"] = "-framework AppKit"
    sources.extend(["translate_file_reference.m"])
elif sys.platform == "win32":
    raise NotImplementedError
elif sys.platform.startswith("linux"):
    raise NotImplementedError

module = Extension("translate_file_reference", sources=sources, libraries=libraries)
modules.append(module)

setup(
    name="translate_file_reference",
    version="1.0",
    description="Module to expose os level functionality.",
    ext_modules=modules,
    libraries=libarary_builds,
    cmdclass={'build_clib': build_shared_clib},
)
