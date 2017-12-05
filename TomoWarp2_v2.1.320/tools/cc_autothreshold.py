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

"""
Automatically calculate the CC threshold based on histogram 
"""

# Date created: 2013-08-20


import numpy
import logging

def cc_autothreshold( cc_field ):
      cc_field = cc_field.astype( numpy.float32 )

      # Finding the minimum CC value which is greater than zero in the CC
      cc_min = cc_field[ numpy.where( cc_field > 0.0 ) ].min()

      # Use this number to build a histogram
      cc_hist, bin_edges = numpy.histogram(cc_field, bins=256, range=(cc_min, 1) )

      # Take only the part of the histogram from cc_min to the max of the histogram.
      cc_hist = cc_hist[ 0:numpy.where( cc_hist == cc_hist.max() )[0][-1]+1 ]

      # Figure out the biggest CC value at which we're below X% of the frequency of the peak of the histogram, this will be our threshold
      # ugly: replace cc_threshold (which if we're here is a string) with a number
      cc_threshold = bin_edges[ numpy.where( cc_hist < 0.015 * cc_hist.max() ) ][-1]
            
      try: logging.log.info( "  Automatic CC threshold calculator: I chose a CC value of: %f"%(cc_threshold) )
      except: print  "  Automatic CC threshold calculator: I chose a CC value of: %f"%(cc_threshold) 

      return cc_threshold