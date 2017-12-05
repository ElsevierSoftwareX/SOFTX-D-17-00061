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

# Date created: 2014-03-11

"""
This function filters a regularly spaced node grid

INPUTs:
- Array of node positions 
- Array of node displacements
- Filter parameters

OUTPUTS:
- filtered displacement fields
"""

import numpy, sys, scipy
import logging

from tools.calculate_node_spacing import calculate_node_spacing
from tools.print_variable import pv

def median_filter(  ):
  print "  -> median_filter: This function is deprecated, please look in:"
  print "     prior_field/prior_median_filter.py"
  

def median_filter_finite( in_matrix ):
  
  median = numpy.median( in_matrix[ numpy.isfinite( in_matrix ) ] )
  
  return median


def median_filter_nans( in_matrix, filter_size ):

  # Following the discussion on http://stackoverflow.com/questions/10683596/efficiently-calculating-boundary-adapted-neighbourhood-average
  #                     ...and  http://stackoverflow.com/questions/5480694/numpy-calculate-averages-with-nans-removed
  #   ...but we are not going to use a mask, just the properties of numpy.median.
  # Defining a simple, median filter which operates on a nd-matrix,
  #   This is done with "scipy.ndimage.generic_filter", with the operation numpy.median
  #   ...since this operation is not sensitive to NaNs, then we won't spread them around the matrix.
  # -> This doesn't work for numpy.mean, or .sum...
  # -> scipy.ndimage.filters.median_filter spreads NaNs more than this solution.

  # Input:
  #   - nd-matrix (possibly with NaNs, but not necessarily masked)
  #   - scipy.ndimage compatible size
  # Output: filtered array.
  
  # Could consider making a circular mask/kernel,
  #   and passing it as footprint= instead of size=
  #return scipy.ndimage.generic_filter( in_matrix, numpy.median, size=filter_size, mode='constant', cval=0.0 )
  #return scipy.ndimage.generic_filter( in_matrix, numpy.median, size=filter_size )
  
  return scipy.ndimage.generic_filter( in_matrix, median_filter_finite, size=filter_size )

  return out_matrix




def kinematics_median_filter_fnc( positions, displacements, filter_size ):
  # 2014-07-23 Eddy (on holiday in Greece...)
  # The median filter above seems both unnecessarily complicated and
  #   not general enough to deserve to name median_filter.
  # => Renaming it kinematics_median_filter.
  
  number_of_nodes = positions.shape[0]
  number_of_displacements = displacements.shape[1]

  if positions.shape[1] != 3:
      try: logging.info.warn("kinematics_median_filter_fnc(): Not given three positions. Stopping.")
      except: print "kinematics_median_filter_fnc(): Not given three positions. Stopping."
      return -1

  if number_of_nodes != displacements.shape[0]:
      try: logging.info.warn("kinematics_median_filter_fnc(): Not given the same amout of positions and displacements. Stopping.")
      except: print "kinematics_median_filter_fnc(): Not given the same amout of positions and displacements. Stopping."
      return -1

  nodes_z, nodes_y, nodes_x = calculate_node_spacing( positions )
   

  try:
      # Figure out spacing from first two nodes positions
      y_spacing = nodes_y[1] - nodes_y[0]
      x_spacing = nodes_x[1] - nodes_x[0]
      if len(nodes_z) == 1:
        #we are working with 2D images
        z_spacing = y_spacing
      else:
        z_spacing = nodes_z[1] - nodes_z[0]
  except IndexError:
      try: logging.info.warn("kinematics_median_filter_fnc(): Not enough nodes to calculate median filter")
      except: print "kinematics_median_filter_fnc(): Not enough nodes to calculate median filter"
      return -1

  # If the node spacing is not the same in every direction, we're not sure that this
  #   can work.
  if z_spacing != y_spacing or z_spacing != x_spacing:
      try: logging.info.warn("kinematics_median_filter_fnc(): The spacing is different, and I'm not sure I can handle this. Stopping.")
      except: "kinematics_median_filter_fnc(): The spacing is different, and I'm not sure I can handle this. Stopping."
      return -1

  # Define output matrix
  result = numpy.zeros( ( number_of_nodes, number_of_displacements ) )

  #-----------------------------------------------------------------------
  #-  Reshape the displacements so that we easily have the neighbours   --
  #-----------------------------------------------------------------------
  # This is a 4D array of z, y, x positions + component...
  displacements = numpy.array( displacements.reshape( ( len( nodes_z ), len( nodes_y ), len( nodes_x ), number_of_displacements ) ) )

  for i in range( number_of_displacements ):
    result[ :, i ] = median_filter_nans( numpy.squeeze(displacements[ :, :, :, i ]), filter_size ).reshape( ( number_of_nodes ) )

  return result


