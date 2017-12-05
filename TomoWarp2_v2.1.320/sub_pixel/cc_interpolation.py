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

""" 2014-10-20 Edward Andò

This is an adapted CC-interpolation as taken directly from Steve's su-file based C-code

Removing his while loop which seems to re-perform a pixel search -- we're now assuming that
  we're being given the right position immediately. This effectively removed the need for max_refinement_step

INPUTS:
- im1 which has dimensions of correlation_window
- im2 which has dimensions of correlation_window + 2 in each dimension, and where the highest CC is in the middle
  (this will be checked for in the code)
+ old parameters from Steve's code:
    - refinement_step_threshold
    - max_refinement_iterations

OUTPUTS:
 - subpixel x,y,z displacements
 - interpolated CC
"""

import numpy
import time
import logging

# This is our pixel_search C-code
from pixel_search.c_code import pixel_search
from tools.print_variable import pv

def cc_interpolation_local( im1, im2, refinement_step_threshold = 0.0001, max_refinement_iterations = 15, max_refinement_step = 2):
        # This is a "half wit" correlation window size in z,y,x directions.

        # Check that im2's size is two pixels bigger in each direction than im1
        if not all( numpy.array(im2.shape) - numpy.array(im1.shape) == 2 ):
            try: logging.log.warning( "cc_interpolation_local(): im2's dimensions ({}) are not im1 ({}) +2".format( im2.shape, im1.shape ) )
            except: print  "cc_interpolation_local(): im2's dimensions ({}) are not im1 ({}) +2".format( im2.shape, im1.shape ) 
            return numpy.array( [ 0, 0, 0, 0, 0, 32] )

        # This is the 3x3x3 matrix of CC values which we will interpolate.
        CC = numpy.zeros( ( 3, 3, 3 ) )

        # Fill CC array with the pixel_seach C-code
        for z in range( 3 ):
          for y in range( 3 ):
            for x in range( 3 ):
              # Calculate the CC just for these two identically sized images.
              #2015-12-20 ET: modify to take the correct size in each direction (important only if the CW has different size in the three directions)
              CC[ z, y, x ] = pixel_search.pixel_search( im1, im2[ z:z+im1.shape[0], y:y+im1.shape[1], x:x+im1.shape[2] ], 4 )[ 3 ]

        # Make sure that our hypothesis that the highest CC is in the middle, this might not work if we have two equal maximum points
        # 2014-10-23 EA:
        #  numpy.where( CC == CC.max() ) returns a list of arrays of x, y, z positions, we're going to turn it into an array itself,
        #  this will return x,y,z tuples for each max position
        #  and look for one that is 1,1,1 (after transposing the matrix, in order to have [x1, y1, z1].
        CCmaxPositions = numpy.array( numpy.where( CC == CC.max() ) ).T

        #                                   |  if each component of  | | sum truth values      |
        #                                   |  CCmaxPositions is 1   | | along x,y,z for all() | if ANY max position was at 1,1,1
        if not numpy.all( CCmaxPositions == numpy.array([1,1,1]).all(), axis=1                 ).any():
            try:
              logging.log.warning("cc_interpolation_local(): Maximum of CC is not in the middle of the im2.")
              logging.log.debug("cc_interpolation_local(): numpy.where( CC == CC.max() = {}".format(numpy.where( CC == CC.max() )))
            except:
              print "cc_interpolation_local(): Maximum of CC is not in the middle of the im2."
              print "cc_interpolation_local(): numpy.where( CC == CC.max() = {}".format(numpy.where( CC == CC.max() ))
            return numpy.array( [ 0, 0, 0, 0, 0, 128] )

        ########################################################################
        ##  Interpolate CC in a volume of 27 pixel around the centre          ##
        ##      This has been taken from Stephen Hall's original C -          ##
        ##          tomowarp code (Version: 100211)                           ##
        ########################################################################
        #-----------------------------------------------------------------------
        #-  Calculate cc matrix to be interpolated                            --
        #-    (moving the image_2 around of 1 pixel)                          --
        #-    and check that the maximum CC is in the centre of the window    --
        #-    if not centre volume on new CCmax and repeat until CCmx is at   --
        #-    centre of CC volume or have reached allowed limit of search     --
        #-    refinement                                                      --
        #-----------------------------------------------------------------------


        #-----------------------------------------------------------------------
        #-  Define quadratic coefficients describing CC volume*/              --
        #-----------------------------------------------------------------------

        c1=2*CC[1, 0, 0] - 0.5*CC[2, 0, 0] - 1.5*CC[0, 0, 0];
        c2=0.5*CC[0, 0, 0] - CC[1, 0, 0] + 0.5*CC[2, 0, 0];
        b1=2*CC[0, 1, 0] - 0.5*CC[0, 2, 0] - 1.5*CC[0, 0, 0];
        b2=0.5*CC[0, 0, 0] - CC[0, 1, 0] + 0.5*CC[0, 2, 0];
        d1=2*CC[0, 0, 1] - 0.5*CC[0, 0, 2] - 1.5*CC[0, 0, 0];
        d2=0.5*CC[0, 0, 0] - CC[0, 0, 1] + 0.5*CC[0, 0, 2];

        e1=0.25*(CC[2, 2, 0] - 4*CC[2, 1, 0] - 4*CC[1, 2, 0] + 16*CC[1, 1, 0] - 9*CC[0, 0, 0] - 6*b1 -6*c1);
        e3=-0.25*(CC[2, 2, 0] - 4*CC[2, 1, 0] - 2*CC[1, 2, 0] + 8*CC[1, 1, 0] - 3*CC[0, 0, 0] - 2*b1 +6*c2);
        e2=0.5*(-0.5*CC[2, 2, 0] + 2*CC[1, 2, 0] + CC[2, 1, 0] - 4*CC[1, 1, 0] + 3*CC[0, 0, 0]/2 - 3*b2+ c1);
        e4=CC[1, 1, 0]-CC[0, 0, 0]-b1-b2-c1-c2-e1-e2-e3;

        f1=0.25*(CC[2, 0, 2] - 4*CC[2, 0, 1] - 4*CC[1, 0, 2] + 16*CC[1, 0, 1] - 9*CC[0, 0, 0] - 6*c1 -6*d1);
        f3=-0.25*(CC[2, 0, 2] - 4*CC[2, 0, 1] - 2*CC[1, 0, 2] + 8*CC[1, 0, 1] - 3*CC[0, 0, 0] - 2*d1 +6*c2);
        f2=0.5*(-0.5*CC[2, 0, 2] + 2*CC[1, 0, 2] + CC[2, 0, 1] - 4*CC[1, 0, 1] + 3*CC[0, 0, 0]/2 - 3*d2+ c1);
        f4=CC[1, 0, 1]-CC[0, 0, 0]-c1-c2-d1-d2-f1-f2-f3;

        g1=0.25*(CC[0, 2, 2] - 4*CC[0, 1, 2] - 4*CC[0, 2, 1] + 16*CC[0, 1, 1] - 9*CC[0, 0, 0] - 6*b1 -6*d1);
        g3=-0.25*(CC[0, 2, 2] - 4*CC[0, 2, 1] - 2*CC[0, 1, 2] + 8*CC[0, 1, 1] - 3*CC[0, 0, 0] - 2*d1 +6*b2);
        g2=0.5*(-0.5*CC[0, 2, 2] + 2*CC[0, 1, 2] + CC[0, 2, 1] - 4*CC[0, 1, 1] + 3*CC[0, 0, 0]/2 - 3*d2+ b1);
        g4=CC[0, 1, 1]-CC[0, 0, 0]-b1-b2-d1-d2-g1-g2-g3;

        h1=-(CC[2, 2, 2]-4*(CC[2, 2, 1]+CC[2, 1, 2]+CC[1, 2, 2])+16*(CC[2, 1, 1]+CC[1, 2, 1]+CC[1, 1, 2]) - 64*CC[1, 1, 1] + 27*CC[0, 0, 0] + 18*b1 + 18*c1 + 18*d1 + 12*e1 + 12*f1 + 12*g1)/8;
        h4=(-CC[2, 2, 2] - 32*CC[1, 1, 1] + 8*CC[1, 1, 2] + 4*CC[2, 2, 1] + 21*CC[0, 0, 0] + 18*b1 + 12*b2 + 18*c1 + 12*c2 + 14*d1 + 12*e1 - 24*e4 + 12*f1 + 8*f3 + 12*g1 + 8*g3 + 8*h1)/16;
        k2=(-CC[2, 2, 2] - 32*CC[1, 1, 1] + 8*CC[2, 1, 1] + 4*CC[1, 2, 2] + 21*CC[0, 0, 0] + 18*b1 +12*b2 + 14*c1 + 18*d1 + 12*d2 + 12*e1 + 8*e2 + 12*f1 + 8*f2 + 12*g1 -24*g4 +8*h1)/16;
        k3=(-CC[2, 2, 2] - 32*CC[1, 1, 1] + 8*CC[1, 2, 1] + 4*CC[2, 1, 2] + 21*CC[0, 0, 0] + 14*b1 +18*c1 + 12*c2 + 18*d1 + 12*d2 + 12*e1 + 8*e3 + 12*f1 -24*f4 + 12*g1 + 8*g2 +8*h1)/16;
        k4= -(-CC[2, 2, 2] + 16*CC[1, 1, 1] -15*CC[0, 0, 0] - 14*(b1+c1+d1) -12*(b2+c2+d2)-12*(e1+f1+g1) - 8*(e2+e3+f2+f3+g2+g3) -8*h1 +16*h4 +16*k2 +16*k3)/48;
        k1 = (2*CC[1, 1, 1] -0.25*CC[2, 2, 1] - 7*CC[0, 0, 0]/4 -3*(b1+c1)/2 -b2 -c2 - 7*(d1+d2)/4 - e1 + 2*e4 -3*(f1+f2)/2 -f3 -f4 -3*(g1+g2)/2 -g3 -g4 -h1 +2*h4 +2*k4);
        h3 = (2*CC[1, 1, 1] -0.5*CC[1, 2, 1] - 3*CC[0, 0, 0]/2 -b1 - 3*(c1+c2+d1+d2)/2 - e1 - e3 - 3*(f1+f2+f3+f4)/2 -g1-g2-h1-k1-k3);
        h2 = (2*CC[1, 1, 1] -0.5*CC[2, 1, 1] - 3*CC[0, 0, 0]/2 -c1 - 3*(b1+b2+d1+d2)/2 - e1 - e2 - 3*(g1+g2+g3+g4)/2 -f1-f2-h1-k1-k2);


        #-----------------------------------------------------------------------
        #-  Iteration loop for Newton's method to determine local maximum in  --
        #-    CC volume - at each iteration need to define first and second   --
        #-    derivatives wrt x,y,z and thus the Jacobian which is then       --
        #-    inverted and used to find the vector (dx,dy,dz)                 --
        #-    iterate to max number of iterations or until increments are     --
        #-    less than threshold                                             --
        #-----------------------------------------------------------------------

        # Starting relative position is taken close to the centre
        rel_z_pos=1.1;
        rel_y_pos=1.1;
        rel_x_pos=1.1;

        # Initialisation of steps - set to 1 to be larger then the threshold and enter the loop
        dx=1.0;
        dy=1.0;
        dz=1.0;

        J = numpy.zeros((3, 3))

        threshold = refinement_step_threshold*refinement_step_threshold;
        iteration = 0;

        # A displacement of 2 times max_refinement_step is allowed at this step
        #   (following the gradient the relative position can go out of the volume and then come in again)
        #   later only displacement smaller then max_refinement_step are accepted
        #   (returning and error otherwise)


        while iteration < max_refinement_iterations and \
              not( (dx*dx) < threshold and dy*dy < threshold and dz*dz < threshold ) and \
              abs(rel_z_pos ) <= 2*max_refinement_step and abs(rel_y_pos) <= 2*max_refinement_step and abs(rel_x_pos) <= 2*max_refinement_step:

            iteration = iteration + 1

            # Calculating the first derivative

            dcc_x = c1 + 2*c2*rel_z_pos + e1*rel_y_pos + e2*rel_y_pos*rel_y_pos + 2*e3*rel_z_pos*rel_y_pos + 2*e4*rel_z_pos*rel_y_pos*rel_y_pos + \
                    f1*rel_x_pos + f2*rel_x_pos*rel_x_pos + 2*f3*rel_z_pos*rel_x_pos + 2*f4*rel_z_pos*rel_x_pos*rel_x_pos + h1*rel_y_pos*rel_x_pos + \
                    h2*rel_y_pos*rel_y_pos*rel_x_pos + 2*h3*rel_z_pos*rel_y_pos*rel_x_pos + 2*h4*rel_z_pos*rel_y_pos*rel_y_pos*rel_x_pos + \
                    k1*rel_y_pos*rel_x_pos*rel_x_pos + k2*rel_y_pos*rel_y_pos*rel_x_pos*rel_x_pos + 2*k3*rel_z_pos*rel_y_pos*rel_x_pos*rel_x_pos + \
                    2*k4*rel_z_pos*rel_y_pos*rel_y_pos*rel_x_pos*rel_x_pos;

            dcc_y = b1 + 2*b2*rel_y_pos + e1*rel_z_pos + 2*e2*rel_z_pos*rel_y_pos + e3*rel_z_pos*rel_z_pos + 2*e4*rel_z_pos*rel_z_pos*rel_y_pos + \
                    g1*rel_x_pos + g2*rel_x_pos*rel_x_pos + 2*g3*rel_y_pos*rel_x_pos + 2*g4*rel_y_pos*rel_x_pos*rel_x_pos + h1*rel_z_pos*rel_x_pos + \
                    2*h2*rel_z_pos*rel_y_pos*rel_x_pos + h3*rel_z_pos*rel_z_pos*rel_x_pos + 2*h4*rel_z_pos*rel_z_pos*rel_y_pos*rel_x_pos + \
                    k1*rel_z_pos*rel_x_pos*rel_x_pos + 2*k2*rel_z_pos*rel_y_pos*rel_x_pos*rel_x_pos + k3*rel_z_pos*rel_z_pos*rel_x_pos*rel_x_pos + \
                    2*k4*rel_z_pos*rel_z_pos*rel_y_pos*rel_x_pos*rel_x_pos;

            dcc_z = d1 + 2*d2*rel_x_pos + f1*rel_z_pos + 2*f2*rel_z_pos*rel_x_pos + f3*rel_z_pos*rel_z_pos + 2*f4*rel_z_pos*rel_z_pos*rel_x_pos + \
                    g1*rel_y_pos + 2*g2*rel_y_pos*rel_x_pos + g3*rel_y_pos*rel_y_pos + 2*g4*rel_y_pos*rel_y_pos*rel_x_pos + h1*rel_z_pos*rel_y_pos + \
                    h2*rel_z_pos*rel_y_pos*rel_y_pos + h3*rel_z_pos*rel_z_pos*rel_y_pos + h4*rel_z_pos*rel_z_pos*rel_y_pos*rel_y_pos + \
                    2*k1*rel_z_pos*rel_y_pos*rel_x_pos + 2*k2*rel_z_pos*rel_y_pos*rel_y_pos*rel_x_pos + 2*k3*rel_z_pos*rel_z_pos*rel_y_pos*rel_x_pos + \
                    2*k4*rel_z_pos*rel_z_pos*rel_y_pos*rel_y_pos*rel_x_pos;

            # Calculating the second derivative

            dcc_yy = 2*(b2 + e2*rel_z_pos + e4*rel_z_pos*rel_z_pos + g3*rel_x_pos + g4*rel_x_pos*rel_x_pos + h2*rel_z_pos*rel_x_pos + \
                    h4*rel_z_pos*rel_z_pos*rel_x_pos + k2*rel_z_pos*rel_x_pos*rel_x_pos + k4*rel_z_pos*rel_z_pos*rel_x_pos*rel_x_pos);

            dcc_xx = 2*(c2 + e3*rel_y_pos + e4*rel_y_pos*rel_y_pos + f3*rel_x_pos + f4*rel_x_pos*rel_x_pos + h3*rel_y_pos*rel_x_pos + \
                    h4*rel_y_pos*rel_y_pos*rel_x_pos + k3*rel_y_pos*rel_x_pos*rel_x_pos + k4*rel_y_pos*rel_y_pos*rel_x_pos*rel_x_pos);

            dcc_zz = 2*(d2 + f2*rel_z_pos + f4*rel_z_pos*rel_z_pos + g2*rel_y_pos + g4*rel_y_pos*rel_y_pos + k1*rel_z_pos*rel_y_pos + \
                    k2*rel_z_pos*rel_y_pos*rel_y_pos + k3*rel_z_pos*rel_z_pos*rel_y_pos + k4*rel_z_pos*rel_z_pos*rel_y_pos*rel_y_pos);

            dcc_xy = e1 + 2*e2*rel_y_pos + 2*e3*rel_z_pos + 4*e4*rel_z_pos*rel_y_pos + h1*rel_x_pos + 2*h2*rel_y_pos*rel_x_pos + \
                    2*h3*rel_z_pos*rel_x_pos + 4*h4*rel_z_pos*rel_y_pos*rel_x_pos + k1*rel_x_pos*rel_x_pos + 2*k2*rel_y_pos*rel_x_pos*rel_x_pos + \
                    2*k3*rel_z_pos*rel_x_pos*rel_x_pos + 4*k4*rel_z_pos*rel_y_pos*rel_x_pos*rel_x_pos;

            dcc_xz = f1 + 2*f2*rel_x_pos + 2*f3*rel_z_pos + 4*f4*rel_z_pos*rel_x_pos + h1*rel_y_pos + h2*rel_y_pos*rel_y_pos + \
                    2*h3*rel_z_pos*rel_y_pos + 2*h4*rel_z_pos*rel_y_pos*rel_y_pos + 2*k1*rel_y_pos*rel_x_pos + 2*k2*rel_y_pos*rel_y_pos*rel_x_pos + \
                    4*k3*rel_z_pos*rel_y_pos*rel_x_pos + 4*k4*rel_z_pos*rel_y_pos*rel_y_pos*rel_x_pos;

            dcc_yz = g1 + 2*g2*rel_x_pos + 2*g3*rel_y_pos + 4*g4*rel_y_pos*rel_x_pos + h1*rel_z_pos + 2*h2*rel_z_pos*rel_y_pos + \
                    h3*rel_z_pos*rel_z_pos + 2*h4*rel_z_pos*rel_z_pos*rel_y_pos + 2*k1*rel_z_pos*rel_x_pos + 4*k2*rel_z_pos*rel_y_pos*rel_x_pos + \
                    2*k3*rel_z_pos*rel_z_pos*rel_x_pos + 4*k4*rel_z_pos*rel_z_pos*rel_y_pos*rel_x_pos;

            J[0, 0] = dcc_xx;
            J[1, 1] = dcc_yy;
            J[2, 2] = dcc_zz;
            J[0, 1] = dcc_xy;
            J[1, 0] = dcc_xy;
            J[0, 2] = dcc_xz;
            J[2, 0] = dcc_xz;
            J[1, 2] = dcc_yz;
            J[2, 1] = dcc_yz;

            detJ = J[0, 0]*J[1, 1]*J[2, 2] - J[0, 0]*J[2, 1]*J[1, 2] - J[1, 0]*J[0, 1]*J[2, 2] + \
                  J[1, 0]*J[2, 1]*J[0, 2] + J[2, 0]*J[0, 1]*J[1, 2] - J[2, 0]*J[1, 1]*J[0, 2];

            dx = -((J[1, 1]*J[2, 2]-J[2, 1]*J[1, 2])*dcc_x + (J[0, 2]*J[2, 1]-(J[2, 2]*J[0, 1]))*dcc_y + \
                  (J[0, 1]*J[1, 2]-(J[1, 1]*J[0, 2]))*dcc_z)/detJ;

            dy = -((J[1, 2]*J[2, 0]-J[2, 2]*J[1, 0])*dcc_x + (J[0, 0]*J[2, 2]-(J[2, 0]*J[0, 2]))*dcc_y + \
                  (J[0, 2]*J[1, 0]-(J[1, 0]*J[1, 2]))*dcc_z)/detJ;

            dz = -((J[1, 0]*J[2, 1]-J[2, 0]*J[1, 1])*dcc_x + (J[0, 1]*J[2, 0]-(J[2, 1]*J[0, 0]))*dcc_y + \
                  (J[0, 0]*J[1, 1]-(J[0, 1]*J[1, 0]))*dcc_z)/detJ;

            rel_z_pos = rel_z_pos + dx;
            rel_y_pos = rel_y_pos + dy;
            rel_x_pos = rel_x_pos + dz;


        if ( abs(rel_z_pos) <= max_refinement_step and abs(rel_y_pos) <= max_refinement_step and abs(rel_x_pos) <= max_refinement_step):

            ncc = CC[0, 0, 0] + b1*rel_y_pos + b2*rel_y_pos*rel_y_pos + c1*rel_z_pos + c2*rel_z_pos*rel_z_pos + d1*rel_x_pos + \
                  d2*rel_x_pos*rel_x_pos + e1*rel_z_pos*rel_y_pos + e2*rel_z_pos*rel_y_pos*rel_y_pos + e3*rel_z_pos*rel_z_pos*rel_y_pos + \
                  e4*rel_z_pos*rel_z_pos*rel_y_pos*rel_y_pos + f1*rel_z_pos*rel_x_pos + f2*rel_z_pos*rel_x_pos*rel_x_pos + \
                  f3*rel_z_pos*rel_z_pos*rel_x_pos + f4*rel_z_pos*rel_z_pos*rel_x_pos*rel_x_pos + g1*rel_y_pos*rel_x_pos + \
                  g2*rel_y_pos*rel_x_pos*rel_x_pos + g3*rel_y_pos*rel_y_pos*rel_x_pos + g4*rel_y_pos*rel_y_pos*rel_x_pos*rel_x_pos + \
                  h1*rel_z_pos*rel_y_pos*rel_x_pos + h2*rel_z_pos*rel_y_pos*rel_y_pos*rel_x_pos + h3*rel_z_pos*rel_z_pos*rel_y_pos*rel_x_pos + \
                  h4*rel_z_pos*rel_z_pos*rel_y_pos*rel_y_pos*rel_x_pos + k1*rel_z_pos*rel_y_pos*rel_x_pos*rel_x_pos + \
                  k2*rel_z_pos*rel_y_pos*rel_y_pos*rel_x_pos*rel_x_pos + k3*rel_z_pos*rel_z_pos*rel_y_pos*rel_x_pos*rel_x_pos + \
                  k4*rel_z_pos*rel_z_pos*rel_y_pos*rel_y_pos*rel_x_pos*rel_x_pos;

            return numpy.array( [ rel_z_pos - 1, rel_y_pos - 1, rel_x_pos - 1, ncc, iteration, 0] )

        else:
            return numpy.array( [ rel_z_pos - 1, rel_y_pos - 1, rel_x_pos - 1, 0, iteration, 8 ] )





