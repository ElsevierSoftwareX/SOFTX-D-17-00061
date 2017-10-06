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

# Date created: 2014-07-25

"""
Correct the displacement for changing in pixel size between the two images

INPUT:
- kinematics matrix
- pixel_size_ratio (pixel_size_image2/pixel_size_image1)
- centre of the image (z,y,x position) where the changing in pixel size does not produce apparent displacement

OUTPUT: 
- kinematics matrix
"""

def correct_pixel_size_changing( kinematics, pixel_size_ratio, image_centre ):

  for i in [ 1, 2, 3 ]:
    kinematics[ :, i+3 ] = kinematics[ :, i+3 ] + ( ( kinematics[ :, i ] - image_centre[ i-1 ] + kinematics[ :, i+3 ] ) / pixel_size_ratio ) * ( pixel_size_ratio - 1 )
    
  return kinematics
