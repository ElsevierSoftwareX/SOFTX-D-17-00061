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

# 2013-08-22 - This test file is supposed to read in a finished, regular subpixel input, and output files.
# 2014-03-13 - Adding a median filter on the kinematics, from Pierre's suggestion

import numpy
import logging

from scipy.interpolate import griddata
from prior_field.prior_median_filter import kinematics_median_filter_fnc
from tools.vtk_tools import WriteVTK_data, WriteVTK_maesh, WriteVTK_headers
from tools.calculate_node_spacing import calculate_node_spacing
from tools.correct_pixel_size_changing import correct_pixel_size_changing
from tools.cc_autothreshold import cc_autothreshold
from tools.resampling_irregular_grid import resampling_irregular_grid
from tools.kinematic_filters import kinematics_remove_outliers
from postproc.regular_strain_small_strain import regular_strain_small_strain
from postproc.regular_strain_large_strain import regular_strain_large_strain
from postproc.regular_strain_large_strain_centred import regular_strain_large_strain_centred
from postproc.tetrahedral_elements_strain import tetrahedral_elements_strain
from tools.print_variable import pv

def construct_mask( kinematics, cc_threshold=None ):
  
    cc_field = numpy.array( kinematics[ :, 10 ] ).astype( '<f4' )

    #-----------------------------------------------------------------------
    #-  Generate a NaN mask to add to other fields                        --
    #-----------------------------------------------------------------------
    mask = numpy.zeros( cc_field.shape, dtype='<f4' )


    if cc_threshold == "auto":
        # if we have a cc_threshold set, add this to the mask
        cc_threshold = cc_autothreshold( cc_field )

    if cc_threshold == None:
        cc_threshold = -1.0 #why do we need this?

    else:
        # if cc_threshold != None, calculate and apply mask
        cc_threshold = float( cc_threshold )
        # ...and mask with cc_threshold
        mask[ numpy.where( cc_field < cc_threshold ) ] = numpy.nan

    # add the nodes which are error nodes to the mask
    mask[ numpy.where( kinematics[ :, 11 ] != 0 ) ] = numpy.inf
    mask[ numpy.where( kinematics[ :, 11 ] > 2 ) ] = numpy.nan
     
    return mask

