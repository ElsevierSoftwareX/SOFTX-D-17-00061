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

# ... File to read images ...

import logging
from print_variable import pv

def read_raw_3D( image_data_format, image_size, base_dir, raw_base_name, extension, slices_range, crop ):
    """
      This reads RAW volume

    INPUTS:
    - Image format        image format as a format spec, i.e. '<f4'
    - image_size          size of  RAW files.
    - base_dir            the directory inside which the raw files are.
    - raw_base_name       the "base" name of the raw files
    - extension           extension of raw files
    - slices_range        tuple or list of number of slices to read
    - crop                list of lists: [ [ x_min, x_max ], [ y_min, y_max ] ]
    """    
    
    import numpy
    
    filename = "%s/%s%s"%( base_dir, raw_base_name, extension )
    try: logging.log.debug( "read_raw_3D: Loading Full Volume: %s"%(filename) )
    except: print "read_raw_3D: Loading Full Volume: %s"%(filename) 

    try:
      outputVolume = numpy.fromfile( filename, dtype=image_data_format )
    except:
      try: logging.log.warning( "read_raw_slices(): File %s not found "%filename )
      except: print  "read_raw_slices(): File %s not found "%filename 
      outputVolume = []
      
    try:
      if outputVolume != []:
        outputVolume = outputVolume.reshape( image_size )
    except:
      raise Exception( "read_raw_slices(): Check image dimensions or ROI")

    outputVolume = outputVolume[ slices_range[0]:slices_range[1]+1, crop[0][1]:crop[1][1]+1, crop[0][2]:crop[1][2]+1 ]

    return outputVolume



def read_raw_slices( image_data_format, image_size, base_dir, raw_base_name, digits, extension, slices_range, crop=None ):
    """
    2014-05-16 -- Edward Ando and Nadia Demartinou
      This reads RAW slices, and returns a 3D volume

    INPUTS:
    - Image format        image format as a format spec, i.e. '<f4'
    - image_size          size of  RAW files.
    - base_dir            the directory inside which the raw files are.
    - raw_base_name       the "base" name of the raw files
    - digits              pre-padding with zeros in file number
    - extension           extension of raw files
    - slices_range        tuple or list of number of slices to read
    - crop                list of lists: [ [ x_min, x_max ], [ y_min, y_max ] ]
    """    
    import numpy
    
    # ET: there should be a +1 here because if I want to load slices from 1 to 5 this give 5 slices and not 4
    numberOfSlices = int( slices_range[1] - slices_range[0] + 1 )
    
    if crop == None:
        outputVolume = numpy.ones( ( numberOfSlices, image_size[1], image_size[0] ), dtype=image_data_format ) * numpy.nan
    else:
        outputVolume = numpy.ones( ( numberOfSlices, crop[1][1]-crop[1][0], crop[0][1]-crop[0][0] ), dtype=image_data_format ) * numpy.nan

    for sliceNumber in range( numberOfSlices ):
        
        try:
            # 2016-04-30 ET: if worrking in 2D digits == 0 and the name in constructed differently
            if digits ==0:
              filename = "%s/%s%s"%( base_dir, raw_base_name, extension )
            else:
              filename = "%s/%s%0*i%s"%( base_dir, raw_base_name, int(digits), sliceNumber + slices_range[0], extension )
            currentImage = numpy.fromfile( filename, dtype=image_data_format )
        except:
            try: logging.log.warning( "read_raw_slices(): File %s not found "%filename )
            except: print "read_raw_slices(): File %s not found "%filename 
            currentImage = []

        try:
          if currentImage != []:
            currentImage = currentImage.reshape( ( image_size ) )
            if crop == None:
                outputVolume[ sliceNumber ] = currentImage
            else:
                outputVolume[ sliceNumber ] = currentImage[ crop[1][0]:crop[1][1], crop[0][0]:crop[0][1] ]
        except:
              raise Exception( "read_raw_slices(): Check image dimensions or ROI")

    return outputVolume

    
    
