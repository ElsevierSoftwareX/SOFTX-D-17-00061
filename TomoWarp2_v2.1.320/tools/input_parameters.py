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

# Date created: 2013-12-16

# Functions that check the given parameters and ask for image properties

import logging

from input_parameters_setup import input_parameters_setup
from image_finder import image_finder_data
from image_size_and_type import image_size_and_type
from print_variable import pv


def input_parameters( data ):

    data = input_parameters_setup( data )

    data.image_prefix = ["", ""]

    data = image_finder_data( data )
    data = image_size_and_type( data )

    try: logging.log.info("\nInput parameters:")
    except: print "\nInput parameters:"
    for key in sorted( data.iterkeys() ):
      try: logging.log.info( pv([data[key]],'\t',False,key, _print=False) )
      except: print pv([data[key]],'\t',False,key, _print=False) 
    try: logging.log.info('\n')
    except: print '\n'

    return data
