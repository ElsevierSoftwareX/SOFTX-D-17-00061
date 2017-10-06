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

# Date created: 2013-08-20

# ... Calculate NCC between two images of the same size...


import numpy


def calculate_ncc( image1, image2 ):
      ##make sure eveything is in arrays:
      image1 = numpy.asarray( image1 )
      image2 = numpy.asarray( image2 )
      
      im1Sum = (image1**2).sum()
      im2Sum = (image2**2).sum()
      
      ncc = (    ( image1 * image2 ).sum()   /      numpy.sqrt( im1Sum * im2Sum  )   ).astype('<f8')

      return ncc
