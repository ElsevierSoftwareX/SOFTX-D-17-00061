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

"""
This function is responsible for interpolating the prior guesses between two different regularly spaced grids

INPUTs:
- Prior array with guesses (old)
- Prior array without guesses (new node spacing)
- Smoothing filter size (a median filter is applied before interpolation if set >0)

OUTPUTS:
- Interpolated new prior array
"""

import numpy
from scipy import ndimage
from scipy.interpolate import griddata
import logging

from tools.calculate_node_spacing import calculate_node_spacing
from tools.kinematic_filters import median_filter_nans
from tools.print_variable import pv

def regular_prior_interpolator( old_prior, new_prior, filter_size=None ):

  old_nodes_z, old_nodes_y, old_nodes_x = calculate_node_spacing( old_prior[ :, 1:4 ] )

  # Figure out spacing from first two nodes positions
  if len(old_nodes_z)==1:
      old_z_spacing=1
  else:
      old_z_spacing = old_nodes_z[1] - old_nodes_z[0]
  old_y_spacing = old_nodes_y[1] - old_nodes_y[0]
  old_x_spacing = old_nodes_x[1] - old_nodes_x[0]
  try: logging.log.info("regular_prior_interpolator: Prior node spacing (z,y,x) is:\t{:.0f} {:.0f} {:.0f}".format( old_z_spacing, old_y_spacing, old_x_spacing ))
  except: print "regular_prior_interpolator: Prior node spacing (z,y,x) is:\t{:.0f} {:.0f} {:.0f}".format( old_z_spacing, old_y_spacing, old_x_spacing )

  # Reshape prior field to a three dimensional arrays
  z_field = old_prior[ :, 4 ].reshape( ( len(old_nodes_z), len(old_nodes_y), len(old_nodes_x) ) )
  y_field = old_prior[ :, 5 ].reshape( ( len(old_nodes_z), len(old_nodes_y), len(old_nodes_x) ) )
  x_field = old_prior[ :, 6 ].reshape( ( len(old_nodes_z), len(old_nodes_y), len(old_nodes_x) ) )
  z_rot   = old_prior[ :, 7 ].reshape( ( len(old_nodes_z), len(old_nodes_y), len(old_nodes_x) ) )
  y_rot   = old_prior[ :, 8 ].reshape( ( len(old_nodes_z), len(old_nodes_y), len(old_nodes_x) ) )
  x_rot   = old_prior[ :, 9 ].reshape( ( len(old_nodes_z), len(old_nodes_y), len(old_nodes_x) ) )
  
  #Replacing the Inf in the prior with the median of finte values around (in None replace with zero)
  inf_positions = numpy.where( numpy.isinf( x_field ) )
  
  for inf_number in range( len( inf_positions[0] ) ):
      z = inf_positions[0][inf_number]
      y = inf_positions[1][inf_number]
      x = inf_positions[2][inf_number]
      
      try:
        z_field[z,y,x] = numpy.media( z_field[ where( numpy.isfinite( z_filed[ z-1:z+2, y-1:y+2, z-1:x+2 ] ) ) ] )
        y_field[z,y,x] = numpy.media( y_field[ where( numpy.isfinite( y_filed[ z-1:z+2, y-1:y+2, z-1:x+2 ] ) ) ] )
        x_field[z,y,x] = numpy.media( x_field[ where( numpy.isfinite( x_filed[ z-1:z+2, y-1:y+2, z-1:x+2 ] ) ) ] )
      except:
        pass
  
  z_field[ numpy.where( numpy.isinf( z_field ) ) ] = 0
  y_field[ numpy.where( numpy.isinf( y_field ) ) ] = 0
  x_field[ numpy.where( numpy.isinf( x_field ) ) ] = 0

  if filter_size is not None and filter_size > 0:
      try: logging.log.info("regular_prior_interpolator: Smoothing kinematics field")
      except: print "regular_prior_interpolator: Smoothing kinematics field"
      # 2014-07-18 -- Edward Ando
      # Changing the median filter for the field from scipy.ndimage.filters.median_filter
      #   (which seems to propagate NaNs) to our own, home-developed median filter:
      z_field = median_filter_nans( numpy.squeeze(z_field),  filter_size ).reshape( ( len(old_nodes_z), len(old_nodes_y), len(old_nodes_x) ) )
      y_field = median_filter_nans( numpy.squeeze(y_field),  filter_size ).reshape( ( len(old_nodes_z), len(old_nodes_y), len(old_nodes_x) ) )
      x_field = median_filter_nans( numpy.squeeze(x_field),  filter_size ).reshape( ( len(old_nodes_z), len(old_nodes_y), len(old_nodes_x) ) )
      z_rot   = median_filter_nans( numpy.squeeze(z_rot)   , filter_size ).reshape( ( len(old_nodes_z), len(old_nodes_y), len(old_nodes_x) ) )
      y_rot   = median_filter_nans( numpy.squeeze(y_rot)   , filter_size ).reshape( ( len(old_nodes_z), len(old_nodes_y), len(old_nodes_x) ) )
      x_rot   = median_filter_nans( numpy.squeeze(x_rot)   , filter_size ).reshape( ( len(old_nodes_z), len(old_nodes_y), len(old_nodes_x) ) )

  # Normalise coordinates of new prior nodes positions
  #   (subtract position of old top corner and divide by old node spacing), to get into the SHAPE => SIZE
  #   of the old prior for interpolation.
  new_prior_normalised = numpy.zeros( (new_prior.shape[0], 3) )
  new_prior_normalised[ :, 0 ] = ( new_prior[ :, 1 ] - old_nodes_z[0] ) / old_z_spacing
  new_prior_normalised[ :, 1 ] = ( new_prior[ :, 2 ] - old_nodes_y[0] ) / old_y_spacing
  new_prior_normalised[ :, 2 ] = ( new_prior[ :, 3 ] - old_nodes_x[0] ) / old_x_spacing

  # Interpolate each prior field for each new node
  # 2014-07-23 Edward Andò:
  #   map_coordinates does not handle NaNs, and cannot handle masked arrays for the moment,
  #   ...so we will seek and destroy the NaNs in the displacement fields before doing a map_coordinates
  # This means for each NaN position, we will grow a window until we get a real value,
  #   and then we'll use that window do make a median to fill in our NaN measurement.

  # Figure out NaN positions... (they will be in the same place for every field)
  nan_positions = numpy.where( numpy.isnan( x_field ) )

  # A mask of ones and zeros in order to quickly work out the smallest window size for the filter
  mask          = numpy.ones( ( len(old_nodes_z), len(old_nodes_y), len(old_nodes_x) ), dtype = 'bool' )
  mask[nan_positions] = False

  number_of_nans = len( nan_positions[0] )

  if number_of_nans > 0:
      try: logging.log.warn("regular_prior_interpolator(): {:.0f} NaNs detected, replacing them with a median value of the smallest window that touches real data".format( number_of_nans ))
      except: print "regular_prior_interpolator(): {:.0f} NaNs detected, replacing them with a median value of the smallest window that touches real data".format( number_of_nans )

  for nan_number in range( number_of_nans ):
      z = nan_positions[0][nan_number]
      y = nan_positions[1][nan_number]
      x = nan_positions[2][nan_number]

      z_top = z
      y_top = y
      x_top = x

      z_bot = z
      y_bot = y
      x_bot = x

      window_sum = 0
      step  = 0


      while window_sum == 0:
            step += 1
            #print "step = ", step
            if z_top >= 0: z_top -= step
            if y_top >= 0: y_top -= step
            if x_top >= 0: x_top -= step

            if z_bot <= len(old_nodes_z): z_bot += step
            if y_bot <= len(old_nodes_y): y_bot += step
            if x_bot <= len(old_nodes_x): x_bot += step

            window_sum = numpy.sum(   mask[ z_top:z_bot+1,\
                                            y_top:y_bot+1,\
                                            x_top:x_bot+1   ] )

            local_mask = numpy.where( mask[ z_top:z_bot+1,\
                                            y_top:y_bot+1,\
                                            x_top:x_bot+1   ] )

      z_field[ z, y, x ] = numpy.median( z_field[ z_top:z_bot+1,\
                                                  y_top:y_bot+1,\
                                                  x_top:x_bot+1   ][local_mask] )
      y_field[ z, y, x ] = numpy.median( y_field[ z_top:z_bot+1,\
                                                  y_top:y_bot+1,\
                                                  x_top:x_bot+1   ][local_mask] )
      x_field[ z, y, x ] = numpy.median( x_field[ z_top:z_bot+1,\
                                                  y_top:y_bot+1,\
                                                  x_top:x_bot+1   ][local_mask] )

      z_rot[ z, y, x ] = numpy.median( z_rot[ z_top:z_bot+1,\
                                                  y_top:y_bot+1,\
                                                  x_top:x_bot+1   ][local_mask] )
      y_rot[ z, y, x ] = numpy.median( y_rot[ z_top:z_bot+1,\
                                                  y_top:y_bot+1,\
                                                  x_top:x_bot+1   ][local_mask] )
      x_rot[ z, y, x ] = numpy.median( x_rot[ z_top:z_bot+1,\
                                                  y_top:y_bot+1,\
                                                  x_top:x_bot+1   ][local_mask] )

  new_z_field = ndimage.map_coordinates( z_field, new_prior_normalised.T, order=1, mode='nearest', prefilter=False ).T
  new_y_field = ndimage.map_coordinates( y_field, new_prior_normalised.T, order=1, mode='nearest' ).T
  new_x_field = ndimage.map_coordinates( x_field, new_prior_normalised.T, order=1, mode='nearest' ).T
  
  new_z_rot   = ndimage.map_coordinates( z_rot,   new_prior_normalised.T, order=1, mode='nearest', prefilter=False ).T
  new_y_rot   = ndimage.map_coordinates( y_rot,   new_prior_normalised.T, order=1, mode='nearest' ).T
  new_x_rot   = ndimage.map_coordinates( x_rot,   new_prior_normalised.T, order=1, mode='nearest' ).T

  # Update and return new prior guesses array
  new_prior[ :, 4 ] = new_z_field
  new_prior[ :, 5 ] = new_y_field
  new_prior[ :, 6 ] = new_x_field
  new_prior[ :, 7 ] = new_z_rot
  new_prior[ :, 8 ] = new_y_rot
  new_prior[ :, 9 ] = new_x_rot

  return new_prior