def read_tiff_3D( image_data_format, image_size, base_dir, base_name, extension, slices_range, crop  ):
    """
      This reads TIFF volume

    INPUTS:
    - Image format        image format as a format spec, i.e. '<f4'
    - image_size          size of  RAW files.
    - base_dir            the directory inside which the raw files are.
    - tiff_base_name      the "base" name of the raw files
    - extension           extension of raw files
    - slices_range        tuple or list of number of slices to read
    - crop                list of lists: [ [ x_min, x_max ], [ y_min, y_max ] ]
    """    

    import numpy
    import tifffile

    filename = "{}/{}{}".format( base_dir, base_name, extension )
    try: logging.log.debug( "Read_tiff_3D: Loading Full TIFF Volume: %s"%(filename) )
    except: print "Read_tiff_3D: Loading Full TIFF Volume: %s"%(filename) 

    outputVolume =  tifffile.imread( filename )
    outputVolume = outputVolume[ slices_range[0]:slices_range[1]+1, crop[0][1]:crop[1][1]+1, crop[0][2]:crop[1][2]+1 ]

    try: logging.log.debug( "Read_tiff_3D: Volume mean value: %f"%( outputVolume.mean() ) )
    except: print  "Read_tiff_3D: Volume mean value: %f"%( outputVolume.mean() ) 

    return outputVolume


  
def read_tiff_slices( image_data_format, imageDimensions, base_dir, tiff_base_name, digits, extension, slices_range, crop=None ):
    """
    This reads TIFF slices, and returns a 3D volume
    2015-03-31 EA: This is becoming default tiff reader with tifffile.py from http://www.lfd.uci.edu/~gohlke/

    INPUT:
    - Image format        image format as a format spec, i.e. '<f4'
    - image_size          size of  RAW files.
    - base_dir            the directory inside which the raw files are.
    - tiff_base_name      the "base" name of the raw files
    - digits              pre-padding with zeros in file number
    - extension           extension of raw files
    - slices_range        tuple or list of number of slices to read
    - crop                list of lists: [ [ x_min, x_max ], [ y_min, y_max ] ]
    """    

    import tifffile
    import numpy
    
    # Erika: there should be a +1 here because if I want to load slices from 1 to 5 this give 5 slices and not 4
    numberOfSlices = int( slices_range[1] - slices_range[0] + 1 )
    
    # Define array for image loading
    if crop == None:
        # If we don't have a crop, we're going to use the whole slice size.
        outputVolume = numpy.ones( ( numberOfSlices, imageDimensions[1], imageDimensions[0] ), dtype=image_data_format ) * numpy.nan
    else:
        # Slice dimensions from crop
        outputVolume = numpy.ones( ( numberOfSlices, crop[1][1] - crop[1][0], crop[0][1] - crop[0][0] ), dtype=image_data_format ) * numpy.nan

    # Load all images into big array
    for sliceNumber in range( numberOfSlices ):
          
          try:
              # 2016-04-30 ET: if worrking in 2D digits == 0 and the name in constructed differently
              if digits ==0:
                filename = "%s/%s%s"%( base_dir, tiff_base_name, extension ) 
              else:
                filename = "%s/%s%0*i%s"%( base_dir, tiff_base_name, digits, sliceNumber + slices_range[0], extension ) 
              # 2015-03-31 EA: Adding a transpose here: -------------------------------------------------------------------------------------| Instead of reshape with PIL...
              #                                                                                                                              V
              currentImage = tifffile.imread( filename )

              if crop == None:
                  outputVolume[ sliceNumber ] = currentImage.reshape( currentImage.size[1], currentImage.size[0] )
              else:
                  outputVolume[ sliceNumber ] = currentImage[ crop[1][0]:crop[1][1], crop[0][0]:crop[0][1] ]

          except :
                #print "\nread_tiff_slices(): Could not read slice "
              try: logging.log.warning( "read_tiff_slices(): File %s not found "%filename )
              except: print "read_tiff_slices(): File %s not found "%filename 
        
    try: logging.log.debug( "read_tiff_slices(): Volume mean value = %s"%(outputVolume.mean()) )
    except: print "read_tiff_slices(): Volume mean value = %s"%(outputVolume.mean()) 
    
    return outputVolume
  
  
