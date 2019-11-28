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
Function to calculate "continuum" strain from kinematics in the Large Strain framework

Useful: http://www.code-aster.org/V2/doc/default/en/man_r/r3/r3.01.01.pdf
Section "Hexahedrons"
This code here will use the "HE8" shape function with 8 nodal displacements

2016-02-24 Pierre Bésuelle and Edward Andò:
  With the objective of facilitating the overlay between strain and microstructure, and in general
  for the strain results to be well-centred on the nodes, we re-write, based on "note_calcul_deformation.pdf"

INPUTS:
- Array of node positions and displacements

OUTPUTS:
- Strain Tensor   (3x3 tensor)
- Rotation matrix (3x3 matrix)
- Connectivity
"""

# We want to calculate the derivative of the displacements in all directions:
# du                                            dShapeFunction    dShapeFunction    ds                     ds
# --  = Bn * nodalDisplacements      where Bn = -------------- =  -------------- *  --  =  SFderivative *  --
# dx                                                dx                ds            dx                     dx



import numpy
import logging

from tools.calculate_node_spacing import calculate_node_spacing


def regular_strain_large_strain_centred( positions, displacements, neighbourhoodDistance, calculateConnectivity=False  ):
  
  pos = positions.copy()
  # neighbourhoodDistance can take positive integer values
  # if =1 we include (2*neighbourhoodDistance+1)^3-1
  numberOfNeighbours = (2*neighbourhoodDistance+1)**3-1

  try: logging.log.info("regular_strain_large_strain_centered(): Calculating strains in Large Deformations framework \
        \n (Geers et al., 1996, Computing strain felds from discrete displacement fields in 2D-solids ) taking neighbours plus or minus {:d}".format(neighbourhoodDistance) )
  except: print "regular_strain_large_strain_centered(): Calculating strains in Large Deformations framework \
        \n (Geers et al., 1996, Computing strain felds from discrete displacement fields in 2D-solids ) taking neighbours plus or minus {:d}".format(neighbourhoodDistance)

  nodalRealtivePositionsRef  = numpy.zeros( ( numberOfNeighbours, 3 ) ) # Delta_X_0 in document
  nodalRealtivePositionsDef  = numpy.zeros( ( numberOfNeighbours, 3 ) ) # Delta_X_t in document
  I                   = numpy.eye( 3 ) # identity matrix
  ########################################################################
  ##  Relative nodal positions                                          ##
  ########################################################################
  #-----------------------------------------------------------------------
  #-  Calculate nodal spacing                                           --
  #-      (this comes from regular_prior_interpolator.py)               --
  #-----------------------------------------------------------------------

  number_of_nodes = positions.shape[0]
  
  connectivity = numpy.zeros((0,1))

  nodes_z, nodes_y, nodes_x = calculate_node_spacing( positions )

  try:
      # Figure out spacing from first two nodes positions
      z_spacing = nodes_z[1] - nodes_z[0]
      y_spacing = nodes_y[1] - nodes_y[0]
      x_spacing = nodes_x[1] - nodes_x[0]
  except IndexError:
      raise Exception('Warning: Not enough nodes to calculate strain')

  ## Define strain matrix
  ##  2014-11-12 PB and EA: changing strain 6-component vector to a full 3x3 strain tensor
  strain = numpy.zeros( ( len( nodes_z ), len( nodes_y ), len( nodes_x ), 3, 3 ) )
  rot    = numpy.zeros( ( len( nodes_z ), len( nodes_y ), len( nodes_x ), 3, 3 ) )
  volStrain = numpy.zeros( ( len( nodes_z ) - 1, len( nodes_y ) - 1, len( nodes_x ) - 1, 1 ) )


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
  positions     = positions.reshape( ( len( nodes_z ), len( nodes_y ), len( nodes_x ), 3 ) )

  #-----------------------------------------------------------------------
  #-  Fetch neighbourhood displacements from x y z displacements        --
  #-    i.e., fill in the nodalDisplacements matrix  numpy.zeros( ( 8, 3 ) )            --
  #-----------------------------------------------------------------------
  for z in range( neighbourhoodDistance, len(nodes_z) - neighbourhoodDistance ):
      print "\tregular_strain_large_strain_centred: Working on z=%04i/%04i\r"%( z, len(nodes_z)-1 ),
      for y in range( neighbourhoodDistance, len(nodes_y) - neighbourhoodDistance ):
          for x in range( neighbourhoodDistance, len(nodes_x) - neighbourhoodDistance ):
              sX0X0 = numpy.zeros( (3,3) )
              sX0Xt = numpy.zeros( (3,3) )
              m0    = numpy.zeros( ( 3 ) )
              mt    = numpy.zeros( ( 3 ) )

              neighbourCount = 0
              centralNodePosition     = positions[ z, y, x, : ]
              centralNodeDisplacement = displacements[ z, y, x, : ]
              for nZ in range( -neighbourhoodDistance,neighbourhoodDistance+1 ):
                  for nY in range( -neighbourhoodDistance,neighbourhoodDistance+1 ):
                      for nX in range( -neighbourhoodDistance,neighbourhoodDistance+1 ):
                          if nZ == 0 and nY == 0 and nX == 0:
                              # we're actually on the node we're studying, skipping this point
                              pass
                          else:
                              # In the reference case this is just the node spacing
                              #                                                 absolute position of this neighbour node
                              #                                                                                         minus abs position of central node
                              nodalRealtivePositionsRef[ neighbourCount, : ] = positions[ z+nZ  , y+nY  , x+nX  , : ] - centralNodePosition


                              #                                                absolute position of this neighbour node
                              #                                                                                         plus displacement of this neighbour node
                              #                                                                                                                                      minus abs position of central node
                              #                                                                                                                                                            minus displacement of central node
                              nodalRealtivePositionsDef[ neighbourCount, : ] = positions[ z+nZ  , y+nY  , x+nX  , : ] + displacements[ z+nZ  , y+nY  , x+nX  , : ] - centralNodePosition - centralNodeDisplacement
                              for u in range(3):
                                  for v in range(3):
                                      sX0X0[u,v] += nodalRealtivePositionsRef[ neighbourCount, u ] * nodalRealtivePositionsRef[ neighbourCount, v ]
                                      sX0Xt[u,v] += nodalRealtivePositionsRef[ neighbourCount, u ] * nodalRealtivePositionsDef[ neighbourCount, v ]

                              m0 += nodalRealtivePositionsRef[ neighbourCount, : ]
                              mt += nodalRealtivePositionsDef[ neighbourCount, : ]
                              neighbourCount += 1
              if numpy.all( numpy.isfinite( nodalRealtivePositionsDef ) ) == False:
                  strain[ z, y, x, :, : ] = numpy.zeros( (3,3) ) * numpy.nan
                  rot[ z, y, x, :, : ]    = numpy.zeros( (3,3) ) * numpy.nan
                  volStrain[ z, y, x] = numpy.nan

              else:
                # multiply the sums sX0X0, sX0Xt by numberOfNeighbours
                sX0X0 = numberOfNeighbours*sX0X0
                sX0Xt = numberOfNeighbours*sX0Xt

                A = sX0X0 - numpy.dot( m0, m0 )
                C = sX0Xt - numpy.dot( m0, mt )

                try:
                    F = numpy.dot( numpy.linalg.inv( A ), C )
                    # Right Cauchy-Green tensor (as opposed to left)
                    rot[ z, y, x, :, : ] = 0.5 * numpy.dot( F.T, -F )

                    # Green-Lagrange tensors
                    E = 0.5*( numpy.dot( F.T, F ) - I )
                    

                    # Call our strain "E"
                    strain[ z, y, x, :, : ] = E
                    volStrain[ z, y, x ] = numpy.linalg.det( F ) - 1
                    #print "\tregular_strain_large_strain_centred: success!!!"
                    
                    # 2017-03-09 EA and JD: If VTK set calculate this -- excluding by default because the .append is crazy slow
                    if calculateConnectivity:
                        #Adding a point cell to connectivity only if strain is non nans
                        connectivity = numpy.append( connectivity, [ [ x+len(nodes_x)*y+len(nodes_x)*len(nodes_y)*z ] ], axis=0 )

                except numpy.linalg.linalg.LinAlgError:
                    print "\tLinAlgError: A", A
                    strain[ z, y, x, :, : ] = numpy.zeros( (3,3) ) * numpy.nan
                    rot[ z, y, x, :, : ]    = numpy.zeros( (3,3) ) * numpy.nan
                    volStrain[ z, y, x ] = numpy.nan


  try: logging.log.info("regular_strain_large_strain_centered(): strain calculation done.")
  except: print "regular_strain_large_strain_centered(): strain calculation done."
  
  return [ strain, rot, connectivity, volStrain]