def remove_outliers(  in_matrix, filter_size, mask=None ):
    
    out_matrix = in_matrix.copy()
    if mask is None: mask = numpy.ones_like(in_matrix)
    
    mask_ccordinates = numpy.where(mask==1)
    
    for i_outlier in range( mask_ccordinates[0].shape[0] ):
        
        z = mask_ccordinates[0][i_outlier]
        y = mask_ccordinates[1][i_outlier]
        x = mask_ccordinates[2][i_outlier]
        
        out_matrix[z,y,x] = median_filter_finite( in_matrix[ max(z-filter_size,0):min(z+filter_size,in_matrix.shape[0])+1, \
                                            max(y-filter_size,0):min(y+filter_size,in_matrix.shape[1])+1, \
                                            max(x-filter_size,0):min(x+filter_size,in_matrix.shape[2])+1 ] )
        
    return out_matrix

def spot_outliers(  in_matrix, filter_size, threshold, absolut_threshold=False, filter_high=True ):
    
    mask = numpy.zeros_like(in_matrix)
    check_sign = 1 if filter_high else -1
    
    for z in range(in_matrix.shape[0]):
        for y in range(in_matrix.shape[1]):
            for x in range(in_matrix.shape[2]):
        
              if numpy.isnan( in_matrix[z,y,x] ):
                    mask[z,y,x] = 1
              elif numpy.isfinite( in_matrix[z,y,x] ):
                 
                if absolut_threshold:
                    if in_matrix[z,y,x]*check_sign > threshold*check_sign:
                        mask[z,y,x] = 1
                else:
                    median = median_filter_finite( in_matrix[ max(z-filter_size,0):min(z+filter_size,in_matrix.shape[0])+1, \
                                                    max(y-filter_size,0):min(y+filter_size,in_matrix.shape[1])+1, \
                                                    max(x-filter_size,0):min(x+filter_size,in_matrix.shape[2])+1 ] )
                    if (in_matrix[z,y,x]-median)*check_sign > threshold:
                        mask[z,y,x] = 1
                        
    return mask


def kinematics_remove_outliers( positions, displacements, filter_size, threshold=2, absolut_threshold=False, filter_high=True, filter_base_field=0 ):

  number_of_nodes = positions.shape[0]
  number_of_displacements = displacements.shape[1]

  if positions.shape[1] != 3:
      try: logging.info.warn("kinematics_remove_outliers(): Not given three positions. Stopping.")
      except: print "kinematics_remove_outliers(): Not given three positions. Stopping."
      return -1

  if number_of_nodes != displacements.shape[0]:
      try: logging.info.warn("kinematics_remove_outliers(): Not given the same amout of positions and displacements. Stopping.")
      except: print "kinematics_remove_outliers(): Not given the same amout of positions and displacements. Stopping."
      return -1

  nodes_z, nodes_y, nodes_x = calculate_node_spacing( positions )
   
  # Initialize output matrix
  result = numpy.zeros( ( number_of_nodes, number_of_displacements ) )

  #-----------------------------------------------------------------------
  #-  Reshape the displacements so that we easily have the neighbours   --
  #-----------------------------------------------------------------------
  # This is a 4D array of z, y, x positions + component...
  displacements = numpy.array( displacements.reshape( ( len( nodes_z ), len( nodes_y ), len( nodes_x ), number_of_displacements ) ) )
  
  mask = spot_outliers(  displacements[ :, :, :, filter_base_field ], filter_size, threshold, absolut_threshold, filter_high )

  for i in range( number_of_displacements ):
    result[ :, i ] = remove_outliers(  displacements[ :, :, :, i ], filter_size, mask ).reshape( ( number_of_nodes ) )

  return result, mask.reshape( ( number_of_nodes ) )
