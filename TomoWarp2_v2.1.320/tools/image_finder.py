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

# Date created: 2015-01-27

"""
Functions that list the images into the input directory and recover the prefix
of the file name, the digits for the number, first and last file number and extension

INPUT:
- input directory
- filter for filename
- extension
- number of digits

OUTPUT:
- filename prefix
- digits
- slices_extent = [firstNumber, lastNumber]
- extension

image_finder_data uptdate the "data" structure
"""

import os, re, string
import logging

from print_variable import pv

def image_finder( directory="./", nameFilter="", extension="", digits=None ):

    # Get a sorted list of files in the folder that match the name filter and the extension, if given.
    filePattern = re.compile( r"(.*)%s(.*)%s"%( nameFilter, extension ) )
    fileList = sorted( [f for f in os.listdir( directory ) if filePattern.match(f)] )

    if fileList == []: raise Exception("\timage_finder(): No matching files found in %s"%(directory))

    # Extract the basename of the first file and split it into filename and extension
    [ firstFileName, extension ] = os.path.splitext( os.path.basename(fileList[0]) )

    # If Digits is not defined, iterate from the back of the filename until we no longer find any digits, and use this to build up our prefix and digits field.
    if digits == None:
        # Define a "firstFileNameEnd" which is the part of the fileName AFTER the nameFilter
        #   and BEFORE the extension. This allows us to put some numbers into the nameFilter
        #   in the case that there are no splitters between prefix and file numbers, e.g. tomo-2015012700001.tif
        #   so that nameFilter = "tomo-20150127"
        if nameFilter == "":
          firstFileNameEnd = firstFileName
        else:
          firstFileNameEnd = string.split(firstFileName,nameFilter)[-1]

        # Iterate from the end of the line until we run out of digits
        i = len(firstFileNameEnd)
        while i>0 and firstFileNameEnd[i-1].isdigit(): i-=1
        digits = len(firstFileNameEnd) - i


    if digits == 0:
        # Then we guess we must be in the case where the whole volume is just in one file -- this is probably the case
        #   for correlating two 2D images too.
        prefix = firstFileName

        # setting this to None, so that the case of digits == 0 can be detected out of this function (in input_parameters.py)
        slices_extent = None
        try:
          logging.log.info( "**********************image_finder():***************************" )
          logging.log.info( "In the directory: %s"%(directory)                                 )
          logging.log.info( "I am working on a single file: %s%s "%(prefix, extension)         )
          logging.log.info( "****************************************************************" )
        except:
          print "**********************image_finder():***************************" 
          print "In the directory: %s"%(directory)                                 
          print "I am working on a single file: %s%s "%(prefix, extension)         
          print "****************************************************************" 

    else:
        # otherwise we're in the regular case of having a certain number of digits -- in this case continue
        #   and try to figure out first and last numbers...
        prefix = firstFileName[0:-digits]
        try:
          firstNumber = int(firstFileName[-digits::])
        except ValueError:
          raise Exception('I can not read the digits in the filename. Please check number of digits of filename format')

        # Get a sorted list of files in the folder that match the name prefix, number of digits and the extension.
        filePattern = re.compile( r"%s\d{%i}%s"%( prefix, digits, extension ) )
        fileList = sorted( [f for f in os.listdir( directory ) if filePattern.match(f)] )

        [ lastFileName, extension ] = os.path.splitext( os.path.basename(fileList[-1]) )
        lastNumber = int(lastFileName[-digits::])

        try:
          logging.log.info( "**********************image_finder():***************************" )
          logging.log.info( "In the directory: %s"%(directory)                                 )
          logging.log.info( "I am matching files %s[%0*i to %0*i]"%(prefix, int(digits), firstNumber, int(digits), lastNumber) )
        except:
          print "**********************image_finder():***************************" 
          print "In the directory: %s"%(directory)                                 
          print "I am matching files %s[%0*i to %0*i]"%(prefix, int(digits), firstNumber, int(digits), lastNumber) 

        for i in range(firstNumber,lastNumber):
            currentFile = "%s/%s%0*i%s"%( directory, prefix, int(digits), i, extension )
            if not os.path.isfile(currentFile):
              try: logging.log.warning( "I can not find file %s"%(currentFile) )
              except: print  "I can not find file %s"%(currentFile) 

        try: logging.log.info( "****************************************************************" )
        except: print  "****************************************************************" 
        slices_extent = [firstNumber, lastNumber]

    return prefix, digits, slices_extent, extension



def image_finder_data( data ):

    data.image_prefix[0], data.image_digits[0], data.image_slices_extent[0], data.image_ext = image_finder ( data.DIR_image[0], data.image_filter[0], data.image_ext, data.image_digits[0] )
    data.image_prefix[1], data.image_digits[1], data.image_slices_extent[1], data.image_ext = image_finder ( data.DIR_image[1], data.image_filter[1], data.image_ext, data.image_digits[1] )

    return data
