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

# Date created: 2015-01-29

"""
This function will be called to do sub-pixel correlation on a pair of images.

  This is taking a lot of code from Edward Andò's PhD work, see:
@phdthesis{ando2013-phd,
   author    = "E. Andò",
   title     = "Experimental investigation of micro-structural changes in deforming granular media using x-ray tomography",
   year      = "2013",
   school    = "Université de Grenoble",
}

INPUTS:
- Two subvolumes -- second one should be +- 1 pixel in each direction in size.
  im1 will stay still and im2 will be translated +- 1 pixel using an optimisation approach.
- translation initial guess ( z,y,x )
- INTERPOLATION describing the type of interpolation to use (nearest neighbour, tri-linear, tri-cubic)

OUTPUTS:
 1. list with subpixel displacements and NCC
"""

import numpy

# Why this function and not the pixel_search in C?
from tools.calculate_cc import calculate_ncc
#from tools.pytricubic import tricubic

import scipy
import scipy.optimize
import scipy.ndimage

# HACK -- this should be passed parameter.
#interpolationMode = "pytricubic"
interpolationMode = "map_coordinates"


# Is this really usefull?
global I
I = 0

def normalise( vector ):
    norm = numpy.linalg.norm( vector )
    if norm > 0:
      return vector / norm
    else:
      return numpy.array( [0,0,0] )


def axis_and_angle_to_rotation_matrix_3d( rot_ax, rot_ang_rad ):
    # 2012.03.02 - generates a 3x3 rotation matrix
    # from http://rip94550.wordpress.com/2008/05/20/axis-and-angle-of-rotation/
    
    # don't bother with too small angles, will just create huge noise
    if rot_ang_rad < 0.0001:
      return numpy.eye(3)

    # copy out components of axis of rotation
    a = rot_ax[0];  b = rot_ax[1]; c = rot_ax[2]

    # positive angle is clockwise
    N = numpy.array( [  [  0,  c, -b ],\
                        [ -c,  0,  a ],\
                        [  b, -a,  0 ] ] ) * -1

    # NOTE the numpy.dot is very important.
    R = numpy.eye(3) + ( numpy.sin( rot_ang_rad ) * N )   +   ( ( 1 - numpy.cos( rot_ang_rad) ) * numpy.dot( N,N ) )

    return R



def translation_rotation_to_ncc( x0, im1, im2, coordinates, coordinatesMiddle, interpolationMode, interpolationOrder):
    ## 2012.02.29 - big function which takes an interpolated reference image,
    ##   a deformed image volume, a translation and a rotation (defines as 3 angles).
    ##
    ## Plan: 1. generate rotation matrix
    ##       2. transform coodinate system
    ##       3. look up interploated image with new coordinate system
    ##       4. calculate ncc between ref_deformed and def

    newCoordinates = coordinates.copy()

    if len( x0 ) == 2:
        Rot = False
        # add back in the third, false, z dimension
        x0 = numpy.array( [ 0, x0[0], x0[1] ] )
        dimension = 2
    if len( x0 ) == 3:
        # In the future, for rotation in 2D this will also be three components, so we'll have to pass a dimensionality, or a more general description of the deformation to apply
        Rot = False
        dimension = 3
    elif len( x0 ) == 6:
        Rot = True
        dimension = 3

    displacementVector = numpy.array( x0[0:3] )

    if Rot:
        rotationVector     = numpy.array( x0[3:6] )

        ## its length is the rotation angle
        rotationAngle  = numpy.sqrt( numpy.vdot( rotationVector, rotationVector ) )

        ## its direction is the rotation axis.
        rotationAxis   = normalise( rotationVector )

        ## Rotate each point
        newCoordinates = numpy.dot(  axis_and_angle_to_rotation_matrix_3d( rotationAxis, rotationAngle ), coordinates )

    ## Move origin back + displacement.
    newCoordinates[0,:] += coordinatesMiddle[0] + displacementVector[0]
    newCoordinates[1,:] += coordinatesMiddle[1] + displacementVector[1]
    newCoordinates[2,:] += coordinatesMiddle[2] + displacementVector[2]


    if interpolationMode == "pytricubic":
        im2deformed = numpy.zeros_like( im1 )
        # The code, for the moment, runs only on a list -- so we'll be passed the interpolator directly,
        #   to avoid re-constructing it at each function call
        for n, coord in enumerate( ( newCoordinates ).T.tolist() ):
            # This will be very slow
            im2deformed[n] = im2.ip( coord  )

    if interpolationMode == "map_coordinates":
        if dimension == 2:
            im2deformed = scipy.ndimage.map_coordinates( im2[0], newCoordinates[1:3], order=interpolationOrder, prefilter=False )
        else:
            im2deformed = scipy.ndimage.map_coordinates( im2, newCoordinates, order=interpolationOrder, prefilter=False )

    global I

    # Calculate NCC
    oneMinusNCC = 1 - calculate_ncc(  im1, im2deformed )

    I+=1
    return oneMinusNCC