def process_results(  kinematics, data ):
    
    interpolate_strain = False
  
    # 2015-04-14 EA: Adding default option to save output files as tiff, which requires tifffile.py
    if data.saveTIFF:
      # tools already added to path
      from tools.tifffile import imsave

    # Generate a mask for the output of the files.
    #   1. All nodes which have reported an error need to be masked.
    #   2. All nodes which have low CC can also be optionally masked.

    # Generate all fields replacing error Nodes with NaNs -- to read from kinematics array...
    # 2013-08-22 - Calculation of node spacing moved to ./tools/calculate_node_spacing.py
    nodes_z, nodes_y, nodes_x = calculate_node_spacing( kinematics[ :, 1:4 ] )

    cc_field = numpy.array( kinematics[ :, 10 ] ).astype( '<f4' )

    mask = construct_mask( kinematics, data.cc_threshold )

    #-----------------------------------------------------------------------
    #-  Done generating the mask...                                       --
    #-----------------------------------------------------------------------
    # Clean up the kinematics with the mask
    for i in [ 4,5,6,7,8,9 ]: kinematics[ :, i ] += mask

    # Remove outliers
    if data.remove_outliers_filter_size != None:
      if data.remove_outliers_filter_size > 0:
          try: logging.log.info("process_results(): Removing outliers") 
          except: print "process_results(): Removing outliers"
          try:
            #kinematics[ :, 4:10 ] = data.kinematics_median_filter_fnc( kinematics[ :, 1:4 ], kinematics[ :, 4:10 ], data.kinematics_median_filter )
            [ kinematics[ :, 4:10 ], mask_outliers ] = kinematics_remove_outliers( kinematics[ :, 1:4 ], kinematics[ :, 4:10 ], \
                data.remove_outliers_filter_size, data.remove_outliers_threshold, data.remove_outliers_absolut_threshold, data.remove_outliers_filter_high, data.filter_base_field )
            #mask[ numpy.where(mask_outliers==1) ] = 0
            mask[ numpy.isfinite(kinematics[:,4]) ] = 0
          except Exception as exc:
            try: logging.log.warn(exc.message)
            except: print exc.message
            pass

    # filter kinematics...
    if data.kinematics_median_filter != None:
      if data.kinematics_median_filter > 0:
          try: logging.log.info("process_results(): Applying a Kinematics Median filter of {:0.1f} (3 means ±1)".format( data.kinematics_median_filter ))
          except: print "process_results(): Applying a Kinematics Median filter of {:0.1f} (3 means ±1)".format( data.kinematics_median_filter )
          try:
            kinematics[ :, 4:10 ] = kinematics_median_filter_fnc( kinematics[ :, 1:4 ], kinematics[ :, 4:10 ], data.kinematics_median_filter )
            mask[ numpy.isfinite(kinematics[:,4]) ] = 0
          except Exception as exc:
            try: logging.log.warn(exc.message)
            except: print exc.message

    if data.pixel_size_ratio != 1:
      if data.image_centre is not None:
          kinematics = correct_pixel_size_changing( kinematics, data.pixel_size_ratio, data.image_centre )
      else:
          raise Exception('Image centre needed to correct pixel size ratio')

    try: logging.log.info( "Writing output files to {}/{}".format( data.DIR_out, data.output_name ) )
    except: print "Writing output files to {}/{}".format( data.DIR_out, data.output_name )

    if data.saveTIFF:
      if data.saveError: imsave( data.DIR_out + "/%s-error-field-%04ix%04ix%04i.tif"%( data.output_name, len(nodes_x), len(nodes_y), len(nodes_z) ), kinematics[ :, 11 ].reshape( ( len(nodes_z), len(nodes_y), len(nodes_x) ) ).astype( '<f4' ) )
      if data.saveCC:    imsave( data.DIR_out +    "/%s-cc-field-%04ix%04ix%04i.tif"%( data.output_name, len(nodes_x), len(nodes_y), len(nodes_z) ),            cc_field.reshape( ( len(nodes_z), len(nodes_y), len(nodes_x) ) ).astype( '<f4' ) )
      if data.saveMask:  imsave( data.DIR_out +        "/%s-mask-%04ix%04ix%04i.tif"%( data.output_name, len(nodes_x), len(nodes_y), len(nodes_z) ),                mask.reshape( ( len(nodes_z), len(nodes_y), len(nodes_x) ) ).astype( '<f4' ) )
    if data.saveRAW:
      if data.saveError: kinematics[ :, 11 ].astype( '<f4' ).tofile( data.DIR_out + "/%s-error-field-%04ix%04ix%04i.raw"%( data.output_name, len(nodes_x), len(nodes_y), len(nodes_z)) )
      if data.saveCC:    cc_field.astype( '<f4' ).tofile(           data.DIR_out + "/%s-cc-field-%04ix%04ix%04i.raw"%( data.output_name, len(nodes_x), len(nodes_y), len(nodes_z)) )
      if data.saveMask:   mask.astype( '<f4' ).tofile(               data.DIR_out + "/%s-mask-%04ix%04ix%04i.raw"%( data.output_name, len(nodes_x), len(nodes_y), len(nodes_z)) )
    if data.saveVTK:
      headersEndPosition = WriteVTK_headers( data.DIR_out + "/%s.vtk"%( data.output_name ), kinematics[ :, 1:4 ], mask )
      if data.saveCC or data.saveDispl or data.saveRot: WriteVTK_data( data.DIR_out + "/%s.vtk"%( data.output_name ), '', [], data_type = 'POINT_DATA', nPoints = numpy.where(numpy.isfinite(mask))[0].shape[0] )
      if data.saveCC: WriteVTK_data( data.DIR_out + "/%s.vtk"%( data.output_name ), 'correlation_coefficient', cc_field, mask )
      if data.saveError:
        WriteVTK_headers( data.DIR_out + "/%s_errors.vtk"%( data.output_name ), kinematics[ :, 1:4 ] )
        WriteVTK_data( data.DIR_out + "/%s_errors.vtk"%( data.output_name ), 'error'                  , kinematics[ :, 11 ], [], 'POINT_DATA')

    if data.saveDispl:
      if data.saveTIFF:
        if not data.images_2D: imsave( data.DIR_out + "/%s-z-field-%04ix%04ix%04i.tif"%(  data.output_name, len(nodes_x), len(nodes_y), len(nodes_z)),     kinematics[ :, 4 ].reshape( ( len(nodes_z), len(nodes_y), len(nodes_x) ) ).astype( '<f4' ) )
        imsave( data.DIR_out + "/%s-y-field-%04ix%04ix%04i.tif"%(  data.output_name, len(nodes_x), len(nodes_y), len(nodes_z)),     kinematics[ :, 5 ].reshape( ( len(nodes_z), len(nodes_y), len(nodes_x) ) ).astype( '<f4' ) )
        imsave( data.DIR_out + "/%s-x-field-%04ix%04ix%04i.tif"%(  data.output_name, len(nodes_x), len(nodes_y), len(nodes_z)),     kinematics[ :, 6 ].reshape( ( len(nodes_z), len(nodes_y), len(nodes_x) ) ).astype( '<f4' ) )
      if data.saveRAW:
        if not data.images_2D: kinematics[ :, 4 ].astype( '<f4' ).tofile( data.DIR_out + "/%s-z-field-%04ix%04ix%04i.raw"%(  data.output_name, len(nodes_x), len(nodes_y), len(nodes_z)) )
        kinematics[ :, 5 ].astype( '<f4' ).tofile( data.DIR_out + "/%s-y-field-%04ix%04ix%04i.raw"%(  data.output_name, len(nodes_x), len(nodes_y), len(nodes_z)) )
        kinematics[ :, 6 ].astype( '<f4' ).tofile( data.DIR_out + "/%s-x-field-%04ix%04ix%04i.raw"%(  data.output_name, len(nodes_x), len(nodes_y), len(nodes_z)) )
      if data.saveVTK:
        WriteVTK_data( data.DIR_out + "/%s.vtk"%( data.output_name ), 'Displacements', kinematics[ :, 4:7 ], mask)

    if data.saveRot:
      if data.saveTIFF:
        if not data.images_2D: imsave( data.DIR_out + "/%s-z-rotvect-%04ix%04ix%04i.tif"%(  data.output_name, len(nodes_x), len(nodes_y), len(nodes_z)),     kinematics[ :, 7 ].reshape( ( len(nodes_z), len(nodes_y), len(nodes_x) ) ).astype( '<f4' ) )
        imsave( data.DIR_out + "/%s-y-rotvect-%04ix%04ix%04i.tif"%(  data.output_name, len(nodes_x), len(nodes_y), len(nodes_z)),     kinematics[ :, 8 ].reshape( ( len(nodes_z), len(nodes_y), len(nodes_x) ) ).astype( '<f4' ) )
        imsave( data.DIR_out + "/%s-x-rotvect-%04ix%04ix%04i.tif"%(  data.output_name, len(nodes_x), len(nodes_y), len(nodes_z)),     kinematics[ :, 9 ].reshape( ( len(nodes_z), len(nodes_y), len(nodes_x) ) ).astype( '<f4' ) )
      if data.saveRAW:
        if not data.images_2D: kinematics[ :, 7 ].astype( '<f4' ).tofile( data.DIR_out + "/%s-z-rotvect-%04ix%04ix%04i.raw"%(  data.output_name, len(nodes_x), len(nodes_y), len(nodes_z)) )
        kinematics[ :, 8 ].astype( '<f4' ).tofile( data.DIR_out + "/%s-y-rotvect-%04ix%04ix%04i.raw"%(  data.output_name, len(nodes_x), len(nodes_y), len(nodes_z)) )
        kinematics[ :, 9 ].astype( '<f4' ).tofile( data.DIR_out + "/%s-x-rotvect-%04ix%04ix%04i.raw"%(  data.output_name, len(nodes_x), len(nodes_y), len(nodes_z)) )
      if data.saveVTK:
        WriteVTK_data( data.DIR_out + "/%s.vtk"%( data.output_name ), 'Rotations', kinematics[ :, 7:10 ], mask)

    try:
      if data.calculate_strain:
        if    data.strain_mode == "smallStrains":
            [ strain, rot, connectivity, cellIndex ] = regular_strain_small_strain( kinematics[:,1:4], kinematics[:,4:7] )
          
            if data.saveVTK:
              connectivity = numpy.searchsorted(numpy.where(numpy.isfinite(mask))[0],connectivity)
              cellType = 12

        elif  data.strain_mode == "largeStrains":
            [ strain, rot, connectivity, cellIndex, volStrain ] = regular_strain_large_strain( kinematics[:,1:4], kinematics[:,4:7], data.saveVTK )
            
            if data.saveVTK:
              connectivity = numpy.searchsorted(numpy.where(numpy.isfinite(mask))[0],connectivity)
              cellType = 12

        elif  data.strain_mode == "largeStrainsCentred":
            neighbourhoodDistance = 1
            [ strain, rot, connectivity, volStrain ] = regular_strain_large_strain_centred( kinematics[:,1:4], kinematics[:,4:7], neighbourhoodDistance )
            if data.saveVTK:
              cellIndex = numpy.squeeze(connectivity).astype( 'i' )
              connectivity = numpy.searchsorted(numpy.where(numpy.isfinite(mask))[0],connectivity)
              cellType = 1

        elif  data.strain_mode == "tetrahedralStrains":
            [ strain, rot, connectivity, coordinates ] = tetrahedral_elements_strain( kinematics[:,1:4], kinematics[:,4:7], mask = mask )
            cellIndex = range(connectivity.shape[0])
            connectivity = numpy.searchsorted(numpy.where(numpy.isfinite(mask))[0],connectivity)
            cellType = 10   
            
            if data.saveTIFF or data.saveRAW:
              interpolate_strain = True


        strain = strain.astype( '<f4' )
        rot    = rot.astype(    '<f4' )
        strain_components = {}              
        strain_components_int = {}

        # 0S: 17-10-18 Catch 2D case
        if len(nodes_z)==1:
            twoD = True
        else:
            twoD = False

        ## Extract strain tensor components
        if len(strain.shape) == 5 :
            strain_components['zz'] = numpy.array( strain[ :, :, :, 0, 0 ] )
            strain_components['zz'] = numpy.array( strain[ :, :, :, 0, 0 ] )
            strain_components['zy'] = numpy.array( strain[ :, :, :, 0, 1 ] )
            strain_components['zx'] = numpy.array( strain[ :, :, :, 0, 2 ] )
            strain_components['yy'] = numpy.array( strain[ :, :, :, 1, 1 ] )
            strain_components['yx'] = numpy.array( strain[ :, :, :, 1, 2 ] )
            strain_components['xx'] = numpy.array( strain[ :, :, :, 2, 2 ] )
        elif len(strain.shape) == 3 :
            strain_components['zz'] = numpy.array( strain[ :, 0, 0 ] )
            strain_components['zy'] = numpy.array( strain[ :, 0, 1 ] )
            strain_components['zx'] = numpy.array( strain[ :, 0, 2 ] )
            strain_components['yy'] = numpy.array( strain[ :, 1, 1 ] )
            strain_components['yx'] = numpy.array( strain[ :, 1, 2 ] )
            strain_components['xx'] = numpy.array( strain[ :, 2, 2 ] )

        # Volumetric Strain is the trace only in the case of small strains...
        if data.strain_mode == "smallStrains":
            strain_components['volumetric']     = strain_components['zz'] + strain_components['yy'] + strain_components['xx']
        
        # "Real" volumetric strain from: https://en.wikipedia.org/wiki/Infinitesimal_strain_theory#Volumetric_strain taking a=1
        elif data.strain_mode == "largeStrains" or data.strain_mode == "largeStrainsCentred" or data.strain_mode == "tetrahedralStrains":
            # 0S: 17-10-18 volumetric strain in large strains is given from the determinant of the transformation gradient tensor F
            strain_components['volumetric']  =  volStrain
        
        # Steve's Maximum Shear Strain, see: Ando (2013) Phd, and Hall et al. 2009
        # 0S: 17-10-18
        #   see Wood: Soil Behaviour and Critical State Soil Mechanics (p. 21)
        #   this definition comes from work-conjugate pairs expressed in terms of the engineering strain γ (γ=0.5*ε)
        #   so the coefficient 3 becomes 12
        #   NOTE #1: this definition is only valid for small strains, for the moment we keep it for large strains too
        #   NOTE #2: in large strains: a decomposition of the stretch tensor U=Uiso*Udev should give us the deviatoric strain --> TODO soon.
        #   NOTE #3: you need to catch a 2D case, otherwise you're subtracting 'yy' and 'xx' from 'zz'(which is 0) and that gives you a huge difference
        if not twoD:
            strain_components['maximum_shear']  = ( 1/3.0 ) * numpy.sqrt( 2*( strain_components['xx']-strain_components['yy'] )**2  +  \
                                                                        2*( strain_components['xx']-strain_components['zz'] )**2  +  \
                                                                        2*( strain_components['yy']-strain_components['zz'] )**2  +  \
                                                                            12*strain_components['yx']**2 + 12*strain_components['zx']**2 + 12*strain_components['zy']**2 )
        else:
            strain_components['maximum_shear']  = ( 1/2.0 ) * numpy.sqrt( (strain_components['xx']-strain_components['yy'] )**2  +  4*strain_components['yx']**2 )

        ############################################
        # 0S: 17-10-18:
        # tests for:
        #   1: isotropic compression and
        #   2: simple shear
        # passed for 3D and 2D.
        ############################################

        if data.saveVTK:
          WriteVTK_maesh( data.DIR_out + "/%s.vtk"%( data.output_name ), connectivity, headersEndPosition, cellType )
          WriteVTK_data( data.DIR_out + "/%s.vtk"%( data.output_name ), '', [], data_type = 'CELL_DATA', nPoints = len( connectivity ) )
          
        for component in enumerate([ 'zz', 'zy', 'zx', 'yy', 'yx', 'xx', 'volumetric', 'maximum_shear' ]):
            
            if data.saveStrain[ component[0] ]:
              
              if data.saveVTK: WriteVTK_data( data.DIR_out + "/%s.vtk"%( data.output_name ), '%s_strain'%( component[1]), strain_components[ component[1] ].flat[cellIndex] )
              
              try:
                if interpolate_strain:
                    try: logging.log.info("Interpolation of %s into a regular grid to save TIF/RAW. This can take some time..."%(component[1]))
                    except: print "Interpolation of %s into a regular grid to save TIF/RAW. This can take some time..."%(component[1])
                    strain_components_int[ component[1] ] = numpy.ones_like( mask )*numpy.nan  
                    strain_components_int[ component[1] ][ numpy.where( ~numpy.isnan(mask) ) ] = griddata( coordinates, strain_components[ component[1] ], kinematics[ numpy.where( ~numpy.isnan( mask ) ), 1:4 ] )
                    strain_components[     component[1] ] = strain_components_int[ component[1] ].reshape( ( len( nodes_z ), len( nodes_y ), len( nodes_x ) ) )
                    try: logging.log.info("Interpolation done!")
                    except: print "Interpolation done!"
                  
                if data.saveTIFF or data.saveRAW:
                  dimZ = strain_components[ component[1] ].shape[0]
                  dimY = strain_components[ component[1] ].shape[1]
                  dimX = strain_components[ component[1] ].shape[2]
                  
                if data.saveTIFF: imsave( data.DIR_out + "/%s-%s_strain-field-%04ix%04ix%04i.tif"%( data.output_name, component[1], dimX, dimY, dimZ), strain_components[ component[1] ].astype( '<f4' ) )
                if data.saveRAW:  strain_components[ component[1] ].astype( '<f4' ).tofile( data.DIR_out + "/%s-%s_strain-field-%04ix%04ix%04i.raw"%( data.output_name, component[1], dimX, dimY, dimZ) )
              
              except:
                try: logging.log.warn("Warning: it was not possible to interpolate %s strain"%(component[1]))
                except: print "Warning: it was not possible to interpolate %s strain"%(component[1])
                      
        if data.saveRotFromStrain:
          # 2014-10-13 EA: calculation of rotation
          if len(strain.shape) == 5 :
              R33 = numpy.array( rot[ :, :, :, 0, 0 ] )
              R32 = numpy.array( rot[ :, :, :, 0, 1 ] )
              R31 = numpy.array( rot[ :, :, :, 0, 2 ] )
              R22 = numpy.array( rot[ :, :, :, 1, 1 ] )
              R21 = numpy.array( rot[ :, :, :, 1, 2 ] )
              R11 = numpy.array( rot[ :, :, :, 2, 2 ] )
          elif len(strain.shape) == 3 :
              R33 = numpy.array( rot[ :, 0, 0 ] )
              R32 = numpy.array( rot[ :, 0, 1 ] )
              R31 = numpy.array( rot[ :, 0, 2 ] )
              R22 = numpy.array( rot[ :, 1, 1 ] )
              R21 = numpy.array( rot[ :, 1, 2 ] )
              R11 = numpy.array( rot[ :, 2, 2 ] )

          RotAngle = numpy.sqrt( R32**2 + R31**2 + R21**2 )

          if data.saveTIFF:
              if len(strain.shape) == 5 :
                  imsave( data.DIR_out + "/%s-rot_angle-%04ix%04ix%04i.tif"%( data.output_name, dimX, dimY, dimZ), RotAngle.astype( '<f4' ) )
              else:
                  try: logging.log.warn("Warning: Strain not in a regular grid. Can not write TIFF")
                  except: print "Warning: Strain not in a regular grid. Can not write TIFF"
          if data.saveRAW:
              if len(strain.shape) == 5 :
                  RotAngle.astype( '<f4' ).tofile( data.DIR_out + "/%s-rot_angle-%04ix%04ix%04i.raw"%( data.output_name, dimX, dimY, dimZ) )
              else:
                  try: logging.log.warn("Warning: Strain not in a regular grid. Can not write RAW")
                  except: print "Warning: Strain not in a regular grid. Can not write RAW"
          if data.saveVTK:
              #WriteVTK_data( data.DIR_out + "/%s.vtk"%( data.output_name ), 'rot_angle', RotAngle )
              pass

    except Exception as exc:
      raise Exception(exc)          
