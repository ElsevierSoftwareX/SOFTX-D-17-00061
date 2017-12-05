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

import logging

def WriteTSV( filename, headers, table_of_results ):
  """
  This function will write a TSV file.
  
  INPUTS:
  - Filename or fileHandle
  - Headers of Columns
  - Matrix of values
  """

  # TODO: Check overwrite
  if not isinstance(filename, file):
    fileHandle = open( filename, 'w')
    try: logging.log.info("WriteTSV(): Going to write %s"%(filename))
    except: print "WriteTSV(): Going to write %s"%(filename)
  else:
    fileHandle = filename
    try: logging.log.info("WriteTSV(): Going to write TSV file")
    except: print "WriteTSV(): Going to write TSV file"

  number_of_headers = len( headers )

  fileHandle.seek(0)

  # Write a first line with headers, separated by tabs:
  for header_number in range( number_of_headers ):
    header = headers[ header_number ]

    # Write a \n on the last field, tabs otherwise
    if header_number is (number_of_headers - 1):
      fileHandle.write("%s\n"%header.lstrip())
    else:
      fileHandle.write("%s\t"%header)

  # write the table
  for row in table_of_results[:]:
    for item_number in range( number_of_headers ):
      if number_of_headers == 1:
          item = row
      else:
          item = row[item_number]

      if item_number is (number_of_headers - 1):
        fileHandle.write('{:f}\n'.format(item))
      else:
        fileHandle.write('{:f}\t'.format(item))

  if not isinstance(filename, file):
    # close up the file
    fileHandle.close()

  try: logging.log.info("WriteTSV(): Done!")
  except: print "WriteTSV(): Done!"




def ReadTSV( filename, index, list_of_desired_stats, start_stop ):
  """
  This function reads a TSV of values.
  General idea:
  1. Read first line's columns headers
  2. Read last line's grain label
  3. go through file putting into matrix

  2013-08-22 Starting to add possibility of reading a header before the beginning of the matrix...
  2013-08-23 Adding important assumption that the first line in the header 
  
  INPUTS:
  - Filename of fileHandle
  - The column header of the Label ( "index" for Visilog 6.7 and 6.8 ) # See below for a change
  - List of column headers we want to match and record.
  - Tuple with start and stop labels
  
  OUTPUTS:
  - Matrix of result - with labels as indexes of the matrix
  
  """

  import string
  import numpy

  # Number of stats including the index
  number_of_stats = 1 + len( list_of_desired_stats )

  # separate start_stop tuple into two different variables
  start = start_stop[0]; 
  stop = start_stop[1]

  # read a text file as a list of lines
  if not isinstance(filename, file):
    try:
      fileHandle = open ( filename,"r" )
    except IOError as e:
      raise Exception('TVS file does not exist')
    try: logging.log.info("ReadTSV(): Processing %s"%(filename))
    except: print "ReadTSV(): Processing %s"%(filename)
  else:
    fileHandle = filename
    try: logging.log.info("ReadTSV(): Processing TSV file ")
    except: print "ReadTSV(): Processing TSV file "

  lineList = fileHandle.readlines()

  if not isinstance(filename, file):
    # close up the file
    fileHandle.close()

  # copy first and last lines into variables
  firstline = string.split(  lineList[ 0], "\t")
  lastline  = string.split(  lineList[-1], "\t")

  # Define a 2x(1+number of stats) matrix to hold the column value of
  # the stats in the first one, and the truth value of whether the stat name
  # has been found on the first line in the second one
  stats_positions = numpy.zeros(  [ number_of_stats, 1], dtype=int )
  stats_found     = numpy.zeros(  [ number_of_stats, 1], dtype=bool )

  # Look through first line, matching column headers, the "index" first:
  for item_count in range(len(firstline)):
    # Assign item - right strip it, to catch spaces and (much more importantly) newlines
    item = string.rstrip( firstline[item_count] )
    # If we match our index
    if item == index:
      stats_positions[0] = item_count
      stats_found[0]     = True
      break

  # Should have got the index, now look through first line, matching the remaining desired fields:
  # For each of the stats specified as third output
  for stat_count in range( number_of_stats-1 ):
    stat = list_of_desired_stats[ stat_count ]

    for item_count in range(len(firstline)):
      # Assign item - right strip it, to catch spaces and (much more importantly) newlines
      item = string.rstrip( firstline[item_count] )
      # If we match our index
      if item == stat:
        stats_positions[ stat_count+1 ] = item_count
        stats_found[ stat_count+1 ]     = True
        break

  # Check we mached everything we wanted:
  for item_count in range( number_of_stats ):
    item = stats_found[ item_count ]
    # If we did not match something... at least complain
    if item == False:
      if item_count == 0:
        raise  Exception("ReadTSV: Did not match: %s EXITING"%(index))
      else:
        try: logging.log.warn("ReadTSV: Did not match \" %s \""%(list_of_desired_stats[ item_count - 1 ])) 
        except: print "ReadTSV: Did not match \" %s \""%(list_of_desired_stats[ item_count - 1 ])
        #NOTE: Consider removing this column from the matrix. Maybe not, otherwise we'll make it less wide, no good


  #--------------------------------------------------------------------
  # At this stage we have looked at the first line, found the positions of the data we want, these are stored in stats_positions
  #--------------------------------------------------------------------
  # making stats_positions a numpy array
  stats_positions = numpy.array( numpy.ravel( stats_positions ) )

  # For the last line, go and get the value of index - this should be the biggest value, and use this to preallocate the matrix
  # to store our results
  # If the lastline does not contain a number as index the previous line is considered
  while True:
    try:
      last_label = int( float( lastline[ stats_positions[ 0 ] ] ) )
      break
    except ValueError:
      try: logging.log.warn("ReadTSV(): skipping a line at the end of the file") 
      except: print "ReadTSV(): skipping a line at the end of the file"
      del lineList[-1]
      lastline  = string.split(  lineList[-1], "\t")
    except:
      raise Exception("ReadTSV(): Could not read TSV file")

  # Now if we've been asked to stop at a certain label, and it is smaller than the biggest label, detect this,
  # and modify the value of the last label
  if (stop < last_label) and (stop != 0): last_label = stop

  # pre-allocate matrix of labels and their statistics:
  results_matrix = numpy.zeros( [ last_label+1, number_of_stats ] )

  # For each line in file
  for line_number in range( start, len( lineList ) ):
    # Split up current line
    line = string.split(  lineList[ line_number ], "\t")

    # extract label
    try:
      label = int( float( line[ stats_positions[ 0 ] ] ) )
      
      # if we hit the largest label, quit
      if label > last_label: break

      # fore each valid stat, copy it in!
      for stat_count in range( number_of_stats ):
        if stats_found[ stat_count ]:
            results_matrix[ label, stat_count ] = line[ stats_positions[ stat_count ] ]
            
    except ValueError:
      try: logging.log.warn("ReadTSV(): skipping line %i: %s"%(line_number,line)) 
      except: print "ReadTSV(): skipping line %i: %s"%(line_number,line)

  try: logging.log.info( "ReadTSV(): Done! (size ={0})".format(results_matrix.shape) )
  except: print "ReadTSV(): Done! (size ={0})".format(results_matrix.shape)

  return results_matrix