def image_interpolation_translation_rotation( im1, im2, initialGuess=None, cornerOffset=numpy.nan, interpolationMode="map_coordinates", interpolationOrder=3, optimisationMode="Powell" ):
      # === Step 1: Measure the dimensions of image 1 ===
      im1Dim = numpy.array( im1.shape )
      im2Dim = numpy.array( im2.shape )

      if len( initialGuess ) == 3:
          Rot = False
          if im1Dim[0] == 1 and im2Dim[0] == 1:
              boundaryLimits  = ( ( -1, 1 ), ( -1, 1 ) )
              # drop the Z guess if we're in 2D
              initialGuess    = initialGuess[1:3]
          else:
              boundaryLimits  = ( ( -1, 1 ), ( -1, 1 ), ( -1, 1 ) )
      else:
          boundaryLimits = ( ( -1, 1 ), ( -1, 1 ), ( -1, 1 ), ( -numpy.pi, numpy.pi ), ( -numpy.pi, numpy.pi ), ( -numpy.pi, numpy.pi ) )

      # 2015-12-17 EA: case condition for 2D
      if not ( im1Dim[0] == 1 and im2Dim[0] == 1 and ( im2Dim[1] - im1Dim[1] ) == 2*cornerOffset and ( im2Dim[2] - im1Dim[2] ) == 2*cornerOffset ) and not all( ( im2Dim - im1Dim ) == 2*cornerOffset ):
          loging.log.warning("image_interpolation_translation_rotation(): (im2Dim - im1Dim) should be 2*cornerOffset but it is {}".format((im2Dim - im1Dim)))
          if Rot:
              return [ [ 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 ], 0.0, numpy.NaN, 32 ]
          else:
              return [ [ 0.0, 0.0, 0.0 ], 0.0, numpy.NaN, 32 ]

      # === Step 2: Generate the list of coordinates for im1 ===
      # This commented block should make you a "coordinates" array given the size of the image.
      coordinatesInitial = numpy.zeros( ( 3, im1Dim[0] *  im1Dim[1] *  im1Dim[2] ), dtype='<f4' )

      # Build an initial coordinates array aligned with im1, which means
      #   a) of dimensions of im1
      #   b) starting from the corner offset
      coordinates_mgrid = numpy.mgrid[  cornerOffset:im1Dim[0]+cornerOffset,\
                                        cornerOffset:im1Dim[1]+cornerOffset,\
                                        cornerOffset:im1Dim[2]+cornerOffset ]

      # In order to facilitate rotation calculation, put the origin in the middle of the volume
      # 1. calculate the offset:
      coordinatesMiddle = numpy.floor( im1Dim / 2.0 ) + cornerOffset

      # 2. subtract from coordinates (it will be added back in the function above)
      coordinatesInitial[0,:] =  coordinates_mgrid[0].flat - coordinatesMiddle[0]
      coordinatesInitial[1,:] =  coordinates_mgrid[1].flat - coordinatesMiddle[1]
      coordinatesInitial[2,:] =  coordinates_mgrid[2].flat - coordinatesMiddle[2]

      del coordinates_mgrid

      if interpolationMode == "pytricubic":
          # float is required for passage to C++ boost libs
          im2 = tricubic.tricubic( list(im2.astype('float')), list(im2Dim) )

      if optimisationMode in [ "Nelder-Mead", "Powell", "CG", "BFGS", "Newton-CG", "L-BFGS-B", "TNC", "COBYLA", "SLSQP", "dogleg", "trust-ncg" ]:
          if optimisationMode == 'BFGS':
              myOptions = {'maxiter': 256, 'disp': False, 'eps': 0.25 }
          elif optimisationMode == 'Powell':
              #myOptions = {'maxiter': 256, 'disp': True, 'xtol': 0.001, 'ftol': 0.00005  }
              myOptions = {'maxiter': 256, 'disp': False }
          else:
              myOptions = {'maxiter': 256, 'disp': False }
          returns = scipy.optimize.minimize(  translation_rotation_to_ncc,    \
                                              initialGuess,                   \
                                              args    = ( im1.flat, im2, coordinatesInitial, coordinatesMiddle, interpolationMode, interpolationOrder ),\
                                              method  = optimisationMode,     \
                                              bounds  = boundaryLimits,       \
                                              tol     = 0.0001,               \
                                              options = myOptions  )
          #         xN            1-CC     number Iter  error
          #                                                 TODO detect error and report...

          try:
              if im1Dim[0] == 1 and im2Dim[0] == 1:
                  return [ [ 0, returns.x[0], returns.x[1]], 1 - returns.fun, returns.nit, 0 ]
              else:
                  return [                        returns.x, 1 - returns.fun, returns.nit, 0 ]

          except AttributeError:
              if im1Dim[0] == 1 and im2Dim[0] == 1:
                  return [ [ 0, returns.x[0], returns.x[1]], 1 - returns.fun, None, 0 ]
              else:
                  return [                        returns.x, 1 - returns.fun, None, 0 ]

      elif optimisationMode == "subPixelSearch":
          subPixelSearchRange = numpy.arange( -1,1.1,0.1 )
          ccMatrix = numpy.zeros( ( len(subPixelSearchRange), len(subPixelSearchRange), len(subPixelSearchRange) ) )
          for nz, dz in enumerate( subPixelSearchRange ) :
            for ny, dy in enumerate( subPixelSearchRange ) :
              for nx, dx in enumerate( subPixelSearchRange ) :
                ccMatrix[ nz, ny, nx ] = translation_rotation_to_ncc( [ dz, dy, dx ], im1.flat, im2, coordinatesInitial, coordinatesMiddle, interpolationMode, interpolationOrder)

          cc = 1 - ccMatrix.min()
          z  = subPixelSearchRange[ numpy.where( ccMatrix == ccMatrix.min() )[0] ][0]
          y  = subPixelSearchRange[ numpy.where( ccMatrix == ccMatrix.min() )[1] ][0]
          x  = subPixelSearchRange[ numpy.where( ccMatrix == ccMatrix.min() )[2] ][0]
          loging.log.debug( "image_interpolation_translation_rotation: subPixelSearch: Min CC: {}".format(cc))
          loging.log.debug( "image_interpolation_translation_rotation: subPixelSearch: Min CC location: {} {} {}".format(x, y, z) ) 

          return [ [ z, y, x,0,0,0 ], cc, len(subPixelSearchRange)**3, 0 ]

      else:
          try: logging.log.error("image_interpolation_translation_rotation: optimisation mode \"{}\" unknown".format( optimisationMode ) )
          except: print "image_interpolation_translation_rotation: optimisation mode \"{}\" unknown".format( optimisationMode ) 
          if Rot:
            return [ [ 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 ], 0.0, 0.0, 999 ]
          else:
            return [ [ 0.0, 0.0, 0.0 ], 0.0, 0.0, 999 ]