def read_tiff_pil_slices( image_data_format, imageDimensions, base_dir, tiff_base_name, digits, extension, slices_range, crop=None ):
    """
    This reads TIFF slices, and returns a 3D volume

    This code has been copied over from:
    RING ARTEFACT CORRECTION PROGRAM - Edward Ando and Matias Silva Illanes
    2013-06-18 - Simple, slow attempt to correct Matias' ring artefacts with
      radiographs /tomo/SCAN/Dmt_Matias_Silva/05.Essai_020413/01.80,1/

    2014-05-16 - ET and EA: Modified to take image_data_format and imageDimensions as input
      and to return a slice of Nan when does not find a file. Control on the crop size moved to image_size_and_type
    
    2015-03-12 EA and ET (the other one): Reading 16-bit unsigned int tiffs from the XAct reconstruction programme
      (this probably applied to all such images) actually makes them come out as SIGNED 16 bit images, which 
      screws everything up. Solution in the long term will be to pass to a less stupid image library such as the 
      repaired "Pillow" which takes on from PIL: http://pillow.readthedocs.org/en/latest/index.html
    
    2015-03-31 EA: This is becoming TIFF_PIL now
    
    In the meanwhile, we can force the data into 16-bit unsignedness by forcing a dtype on the numpy array.
    
    INPUT:
    - Image format        image format as a format spec, i.e. '<f4'
    - image_size          size of  RAW files.
    - base_dir            the directory inside which the raw files are.
    - tiff_base_name      the "base" name of the raw files
    - digits              pre-padding with zeros in file number
    - extension           extension of raw files
    - slices_range        tuple or list of number of slices to read
    - crop                list of lists: [ [ x_min, x_max ], [ y_min, y_max ] ]
    """    

    try:
      from PIL import Image
    except:
      raise Exception( "Module PIL - Image not intalled" )
      
    import numpy
    
    # Erika: there should be a +1 here because if I want to load slices from 1 to 5 this give 5 slices and not 4
    numberOfSlices = int( slices_range[1] - slices_range[0] + 1 )

    # Define array for image loading
    if crop == None:
        # If we don't have a crop, we're going to use the whole slice size.
        outputVolume = numpy.ones( ( numberOfSlices, imageDimensions[1], imageDimensions[0] ), dtype=image_data_format ) * numpy.nan
    else:
        # Slice dimensions from crop
        outputVolume = numpy.ones( ( numberOfSlices, crop[1][1] - crop[1][0], crop[0][1] - crop[0][0] ), dtype=image_data_format ) * numpy.nan

    # Load all images into big array
    for sliceNumber in range( numberOfSlices ):

        try:
            # 2016-04-30 ET: if worrking in 2D digits == 0 and the name in constructed differently
            if digits ==0:
              filename = "%s/%s%s"%( base_dir, tiff_base_name, extension ) 
            else:
              filename = "%s/%s%0*i%s"%( base_dir, tiff_base_name, digits, sliceNumber + slices_range[0], extension ) 
            currentImage = Image.open( filename )

            # put it into the right place in the radios matrix, transposing because numpy (y,x) and PIL (x,y) are confused
            #  NOTE: transpose doesn't work, we're just going to reshape( y,x) whch works
            if crop == None:
                outputVolume[ sliceNumber ] = numpy.array( currentImage.getdata(), dtype=image_data_format ).reshape( currentImage.size[1], currentImage.size[0] )
            else:
                outputVolume[ sliceNumber ] = numpy.array( currentImage.getdata(), dtype=image_data_format ).reshape( currentImage.size[1], currentImage.size[0] )[ crop[1][0]:crop[1][1], crop[0][0]:crop[0][1] ]

        except :
            try: logging.log.warning( "read_tiff_slices(): File %s not found "%filename )
            except: print "read_tiff_slices(): File %s not found "%filename 
    
    try: logging.log.debug( "read_tiff_pil_slices(): Volume mean value = %s"%( outputVolume.mean() ) )
    except: print "read_tiff_pil_slices(): Volume mean value = %s"%( outputVolume.mean() ) 
        
    return outputVolume
  
  