def cc_interpolation_local_2D( im1, im2,    refinement_step_threshold = 0.0001, max_refinement_iterations = 15, max_refinement_step = 2):
        # This is a "half wit" correlation window size in z,y,x directions.

        # Check that im2's size is two pixels bigger in each direction than im1
        if not ( im2.shape[1] - im1.shape[1] == 2 and im2.shape[2] - im1.shape[2] == 2 ):
            try: logging.log.warning( "cc_interpolation_local_2D(): im2's dimensions ({}) are not im1 ({}) +2".format( im2.shape, im1.shape ) )
            except: print  "cc_interpolation_local_2D(): im2's dimensions ({}) are not im1 ({}) +2".format( im2.shape, im1.shape ) 
            return numpy.array( [ 0, 0, 0, 0, 0, 32] )

        # This is the 3x3x3 matrix of CC values which we will interpolate.
        CC = numpy.zeros( ( 3, 3 ) )
        
        # Fill CC array with the pixel_seach C-code
        for y in range( 3 ):
          for x in range( 3 ):
            # Calculate the CC just for these two identically sized images.
            CC[ y, x ] = pixel_search.pixel_search( im1, im2[ :, y:y+im1.shape[1], x:x+im1.shape[2] ], 4 )[ 3 ]
            
        # Make sure that our hypothesis that the highest CC is in the middle, this might not work if we have two equal maximum points
        # 2014-10-23 EA:
        #  numpy.where( CC == CC.max() ) returns a list of arrays of x, y, z positions, we're going to turn it into an array itself,
        #  this will return x,y,z tuples for each max position
        #  and look for one that is 1,1 (after transposing the matrix, in order to have [x1, y1].
        CCmaxPositions = numpy.array( numpy.where( CC == CC.max() ) ).T
        
        #                                   |  if each component of  | | sum truth values      |
        #                                   |  CCmaxPositions is 1   | | along x,y,z for all() | if ANY max position was at 1,1,1
        if not numpy.all( CCmaxPositions == numpy.array([1,1]).all(), axis=1                 ).any():
            try:
              logging.log.warning("cc_interpolation_local_2D(): Maximum of CC is not in the middle of the im2.")
              logging.log.debug("cc_interpolation_local_2D(): numpy.where( CC == CC.max() = {}".format(numpy.where( CC == CC.max() )))
            except:
              print "cc_interpolation_local_2D(): Maximum of CC is not in the middle of the im2."
              print "cc_interpolation_local_2D(): numpy.where( CC == CC.max() = {}".format(numpy.where( CC == CC.max() ))
            return numpy.array( [ 0, 0, 0, 0, 0, 128] )

        ########################################################################
        ##  Interpolate CC in a surface of 9 pixel around the centre          ##
        ##      This has been taken from Stephen Hall's original C -          ##
        ##          photowarp code                                            ##
        ########################################################################
        #-----------------------------------------------------------------------
        #-  Calculate cc matrix to be interpolated                            --
        #-    (moving the image_2 around of 1 pixel)                          --
        #-    and check that the maximum CC is in the centre of the window    --
        #-    if not centre volume on new CCmax and repeat until CCmx is at   --
        #-    centre of CC volume or have reached allowed limit of search     --
        #-    refinement                                                      --
        #-----------------------------------------------------------------------


        #---------------------------------------------------------------------------------------
        #-  Define quadratic coefficients describing CC volume*/                              --
        #-  cc = a + b1*y + b2*x + c1*y^2 + c2*x^2 + d*y*x + e1*y^2*x + e2*y*x^2 + f* y^2*x^2 --
        #---------------------------------------------------------------------------------------

        b1 = 2.0*CC[1][0] - 0.5*CC[2][0] - 1.5*CC[0][0];
        b2 = 2.0*CC[0][1] - 0.5*CC[0][2] - 1.5*CC[0][0];
        c1 = 0.5*CC[0][0] + 0.5*CC[2][0] - CC[1][0];
        c2 = 0.5*CC[0][0] + 0.5*CC[0][2] - CC[0][1];

        d  = 0.25*( CC[2][2] - 4.0*CC[2][1] - 4.0*CC[1][2] + 16.0*CC[1][1] - 9.0*CC[0][0] - 6.0*b2 - 6.0*b1);
        e1 = 0.25*(-CC[2][2] + 4.0*CC[2][1] + 2.0*CC[1][2] -  8.0*CC[1][1] + 3.0*CC[0][0] + 2.0*b2 - 6.0*c1);
        e2 = 0.25*(-CC[2][2] + 4.0*CC[1][2] + 2.0*CC[2][1] -  8.0*CC[1][1] + 3.0*CC[0][0] + 2.0*b1 - 6.0*c2);
        f  = CC[1][1]-CC[0][0]-b2-c2-b1-c1-d-e2-e1;

        #-----------------------------------------------------------------------
        #-  Iteration loop for Newton's method to determine local maximum in  --
        #-    CC volume - at each iteration need to define first and second   --
        #-    derivatives wrt x,y,z and thus the Jacobian which is then       --
        #-    inverted and used to find the vector (dx,dy,dz)                 --
        #-    iterate to max number of iterations or until increments are     --
        #-    less than threshold                                             --
        #-----------------------------------------------------------------------

        # Starting relative position is taken close to the centre
        rel_y_pos=1.1;
        rel_x_pos=1.1;

        # Initialisation of steps - set to 1 to be larger then the threshold and enter the loop
        dy=1.0;
        dx=1.0;

        J = numpy.zeros((2, 2))

        threshold = refinement_step_threshold*refinement_step_threshold;
        iteration = 0;

        # A displacement of 2 times max_refinement_step is allowed at this step
        #   (following the gradient the relative position can go out of the volume and then come in again)
        #   later only displacement smaller then max_refinement_step are accepted
        #   (returning and error otherwise)

        while iteration < max_refinement_iterations and \
              not ( (dx*dx) < threshold and dy*dy < threshold ) and \
              abs(rel_y_pos) <= 2*max_refinement_step and abs(rel_x_pos) <= 2*max_refinement_step and \
              abs(rel_y_pos) >= -2*max_refinement_step and abs(rel_x_pos) >= -2*max_refinement_step:

            iteration = iteration + 1

            # Calculating the first derivative

            dccy = b1 + 2.0*c1*rel_y_pos + d*rel_x_pos + 2.0*e1*rel_y_pos*rel_x_pos + e2*rel_x_pos*rel_x_pos + 2.0*f*rel_y_pos*rel_x_pos*rel_x_pos;
            dccx = b2 + 2.0*c2*rel_x_pos + d*rel_y_pos + e1*rel_y_pos*rel_y_pos + 2.0*e2*rel_y_pos*rel_x_pos + 2.0*f*rel_y_pos*rel_y_pos*rel_x_pos;
            dccyy = 2.0*c1 + 2.0*e1*rel_x_pos + 2.0*f*rel_x_pos*rel_x_pos;
            dccxx = 2.0*c2 + 2.0*e2*rel_y_pos + 2.0*f*rel_y_pos*rel_y_pos;
            dccyx = d + 2.0*e1*rel_y_pos + 2.0*e2*rel_x_pos + 4.0*f*rel_y_pos*rel_x_pos;

            J[0][0]=dccyy;
            J[1][1]=dccxx;
            J[0][1]=dccyx;
            J[1][0]=dccyx;

            detJ= J[0][0]*J[1][1] - J[1][0]*J[0][1];

            #pv([J,detJ])

            dy=-( J[1][1]*dccy - J[1][0]*dccx)/detJ;
            dx=-(-J[0][1]*dccy + J[0][0]*dccx)/detJ;

            rel_y_pos = rel_y_pos + dy;
            rel_x_pos = rel_x_pos + dx;

            ncc = CC[0][0] + b2*rel_x_pos + c2*rel_x_pos*rel_x_pos + b1*rel_y_pos + c1*rel_y_pos*rel_y_pos + d*rel_x_pos*rel_y_pos + e2*rel_x_pos*rel_x_pos*rel_y_pos + \
            e1*rel_x_pos*rel_y_pos*rel_y_pos + f*rel_x_pos*rel_x_pos*rel_y_pos*rel_y_pos;

        if ( abs(rel_y_pos) <= max_refinement_step and abs(rel_x_pos) <= max_refinement_step):
            return numpy.array( [ 0, rel_y_pos - 1, rel_x_pos - 1, ncc, iteration, 0] )
        else:
            return numpy.array( [ 0, rel_y_pos - 1, rel_x_pos - 1, 0, iteration, 8 ] )