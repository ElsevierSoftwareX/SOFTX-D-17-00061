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
This function calculates strains, from regularly spaced node kinematics
This has been taken from Stephen Hall's original C - tomowarp code (Version: 271109)

See 2006 paper Hall et al. Geophysics paper for notation.

N.B. This is in SMALL STRAINS !!!

2014-10-13 EA: Adding Rotation Matrix Calculation from displacments, by taking the
  antisymteric part of the strain tensor. Taken from Matias Silva's changes to this same code.

2014-11-12 PA and EA: This is deprecated -- regular_strain_large_def.py and regular_strain_small_def.py now exist,
  which return a whole z-first tensor

INPUTs:
 1. Array of node positions and displacements

OUTPUTS:
OUTPUTS:
 1. Strain Tensor   (3x3 tensor)
 2. Rotation matrix (3x3 matrix)
"""

import numpy

import sys
from tools.calculate_node_spacing import calculate_node_spacing

def regular_strain( positions, displacements ):

  # s is local coordinates
  print "  -> Calculating strain...",

  dNds  = numpy.zeros( ( 3, 8 ) ) # Shape function derivative?!
  xn    = numpy.zeros( ( 8, 3 ) ) # RELATIVE Node positions
  un    = numpy.zeros( ( 8, 3 ) ) # Nodal displacements
  dsdx  = numpy.zeros( ( 3, 3 ) ) #
  dxds  = numpy.zeros( ( 3, 3 ) )
  Bn    = numpy.zeros( ( 3, 8 ) ) # D/dx with shape function


  ########################################################################
  ##  Derivative of shape function nodal weights                        ##
  ########################################################################
  dNds[0,0]=-0.125; dNds[0,1]=0.125; dNds[0,2]=0.125; dNds[0,3]=-0.125;
  dNds[0,4]=-0.125; dNds[0,5]=0.125; dNds[0,6]=0.125; dNds[0,7]=-0.125;

  dNds[1,0]=-0.125; dNds[1,1]=-0.125; dNds[1,2]=0.125; dNds[1,3]=0.125;
  dNds[1,4]=-0.125; dNds[1,5]=-0.125; dNds[1,6]=0.125; dNds[1,7]=0.125;

  dNds[2,0]=-0.125; dNds[2,1]=-0.125; dNds[2,2]=-0.125; dNds[2,3]=-0.125;
  dNds[2,4]=0.125;  dNds[2,5]=0.125;  dNds[2,6]=0.125;  dNds[2,7]=0.125;


  ########################################################################
  ##  Relative nodal positions                                          ##
  ########################################################################
  #-----------------------------------------------------------------------
  #-  Calculate nodal spacing                                           --
  #-      (this comes from regular_prior_interpolator.py)               --
  #-----------------------------------------------------------------------

  number_of_nodes = positions.shape[0]

  nodes_z, nodes_y, nodes_x = calculate_node_spacing( positions )

  # Figure out spacing from first two nodes positions
  z_spacing = nodes_z[1] - nodes_z[0]
  y_spacing = nodes_y[1] - nodes_y[0]
  x_spacing = nodes_x[1] - nodes_x[0]

  # If the node spacing is not the same in every direction, we're not sure that this
  #   can work.
  if z_spacing != y_spacing or z_spacing != x_spacing:
    print "regular_strain(): the spacing is different, and I'm not sure I can handle this. Stopping."
    sys.exit()

  # Define strain matrix
  strain = numpy.zeros( ( len( nodes_z ), len( nodes_y ), len( nodes_x ), 6 ) )
  rot    = numpy.zeros( ( len( nodes_z ), len( nodes_y ), len( nodes_x ), 6 ) )


  #-----------------------------------------------------------------------
  #-  Definition of elements                                            --
  #-----------------------------------------------------------------------
  # TODO: Defining all these zeros is useless since we have initialised these arrays with zeros.
  xn[0,0]=0.0; xn[1,0]=z_spacing; xn[2,0]=z_spacing; xn[3,0]=0.0;
  xn[4,0]=0.0; xn[5,0]=z_spacing; xn[6,0]=z_spacing; xn[7,0]=0.0;

  xn[0,1]=0.0; xn[1,1]=0.0; xn[2,1]=y_spacing; xn[3,1]=y_spacing;
  xn[4,1]=0.0; xn[5,1]=0.0; xn[6,1]=y_spacing; xn[7,1]=y_spacing;

  xn[0,2]=0.0; xn[1,2]=0.0; xn[2,2]=0.0; xn[3,2]=0.0;
  xn[4,2]=x_spacing; xn[5,2]=x_spacing;
  xn[6,2]=x_spacing; xn[7,2]=x_spacing;

  # Original Comment: /* Calculate dxds=dNds*xn and so dsdx=inv(dxds) */
  for ii in range(3):
    for jj in range(3):
      for kk in range(8):
        dxds[ii,jj] = dxds[ii,jj] + dNds[ii,kk] * xn[kk,jj]

  detdxds = dxds[0,0]*dxds[1,1]*dxds[2,2] - dxds[0,0]*dxds[1,2]*dxds[2,1] - \
            dxds[0,1]*dxds[1,0]*dxds[2,2] + dxds[0,1]*dxds[1,2]*dxds[2,0] + \
            dxds[0,2]*dxds[1,0]*dxds[2,1] - dxds[0,2]*dxds[1,1]*dxds[2,0];

  dsdx[0,0] = (dxds[1,1]*dxds[2,2]-dxds[2,1]*dxds[1,2])/detdxds;
  dsdx[0,1] = (dxds[0,2]*dxds[2,1]-dxds[2,2]*dxds[0,1])/detdxds;
  dsdx[0,2] = (dxds[0,1]*dxds[1,2]-dxds[1,1]*dxds[0,2])/detdxds;
  dsdx[1,0] = (dxds[1,2]*dxds[2,0]-dxds[2,2]*dxds[1,0])/detdxds;
  dsdx[1,1] = (dxds[0,0]*dxds[2,2]-dxds[2,0]*dxds[0,2])/detdxds;
  dsdx[1,2] = (dxds[0,2]*dxds[1,0]-dxds[1,2]*dxds[0,0])/detdxds;
  dsdx[2,0] = (dxds[1,0]*dxds[2,1]-dxds[2,0]*dxds[1,1])/detdxds;
  dsdx[2,1] = (dxds[0,1]*dxds[2,0]-dxds[2,1]*dxds[0,0])/detdxds;
  dsdx[2,2] = (dxds[0,0]*dxds[1,1]-dxds[1,0]*dxds[0,1])/detdxds;

  #-----------------------------------------------------------------------
  #-  Operator which describes weighting of nodal coordinates by shape  --
  #-    function (see Hall et al. 2006)                                 --
  #-----------------------------------------------------------------------
  for ii in range(3):
    for jj in range(8):
      for kk in range(3):
        Bn[ii,jj] = Bn[ii,jj] + dsdx[ii,kk]*dNds[kk,jj]


  ########################################################################
  ##  Getting the displacements around each node                        ##
  ########################################################################
  #-----------------------------------------------------------------------
  #-  Reshape the displacements so that we easily have the neighbours   --
  #-----------------------------------------------------------------------
  displacements_z = displacements[ :, 0 ].reshape( ( len( nodes_z ), len( nodes_y ), len( nodes_x ) ) )
  displacements_y = displacements[ :, 1 ].reshape( ( len( nodes_z ), len( nodes_y ), len( nodes_x ) ) )
  displacements_x = displacements[ :, 2 ].reshape( ( len( nodes_z ), len( nodes_y ), len( nodes_x ) ) )

  # This is a 4D array of x, y, z positions + component...
  displacements = displacements.reshape( ( len( nodes_z ), len( nodes_y ), len( nodes_x ), 3 ) )


  #-----------------------------------------------------------------------
  #-  Fetch neighbourhood displacements from x y z displacements        --
  #-    i.e., fill in the un matrix  numpy.zeros( ( 8, 3 ) )            --
  #-----------------------------------------------------------------------
  for z in range( len(nodes_z) - 1 ):
    for y in range( len(nodes_y) - 1 ):
      for x in range( len(nodes_x) - 1 ):

        # All the displacements (z,y,x) for the node
        un[ 0, : ] = displacements[ z  ,y  ,x  , : ]
        un[ 1, : ] = displacements[ z+1,y  ,x  , : ]
        un[ 2, : ] = displacements[ z+1,y+1,x  , : ]
        un[ 3, : ] = displacements[ z  ,y+1,x  , : ]
        un[ 4, : ] = displacements[ z  ,y  ,x+1, : ]
        un[ 5, : ] = displacements[ z+1,y  ,x+1, : ]
        un[ 6, : ] = displacements[ z+1,y+1,x+1, : ]
        un[ 7, : ] = displacements[ z  ,y+1,x+1, : ]

        #-----------------------------------------------------------------------
        #-  Calculate Strain                                                  --
        #-----------------------------------------------------------------------
        d = 0
        for ii in range(3):
          for jj in range( ii,3 ):  # N.B. j from ii to 3 !!!
            for kk in range(8):
              # Original Comment: /* strain=dsdx*dNds*un; */
              strain[z,y,x,d] = strain[z,y,x,d] + 0.5*(Bn[ii,kk]*un[kk,jj]+Bn[jj,kk]*un[kk,ii])
              # 2014-10-13 adding rotation matrix calculation
              rot[   z,y,x,d] = rot[   z,y,x,d] + 0.5*(Bn[ii,kk]*un[kk,jj]-Bn[jj,kk]*un[kk,ii])

            # 2014-02-11: corrected indentation level of this d+1
            d += 1

        # Filter too-large strains...
        for d in range( 6 ):
          if strain[z,y,x,d]*strain[z,y,x,d]> .5*.5:
             strain[z,y,x,d] = 0.0
             # 2014-10-13 Also filtering rot matrix
             rot[   z,y,x,d] = 0.0

  print "done."
  return [ strain, rot ]