def read_edf_slices( imageDimensions, base_dir, edf_base_name, digits, extension, slices_range, crop=None ):
    """
    This reads EDF slices, and returns a 3D volume

    INPUT:
    - image_size          size of  RAW files.
    - base_dir            the directory inside which the raw files are.
    - edf_base_name       the "base" name of the raw files
    - digits              pre-padding with zeros in file number
    - extension           extension of raw files
    - slices_range        tuple or list of number of slices to read
    - crop                list of lists: [ [ x_min, x_max ], [ y_min, y_max ] ]
    """    

    import numpy
    import EdfFile
    
    # ET: there should be a +1 here because if I wanto to load slices from 1 to 5 this give 5 slices and not 4 
    numberOfSlices = slices_range[1] - slices_range[0] + 1
        
    # Define array for image loading
    if crop == None:
        # If we don't have a crop, we're going to use the whole slice size.
        outputVolume = numpy.ones( ( numberOfSlices, imageDimensions[1], imageDimensions[0] ), dtype='<f4' ) * numpy.nan
    else:
        # Slice dimensions from crop
        outputVolume = numpy.ones( ( numberOfSlices, crop[1][1] - crop[1][0], crop[0][1] - crop[0][0] ), dtype='<f4' ) * numpy.nan

    # Load all images into big array
    for sliceNumber in range( numberOfSlices ):

        try:
            # 2016-04-30 ET: if worrking in 2D digits == 0 and the name in constructed differently
            if digits ==0:
              filename = "%s/%s%s"%( base_dir, edf_base_name, extension )
            else:
              filename = "%s/%s%0*i%s"%( base_dir, edf_base_name, digits, sliceNumber + slices_range[0], extension )
            currentImage = numpy.array( EdfFile.EdfFile( filename ).GetData( 0 ) )

            if crop == None:
                outputVolume[ sliceNumber ] = currentImage
            else:
                outputVolume[ sliceNumber ] = currentImage[ crop[1][0]:crop[1][1], crop[0][0]:crop[0][1] ]
                
        except :
            try: logging.log.warning( "read_edf_slices(): File %s not found "%filename )
            except: print "read_edf_slices(): File %s not found "%filename 
            pass
          
    try: logging.log.debug( "read_edf_pil_slices(): Volume mean value = %s"%( outputVolume.mean() ) )
    except: print "read_edf_pil_slices(): Volume mean value = %s"%( outputVolume.mean() ) 

    return outputVolume
  
  
  
def read_su(  ):
    pass

def read_images( image_data_format, image_format, image_size, base_dir, base_name, digits, extension, corners, slices_range ):
        import sys
        
        # 2015-03-31 EA: This is now the tifffile reader
        if  image_format == "TIFF":
            if len( image_size ) == 3:
                outputVolume = read_tiff_3D( image_data_format, image_size, base_dir, base_name, extension, slices_range, corners )
            else:
                outputVolume = read_tiff_slices(     image_data_format, image_size, base_dir, base_name, digits, extension, slices_range, [ [ corners[0][2], corners[1][2] ], [ corners[0][1], corners[1][1] ] ] )
                
        # 2015-03-31 EA: Moving to tiffffile for reading TIFF images, leaving the old option as a type of image called TIFF_PIL
        elif  image_format == "TIFF_PIL":
            outputVolume = read_tiff_pil_slices( image_data_format, image_size, base_dir, base_name, digits, extension, slices_range, [ [ corners[0][2], corners[1][2] ], [ corners[0][1], corners[1][1] ] ] )
          
        elif  image_format == "EDF":
            outputVolume = read_edf_slices( image_size, base_dir, base_name, digits, extension, slices_range, [ [ corners[0][2], corners[1][2] ], [ corners[0][1], corners[1][1] ] ] )
            
        elif image_format == "RAW":
            if len( image_size ) == 2:
                outputVolume =  read_raw_slices( image_data_format, image_size, base_dir, base_name, digits, extension, slices_range, [ [ corners[0][2], corners[1][2] ], [ corners[0][1], corners[1][1] ] ] )
                  
            elif len( image_size ) == 3:
                outputVolume = read_raw_3D( image_data_format, image_size, base_dir, base_name, extension, slices_range, corners )
                
            else:
                raise Exception( "read_images(): image_size has to have 2 or 3 dimensions ")
                
        else:
            raise Exception( "read_images(): Unsupported image format")

        return outputVolume
