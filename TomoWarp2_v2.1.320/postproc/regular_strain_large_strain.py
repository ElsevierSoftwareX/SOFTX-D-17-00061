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

# Date created: 2014-11-12

# Authors: Pierre Bésuelle and Edward Andò

"""
New function to calculate "continuum" strain from kinematics in the Large Strain framework

# Useful: http://www.code-aster.org/V2/doc/default/en/man_r/r3/r3.01.01.pdf
# Section "Hexahedrons"
# This code here will use the "HE8" shape function with 8 nodal displacements

INPUTS:
- Array of node positions and displacements

OUTPUTS:
- Strain Tensor   (3x3 tensor)
- Rotation matrix (3x3 matrix)
- Connectivity
- Cell index
"""

# We want to calculate the derivative of the displacements in all directions:
# du                                            dShapeFunction    dShapeFunction    ds                     ds
# --  = Bn * nodalDisplacements      where Bn = -------------- =  -------------- *  --  =  SFderivative *  --
# dx                                                dx                ds            dx                     dx

import numpy, copy
import logging

from tools.calculate_node_spacing import calculate_node_spacing
from tools.print_variable import pv

def regular_strain_large_strain( positions, displacements, calculateConnectivity=False ):

  try: logging.log.info("regular_strain_large_strain: Calculating strains in Large Deformations framework...")
  except: print "regular_strain_large_strain: Calculating strains in Large Deformations framework..."

  SFderivative        = numpy.zeros( ( 3, 8 ) ) # Derivative of shape functions from F.E.
  relNodePos          = numpy.zeros( ( 8, 3 ) ) # RELATIVE Node positions
  nodalDisplacements  = numpy.zeros( ( 8, 3 ) ) # Nodal displacements
  dsdx                = numpy.zeros( ( 3, 3 ) ) #
  dxds                = numpy.zeros( ( 3, 3 ) )
  Bn                  = numpy.zeros( ( 3, 8 ) ) # D/dx with shape function
  I                   = numpy.eye( 3 ) # identity matrix

  # N.B. x is in the real coordiantes of the image
  #      s is in the Shape Function coordinates.


  ########################################################################
  ##   Derivative of shape function nodal weights from F.E.             ##
  ########################################################################
  # Derivatives of the 8-node shape function wrt X
  SFderivative[0,0]=-0.125; SFderivative[0,1]=0.125; SFderivative[0,2]=0.125; SFderivative[0,3]=-0.125; SFderivative[0,4]=-0.125; SFderivative[0,5]=0.125; SFderivative[0,6]=0.125; SFderivative[0,7]=-0.125;

  # Derivatives of the 8-node shape function wrt Y
  SFderivative[1,0]=-0.125; SFderivative[1,1]=-0.125; SFderivative[1,2]=0.125; SFderivative[1,3]=0.125; SFderivative[1,4]=-0.125; SFderivative[1,5]=-0.125; SFderivative[1,6]=0.125; SFderivative[1,7]=0.125;

  # Derivatives of the 8-node shape function wrt Z
  SFderivative[2,0]=-0.125; SFderivative[2,1]=-0.125; SFderivative[2,2]=-0.125; SFderivative[2,3]=-0.125; SFderivative[2,4]=0.125;  SFderivative[2,5]=0.125;  SFderivative[2,6]=0.125;  SFderivative[2,7]=0.125;


  ########################################################################
  ##  Relative nodal positions                                          ##
  ########################################################################
  #-----------------------------------------------------------------------
  #-  Calculate nodal spacing                                           --
  #-      (this comes from regular_prior_interpolator.py)               --
  #-----------------------------------------------------------------------

  number_of_nodes = positions.shape[0]
  connectivity = numpy.zeros((0,8))
  cellIndex = numpy.zeros((0,)).astype( 'i' )

  nodes_z, nodes_y, nodes_x = calculate_node_spacing( positions )
  
  if len(nodes_z)==1:
    
    # To make the strain calculation work in 2D a fictitious second layer of equal displacements is added 
    #   so that the strain in z is null
    positions_fictitious = numpy.copy( positions )
    positions_fictitious[:,0]+=1
    
    positions      = numpy.concatenate( ( positions, positions_fictitious ) )
    displacements  = numpy.concatenate( ( displacements, displacements ) )
    nodes_z = nodes_z + [1]

    nodes_z, nodes_y, nodes_x = calculate_node_spacing( positions )
  
  try:
      # Figure out spacing from first two nodes positions
      z_spacing = nodes_z[1] - nodes_z[0]
      y_spacing = nodes_y[1] - nodes_y[0]
      x_spacing = nodes_x[1] - nodes_x[0]
  except IndexError:
      raise Exception('Warning: Not enough nodes to calculate strain')

  # Define strain matrix
  #  2014-11-12 PB and EA: changing strain 6-component vector to a full 3x3 strain tensor
  #  2016-04-28 ET: strain tensor is filled up to len( nodes_# )-1, changing the declaration to fit this size 
  strain = numpy.zeros( ( len( nodes_z ) - 1, len( nodes_y ) - 1, len( nodes_x ) - 1, 3, 3 ) )
  rot    = numpy.zeros( ( len( nodes_z ) - 1, len( nodes_y ) - 1, len( nodes_x ) - 1, 3, 3 ) )
  volStrain = numpy.zeros( ( len( nodes_z ) - 1, len( nodes_y ) - 1, len( nodes_x ) - 1, 1 ) )


  #-----------------------------------------------------------------------
  #-  Definition of elements                                            --
  #-----------------------------------------------------------------------
  # 2014-11-12 PB and EA: This is the RELATIVE position of the nodes WRT node 1, which is at 0,0,0
  # 2014-11-12 PB and EA: We're going to read in the displacements z-first so we'll put z-spacing first here.
  relNodePos[0,0]=0.0; relNodePos[1,0]=z_spacing; relNodePos[2,0]=z_spacing; relNodePos[3,0]=0.0;       relNodePos[4,0]=0.0;        relNodePos[5,0]=z_spacing;  relNodePos[6,0]=z_spacing; relNodePos[7,0]=0.0;
  relNodePos[0,1]=0.0; relNodePos[1,1]=0.0;       relNodePos[2,1]=y_spacing; relNodePos[3,1]=y_spacing; relNodePos[4,1]=0.0;        relNodePos[5,1]=0.0;        relNodePos[6,1]=y_spacing; relNodePos[7,1]=y_spacing;
  relNodePos[0,2]=0.0; relNodePos[1,2]=0.0;       relNodePos[2,2]=0.0;       relNodePos[3,2]=0.0;       relNodePos[4,2]=x_spacing;  relNodePos[5,2]=x_spacing;  relNodePos[6,2]=x_spacing; relNodePos[7,2]=x_spacing;

  # Original Comment: /* Calculate dxds = SFderivative*relNodePos and so dsdx=inv(dxds) */
  for i in range(3):
    for j in range(3):
      for nodeNumber in range(8):
        # 2014-11-12 PB and EA: loop over each of the 8 nodes, summing the 8 derivatives
        dxds[ i, j ] = dxds[ i, j ] +      SFderivative[ i, nodeNumber ] * relNodePos[ nodeNumber, j ]

  # 2014-11-12 PB and EA: Replaing above commented calculations with a numpy inverse
  dsdx =  numpy.linalg.inv( dxds )

  #-----------------------------------------------------------------------
  #-  Operator which describes weighting of nodal coordinates by shape  --
  #-    function (see Hall et al. 2006)                                 --
  #-----------------------------------------------------------------------
  for ii in range(3):
    for nodeNumber in range(8):
      for kk in range(3):
        Bn[ ii, nodeNumber ] = Bn[ ii, nodeNumber ] + dsdx[ ii, kk ] * SFderivative[ kk, nodeNumber ]


  ########################################################################
  ##  Getting the displacements around each node                        ##
  ########################################################################
  #-----------------------------------------------------------------------
  #-  Reshape the displacements so that we easily have the neighbours   --
  #-----------------------------------------------------------------------
  #displacements_x = displacements[ :, 2 ].reshape( ( len( nodes_z ), len( nodes_y ), len( nodes_x ) ) )
  #displacements_y = displacements[ :, 1 ].reshape( ( len( nodes_z ), len( nodes_y ), len( nodes_x ) ) )
  #displacements_z = displacements[ :, 0 ].reshape( ( len( nodes_z ), len( nodes_y ), len( nodes_x ) ) )

  # This is a 4D array of x, y, z positions + component...
  displacements = displacements.reshape( ( len( nodes_z ), len( nodes_y ), len( nodes_x ), 3 ) )

  #-----------------------------------------------------------------------
  #-  Fetch neighbourhood displacements from x y z displacements        --
  #-    i.e., fill in the nodalDisplacements matrix  numpy.zeros( ( 8, 3 ) )            --
  #-----------------------------------------------------------------------
  for z in range( len(nodes_z) - 1 ):
    print "\tregular_strain_large_strain: Working on z=%04i/%04i\r"%( z, len(nodes_z)-1 ),

    for y in range( len(nodes_y) - 1 ):
      for x in range( len(nodes_x) - 1 ):

        # All the displacements (x,y,z) for the node
        # 2014-11-12 PB and EA: Going to read in the displacements z,y,x even though the rest of the code is nominally x,y,z
        #    so that our resulting strain tensor is the right way around (that is to say z-first)
        nodalDisplacements[ 0, : ] = displacements[ z  , y  , x  , : ]
        nodalDisplacements[ 1, : ] = displacements[ z+1, y  , x  , : ]
        nodalDisplacements[ 2, : ] = displacements[ z+1, y+1, x  , : ]
        nodalDisplacements[ 3, : ] = displacements[ z  , y+1, x  , : ]
        nodalDisplacements[ 4, : ] = displacements[ z  , y  , x+1, : ]
        nodalDisplacements[ 5, : ] = displacements[ z+1, y  , x+1, : ]
        nodalDisplacements[ 6, : ] = displacements[ z+1, y+1, x+1, : ]
        nodalDisplacements[ 7, : ] = displacements[ z  , y+1, x+1, : ]
        
        if numpy.all( numpy.isfinite( nodalDisplacements ) ) == False:
            strain[ z, y, x, :, : ] = numpy.zeros( (3,3) ) * numpy.nan
            rot[ z, y, x, :, : ]    = numpy.zeros( (3,3) ) * numpy.nan
            volStrain[ z, y, x] = numpy.nan

        else:
            # This is our temporary variable for the calculation of the gradient of displacement
            dudx = numpy.zeros( ( 3, 3 ) )

            #-----------------------------------------------------------------------
            #-  Calculate du/dx --  2014-11-12 PB and EA: removing (du/dx).T since we're going for a green-lagrange tensor... see above
            #-----------------------------------------------------------------------
            for i in range(3):
              # OS 17-10-18: in large strains dudx is NOT symmetric
              #for j in range( i, 3 ):  # N.B. this does: i,j = 0,0; 0,1; 0,2; 1,1; 1,2; 2,2
              for j in range(3):
                for nodeNumber in range(8):
                  # Original Comment: /* strain=dsdx*SFderivative*nodalDisplacements; */
                  dudx[i,j] = dudx[i,j] + ( Bn[i,nodeNumber] * nodalDisplacements[nodeNumber,j] )

                  # 2014-10-13 adding rotation matrix calculation
                  rot[   z,y,x,i,j] = rot[   z,y,x,i,j] + \
                                      0.5*(Bn[i,nodeNumber]*nodalDisplacements[nodeNumber,j] - Bn[j,nodeNumber]*nodalDisplacements[nodeNumber,i])

           # OS 17-10-18: in large strains dudx is NOT symmetric
           # # 2014-11-12 PB and EA: completing the diagonal terms of the dudx and rotation tensors
           # dudx[ 1, 0 ] = dudx[ 0, 1 ]
           # dudx[ 2, 0 ] = dudx[ 0, 2 ]
           # dudx[ 2, 1 ] = dudx[ 1, 2 ]

            rot[ z,y,x,1,0 ]    = rot[ z,y,x,0,1]
            rot[ z,y,x,2,0 ]    = rot[ z,y,x,0,2]
            rot[ z,y,x,2,1 ]    = rot[ z,y,x,1,2]

            # Strain Gradient tensor
            F = I + dudx
            #volStraini = numpy.linalg.det( Fi ) - 1

            # Right Cauchy-Green tensor (as opposed to left)
            C = numpy.dot( F.T, F )

            # Green-Lagrange tensors
            E = 0.5*( C - I )

            # Call our strain "E"
            strain[ z, y, x, :, : ] = E
            volStrain[ z, y, x ] = numpy.linalg.det( F ) - 1
            

            # 2017-03-09 EA and JD: If VTK set calculate this -- excluding by default because the .append is crazy slow
            if calculateConnectivity:
                firstCorner = x + y*len(nodes_x) + z*len(nodes_x)*len(nodes_y)
                connectivity = numpy.append( connectivity, [ [ firstCorner,                                          firstCorner+1, 
                                                                firstCorner+len(nodes_x)+1,                           firstCorner+len(nodes_x),
                                                                firstCorner+len(nodes_x)*len(nodes_y),                firstCorner+len(nodes_x)*len(nodes_y)+1, 
                                                                firstCorner+len(nodes_x)*len(nodes_y)+len(nodes_x)+1, firstCorner+len(nodes_x)*len(nodes_y)+len(nodes_x) ] ], axis=0 )
                cellIndex = numpy.append( cellIndex, x + y*(len(nodes_x)-1) + z*(len(nodes_x)-1)*(len(nodes_y)-1) )

  try: logging.log.info("regular_strain_large_strain: strain calculation done.")
  except: print "regular_strain_large_strain: strain calculation done."
                
  return [ strain, rot, connectivity, cellIndex,  volStrain]
