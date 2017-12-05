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
Functions that check the image_format and ask for it if necessary then read the first 
images in the two folders and determine their size and type
"""

import tifffile, numpy, getopt, re, sys
import logging
from print_variable import pv

try:
  from PIL import Image
except:
  pass

def image_size_and_type( data ):

    if re.compile( r"\.[Tt][Ii][Ff]{1,2}" ).match(data.image_ext):
        if data.image_format == "auto" or data.image_format == "TIFF":
          data.image_format = "TIFF"

          # 1.1 Load the first image in both directories and figure out its dimensions
          try:
            
              if data.image_slices_extent[0][0] is None:
                  # This is the case for 2D images
                  image_filename="%s/%s%s"%( data.DIR_image[0], data.image_prefix[0], data.image_ext )
              else:
                  image_filename="%s/%s%0*i%s"%( data.DIR_image[0], data.image_prefix[0], int(data.image_digits[0]), data.image_slices_extent[0][0], data.image_ext )
              
              # Transpose below!
              firstImage1 = tifffile.imread( image_filename ).T

              data.image_data_format = firstImage1.dtype.str
              
              if data.image_slices_extent[0][0] is None:
                  # This is the case for 2D images
                  image_filename="%s/%s%s"%( data.DIR_image[1], data.image_prefix[1], data.image_ext )
              else:
                  image_filename="%s/%s%0*i%s"%( data.DIR_image[1], data.image_prefix[1], int(data.image_digits[1]), data.image_slices_extent[1][0], data.image_ext )
                  
              # Transpose below!
              firstImage2 = tifffile.imread( image_filename ).T

              data.image_size     = numpy.array( [ firstImage1.shape[::-1], firstImage2.shape[::-1] ] )
              
              # checks that the format is the same for image_1 and image_2 and if not gives an error
              # we might want to give the possibility to have different format in the future
              if firstImage2.dtype != data.image_data_format:
                  raise Exception("image_size_and_type(): The images seem to have different format. We can not deal with it now. Exiting")

              del firstImage1, firstImage2

          except getopt.GetoptError as e:
              raise Exception('image_size_and_type(): Could not open images')

        # 2015-03-31 EA: Old system for loading TIFF files with PIL
        elif data.image_format == "TIFF_PIL":
          import Image
          # 1.1 Load the first image in both directories and figure out its dimensions
          try:
              firstImage1 = Image.open( "%s/%s%0*i%s"%( data.DIR_image[0], data.image_prefix[0], int(data.image_digits[0]), data.image_slices_extent[0][0], data.image_ext ) )
              #                                 backwards
              data.image_size[0] = numpy.array(firstImage1.size[ :: -1 ])

              if firstImage1.mode == "I;16":
                  data.image_data_format = '<u2'
              elif firstImage1.mode == "I;16B":
                  data.image_data_format = '<u2'
              elif firstImage1.mode == "F":
                  data.image_data_format = '<f4'
              else:
                  raise Exception('image_size_and_type(): Image mode (%s) not supported, someone should add this and check the reading is done properly"%(mode)')

              firstImage2 = Image.open( "%s/%s%0*i%s"%( data.DIR_image[1], data.image_prefix[1], int(data.image_digits[1]), data.image_slices_extent[1][0], data.image_ext ) )
              #                                 backwards
              data.image_size[1] = numpy.array(firstImage2.size[ :: -1 ])
              data.image_size = numpy.array(data.image_size)
              # checks that the format is the same for image_1 and image_2 and if not gives an error
              # we might want to give the possibility to have different format in the future
              if firstImage2.mode != firstImage1.mode:
                  raise Exception("image_size_and_type(): The images seem to have different format. We can not deal with it now. Exiting")

              del firstImage1, firstImage2

          except getopt.GetoptError as e:
              raise Exception('image_size_and_type(): Could not open images')

        else:
          raise Exception( "image_size_and_type(): image_format given in input (%s) does not match the extension found (%s)\nOmit image_format or define image_ext"%( data.image_format, data.image_ext ) )

    elif re.compile( r"\.[Ee][Dd][Ff]" ).match(data.image_ext):

        import EdfFile

        if data.image_format == None or data.image_format == "EDF":
          data.image_format = "EDF"
          # 1.1 Load the first image in both directories and figure out its dimensions
          firstImage = numpy.array( EdfFile.EdfFile( "%s/%s%0*i%s"%( data.DIR_image[0], data.image_prefix[0], int(data.image_digits[0]), data.image_slices_extent[0,0], data.image_ext ) ).GetData( 0 )  )
          #                         backwards
          data.image_size[0] = firstImage.shape[ :: -1 ]
          firstImage = numpy.array( EdfFile.EdfFile( "%s/%s%0*i%s"%( data.DIR_image[1], data.image_prefix[1], int(data.image_digits[1]), data.image_slices_extent[1,0], data.image_ext ) ).GetData( 0 )  )
          #                         backwards
          data.image_size[1] = firstImage.shape[ :: -1 ]

          #HACK we assume Edf file to be 32bit for the memLimitSlices calculation
          data.image_data_format = '<f4'

          del firstImage

        else:
          raise Exception( "image_size_and_type(): image_format given in input (%s) does not match the extension found (%s)\nOmit image_format or define image_ext"%( data.image_format, data.image_ext ) )

    elif data.image_format != "RAW":
        raise Exception("image_size_and_type(): image_format not recognised. Give it as input")

    # === Loop over image numbers 0 and 1 === #
    for im in [ 0, 1 ]:
          # === Check we're not operating on a single file, i.e., either a 3D volume or a single 2D image file === #
          if any(x is None for x in data.image_slices_extent[im]):
              if len( data.image_size[im] ) == 3:
                # Then we're in a 3D volume -- so update the slices extent based on the third value of image_size that should be set.
                #print "\timage_size_and_type(): 3D Volume -- extents = size of whole volume!"
                data.image_slices_extent[im] = [ 0, data.image_size[im,0]-1 ]
              else:
                try: logging.log.debug( "image_size_and_type(): I got data.image_slices_extent == None, but I'm in a 2D file... " )
                except: print "image_size_and_type(): I got data.image_slices_extent == None, but I'm in a 2D file... " 
                data.image_slices_extent[im] = [ 0, 0 ]

          # === Update ROI to whole volume if missing === #
    if data.ROI_corners == [[None,None,None],[None,None,None]]:
        #                                               zLow                   yL xL                 zHigh                      yHigh                       xHigh
        data.ROI_corners = numpy.array( [ [ data.image_slices_extent[0,0], 0, 0 ], [ data.image_slices_extent[0,1], data.image_size[0,-2]-1, data.image_size[0,-1]-1 ] ] )
        
    data.ROI_corners = [ data.ROI_corners, [[None,None,None],[None,None,None]] ]

    # Updating the ROI corners to respect image sizes
    data.ROI_corners[0][0][0] = max( data.ROI_corners[0][0][0], data.image_slices_extent[0,0] )  # zLow
    data.ROI_corners[0][1][0] = min( data.ROI_corners[0][1][0], data.image_slices_extent[0,1] )  # zHigh
    data.ROI_corners[0][0][1] = max( data.ROI_corners[0][0][1], 0                             )  # yLow
    data.ROI_corners[0][1][1] = min( data.ROI_corners[0][1][1], data.image_size[0,-2]-1       )  # yHigh
    data.ROI_corners[0][0][2] = max( data.ROI_corners[0][0][2], 0                             )  # xLow
    data.ROI_corners[0][1][2] = min( data.ROI_corners[0][1][2], data.image_size[0,-1]-1       )  # xHigh
    
    # Updating the ROI corners to respect image sizes and extra data needed to correlate
    data.ROI_corners[1][0][0] = max( data.ROI_corners[0][0][0] - data.correlation_window[0] + data.search_window[0][0], data.image_slices_extent[1,0] )  # zLow
    data.ROI_corners[1][1][0] = min( data.ROI_corners[0][1][0] + data.correlation_window[0] + data.search_window[0][1], data.image_slices_extent[1,1] )  # zHigh
    data.ROI_corners[1][0][1] = max( data.ROI_corners[0][0][1] - data.correlation_window[1] + data.search_window[1][0], 0                             )  # yLow
    data.ROI_corners[1][1][1] = min( data.ROI_corners[0][1][1] + data.correlation_window[1] + data.search_window[1][1], data.image_size[1,-2]-1       )  # yHigh
    data.ROI_corners[1][0][2] = max( data.ROI_corners[0][0][2] - data.correlation_window[2] + data.search_window[2][0], 0                             )  # xLow
    data.ROI_corners[1][1][2] = min( data.ROI_corners[0][1][2] + data.correlation_window[2] + data.search_window[2][1], data.image_size[1,-1]-1       )  # xHigh

    data.ROI_corners = numpy.array(data.ROI_corners)

    return data