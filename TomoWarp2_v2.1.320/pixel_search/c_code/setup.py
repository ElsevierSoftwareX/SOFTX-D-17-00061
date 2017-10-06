#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Erika Tudisco, Edward Andò, Stephen Hall, Rémi Cailletaud

# This file is part of TomoWarp2.
# 
# TomoWarp2 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TomoWarp2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with TomoWarp2.  If not, see <http://www.gnu.org/licenses/>.

# ===================================================================
# ===========================  TomoWarp2  ===========================
# ===================================================================

# Authors: Erika Tudisco, Edward Andò, Stephen Hall, Rémi Cailletaud

#!/usr/bin/env python

"""
setup.py file for SWIG pixel_search
"""

from distutils.core import setup, Extension
import numpy

pixel_search_module = Extension('_pixel_search',
                        sources=['pixel_search.i', 'pixel_search.c'],
                        include_dirs = [numpy.get_include(),'.'])

setup (name = 'pixel_search',
        version = '0.1',
        author      = "3sr",
        description = """Simple swig pixel_search""",
        ext_modules = [pixel_search_module],
        py_modules = ["pixel_search"],
        )
