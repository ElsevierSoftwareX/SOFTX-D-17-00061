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
Function that calculates "continuum" strain using tetrahedral elements

INPUTs:
- Array of node positions
- Array of displacements
- connectivity matrix
- mask (if an element of mask is set to Nan the nodes is skipped)

OUTPUTS:
- Strain Tensor   (3x3 tensor)
- Rotation matrix (3x3 matrix)
- Connectivity matrix
- Coordinates of the barycentre
"""

# We want to calculate the derivative of the displacements in all directions:
# du                                            dShapeFunction    dShapeFunction    ds                     ds
# --  = Bn * nodalDisplacements      where Bn = -------------- =  -------------- *  --  =  SFderivative *  --
# dx                                                dx                ds            dx                     dx


import numpy
import re, traceback
import logging

from scipy.spatial import Delaunay

from tools.print_variable import pv

def tetrahedral_elements_strain( positions, displacements, connectivity = None, mask = [] ):

  try: logging.log.info("tetrahedral_elements_strain(): Calculating strains using tetrahedral elements")
  except: print "tetrahedral_elements_strain(): Calculating strains using tetrahedral elements"

  positions = positions[:,[2,1,0]]

  #-------------------------------------------------------------------------
  # 4 noded tetraahedral element, linear shape functions
  #-------------------------------------------------------------------------

  ########################################################################
  ##   Derivative of shape function nodal weights from F.E.             ##
  ########################################################################

  SFderivative        = numpy.zeros( ( 3, 4 ) ) # Derivative of shape functions from F.E.
  relNodePos          = numpy.zeros( ( 4, 3 ) ) # RELATIVE Node positions
  nodalDisplacements  = numpy.zeros( ( 4, 3 ) ) # Nodal displacements
  dsdx                = numpy.zeros( ( 3, 3 ) ) #
  dxds                = numpy.zeros( ( 3, 3 ) )
  Bn                  = numpy.zeros( ( 3, 4 ) ) # D/dx with shape function
  I                   = numpy.eye( 3 ) # identity matrix

  weight = 1.0 / 6.0 ;

  # Derivatives of the 4-node shape function wrt X
  SFderivative[0,0]=-1; SFderivative[0,1]=0; SFderivative[0,2]=0; SFderivative[0,3]=1;

  # Derivatives of the 4-node shape function wrt Y
  SFderivative[1,0]=-1; SFderivative[1,1]=0; SFderivative[1,2]=1; SFderivative[1,3]=0;

  # Derivatives of the 4-node shape function wrt Z
  SFderivative[2,0]=-1; SFderivative[2,1]=1; SFderivative[2,2]=0; SFderivative[2,3]=0;

  SFderivative = SFderivative * weight

  if connectivity == None:
    try:
        elements = Delaunay( positions )
    except:
        raise Exception('Warning: Not enough nodes to calculate strain')

    # In the new version of scipy vertices has been replaced by simplices
    try:
      connectivity = elements.vertices
    except :
      #print('vertices not working')
      pass

    try:
      connectivity = elements.simplices
    except:
      #print('simplices not working')
      pass


  [ nElements, nNodes ] = connectivity.shape

  # Define strain matrix
  #  2014-11-12 PB and EA: changing strain 6-component vector to a full 3x3 strain tensor
  strain = numpy.zeros( ( 0, 3, 3 ) )
  rot    = numpy.zeros( ( 0, 3, 3 ) )
  new_connectivity =  numpy.zeros( ( 0, 4 ) ).astype('i')
  coordinates = numpy.zeros( ( 0, 3 ) )

  flat_element = 0

  for elementNumber in reversed( range( nElements ) ):
    
        try:
          if (nElements-elementNumber)%int(nElements/100) == 0:
              print  "\tCompleted cells %2.2f %%\r"%( 100*((nElements-elementNumber))/float(nElements) ),
        except:
          pass

        relNodePos = positions[ connectivity[ elementNumber ] ]
        nodalDisplacements = displacements[ connectivity[ elementNumber ] ]
        
        if numpy.all( numpy.isfinite( nodalDisplacements ) ):
                  
          # Original Comment: /* Calculate dxds = SFderivative*relNodePos and so dsdx=inv(dxds) */
          dxds = numpy.dot( SFderivative, relNodePos )
          try:
            dsdx = numpy.linalg.inv( dxds )

            #-----------------------------------------------------------------------
            #-  Operator which describes weighting of nodal coordinates by shape  --
            #-    function (see Hall et al. 2006)                                 --
            #-----------------------------------------------------------------------
            Bn   = numpy.dot( dsdx, SFderivative )

            # rotation matrix calculation
            rot = numpy.append( rot, [0.5 * ( numpy.dot( Bn, nodalDisplacements) - numpy.dot( nodalDisplacements.T, Bn.T ) )], axis=0  )

            # Original Comment: /* strain=dsdx*SFderivative*nodalDisplacements; */
            dudx = numpy.dot( Bn, nodalDisplacements )
            # Strain Gradient tensor
            F = I + dudx

            # Right Cauchy-Green tensor (as opposed to left)
            C = numpy.dot( F.T, F )

            # Green-Lagrange tensors
            E = 0.5*( C - I )

            # Call our strain "E"
            
            strain = numpy.append( strain, [E], axis=0  )
            
            new_connectivity = numpy.append( new_connectivity, [connectivity[ elementNumber ]], axis=0  )
            ##Coordinates of the barycentre of the element
            coordinates = numpy.append( coordinates, [numpy.mean( relNodePos, 0 )[[2,1,0]]], axis=0  )

          except Exception as exc:
            flat_element += 1
  
  strain[ numpy.where(strain>10) ] = 0

  try: logging.log.info("tetrahedral_elements_strain: strain calculation done.")
  except: print "tetrahedral_elements_strain: strain calculation done."

  return [ strain, rot, new_connectivity, coordinates ]
