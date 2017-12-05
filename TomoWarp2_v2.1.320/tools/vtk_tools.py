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

# ... VTK Tools ...

import numpy
import logging

def WriteVTK_headers( filename, positions, mask = [], DATASET = "UNSTRUCTURED_GRID" ):
  """
  Function to write headers and nodes coordinates to a VTK file
  
  INPUTS:
  - output file name
  - arrays of node positions
  - mask (if an element of mask is set to Nan the nodes is skipped)
  - type of dataset
  
  OUTPUTS:
  - current position of file
  """

  if not isinstance(filename, file):
    fileHandle = open( filename, 'w')
    try: logging.log.info("WriteVTK_headers(): Going to write %s"%(filename))
    except: print "WriteVTK_headers(): Going to write %s"%(filename)
  else:
    fileHandle = filename
    try: logging.log.info("WriteVTK_headers(): Going to write VTK file")
    except: print "WriteVTK_headers(): Going to write VTK file"

  fileHandle.seek(0)

  fileHandle.write('# vtk DataFile Version 3.0\n');
  fileHandle.write('TomoWarp2 D.I.C. results\n');
  fileHandle.write('ASCII\n');

  fileHandle.write('DATASET %s\n'%DATASET);
  
  positions = numpy.delete( positions, numpy.where( ~numpy.isfinite( mask ) ), 0 )

  nPoints = positions.shape[0]
  fileHandle.write('POINTS %i float\n'%nPoints);

  for iPoint in range(nPoints):
    fileHandle.write( '%s\n'%'\t'.join( map( str, positions[iPoint,[2,1,0]] ) ) )

  textPosition = fileHandle.tell()

  if not isinstance(filename, file):
    # close up the file
    fileHandle.close()

  return textPosition

def WriteVTK_maesh( filename, connectivity, position = 0, cell_type = 10):
  """
  Function to write maesh specification to a VTK file
  
  INPUTS:
  - output file name
  - connectivity matrix
  - a specific position where to write in the file
  - type of cell
  """

  if not isinstance(filename, file):
    fileHandle = open( filename, 'r+')
    try: logging.log.info("WriteVTK_maesh(): Going to write %s"%(filename))
    except: print "WriteVTK_maesh(): Going to write %s"%(filename)
  else:
    fileHandle = filename
    try: logging.log.info("WriteVTK_maesh(): Going to write VTK file")
    except: print "WriteVTK_maesh(): Going to write VTK file"

  before = fileHandle.read(position)
  after = fileHandle.read()

  # Goes to desired position
  fileHandle.seek(0)
  fileHandle.write(before)

  [ nCell, nVertex ] = connectivity.shape

  fileHandle.write('CELLS %i %i\n'%( nCell, nVertex*nCell+nCell ) );
  for iCell in range(nCell):
    #For each cell write the connectivity
    fileHandle.write( '%i %s\n'%( nVertex, '\t'.join( map( str, connectivity[iCell,:] ) ) ) )

  fileHandle.write('CELL_TYPES %i\n'%( nCell ) );
  for iCell in range(nCell):
    #For each cell write the cell type
    fileHandle.write( '%i\n'%( cell_type ) )

  #Goes back to original position
  fileHandle.write(after)

  if not isinstance(filename, file):
    # close up the file
    fileHandle.close()


def WriteVTK_data( filename, name, data, mask = [], data_type = '', LOOKUP_TABLE = "default", nPoints = None ):
  """
  Function to write maesh specification to a VTK file
  
  INPUTS:
  - output file name
  - data name
  - data matrix
  - mask (if an element of mask is set to Nan the nodes is skipped)
  - type of data
  - LookUp Table
  - number of data points
  """

  if not isinstance(filename, file):
    fileHandle = open( filename, 'a')
    try: logging.log.info("WriteVTK_maesh(): Going to write %s"%(filename))
    except: print "WriteVTK_maesh(): Going to write %s"%(filename)
  else:
    fileHandle = filename
    try: logging.log.info("WriteVTK_maesh(): Going to write VTK file")
    except: print "WriteVTK_maesh(): Going to write VTK file"

  fileHandle.seek(0,2)

  try:
    data = numpy.delete( data, numpy.where( ~numpy.isfinite( mask ) ), 0 )
  except:
    pass

  # Visit is not able to read vtk files where vectors contain NaNs - replacing with zeros
  data[ numpy.where( numpy.isinf( data ) ) ] = 0
  data[ numpy.where( numpy.isnan( data ) ) ] = 0

  if nPoints == None: nPoints = len( data )
  if data_type != '': fileHandle.write('%s %i\n'%( data_type, nPoints ) );

  try:
    try:
      if data.shape[1] == 3:
          fileHandle.write('VECTORS %s float\n'%name);
          for iPoint in range(nPoints):
              fileHandle.write( '%s\n'%'\t'.join(map(str, data[iPoint,[2,1,0]] ) ) )
      else:
          try: logging.log.warn("WriteVTK_headers(): Errors in data file. I can not write to VTK")
          except: print "WriteVTK_headers(): Errors in data file. I can not write to VTK"
    except:
      if name != '':
        fileHandle.write('SCALARS %s float\n'%name);
        fileHandle.write('LOOKUP_TABLE %s\n'%LOOKUP_TABLE);
        for iPoint in range(nPoints):
          fileHandle.write( '%f\n'%data[iPoint] )
  except IndexError:
    pass

  if not isinstance(filename, file):
    # close up the file
    fileHandle.close()