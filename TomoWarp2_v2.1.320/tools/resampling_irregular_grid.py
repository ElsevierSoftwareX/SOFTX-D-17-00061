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

# Functions that resamples data on irregular grid

import numpy
from scipy.interpolate import griddata

def resampling_irregular_grid( data, positions, new_spacing=None, interpolationMethod='linear'):

    zmin = min( positions[:,0] )
    zmax = max( positions[:,0] )
    ymin = min( positions[:,1] )
    ymax = max( positions[:,1] )
    xmin = min( positions[:,2] )
    xmax = max( positions[:,2] )

    if new_spacing == None:
                                #cubic root of total_pixels/number_of_points to get average original spacing
                                #total pixels in the volume          number of original points         resampling to half of the original spacing
        new_spacing = round( ( (xmax-xmin)*(ymax-ymin)*(zmax-zmin) / positions.shape[0] )**(1.0/3.0) / 2)

    # Determine the new position of a regular grid in the 3 directions
    newZ = numpy.arange(zmin, zmax+new_spacing, new_spacing)
    newY = numpy.arange(ymin, ymax+new_spacing, new_spacing)
    newX = numpy.arange(xmin, xmax+new_spacing, new_spacing)

    # Determine the position for each node
    xx, yy, zz = numpy.broadcast_arrays(newZ[:,None,None], newY[None,:,None], newX[None,None,:])
    newPositions= numpy.array( [ zz.ravel(), yy.ravel(), xx.ravel() ] ).T

    # Interpolating original data on refgular grid
    newData = griddata( positions, data, newPositions, method=interpolationMethod )
    newData = newData.reshape( ( len(newZ), len(newY), len(newX) ) )

    return newData