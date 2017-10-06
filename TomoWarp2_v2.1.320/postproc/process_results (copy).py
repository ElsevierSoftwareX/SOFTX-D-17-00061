# -*- coding: utf-8 -*-
# 2013-08-22 - This test file is supposed to read in a finished, regular subpixel input, and output files.
# 2014-03-13 - Adding a median filter on the kinematics, from Pierre's suggestion

import numpy
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

    #-----------------------------------------------------------------------
    #-  Generate a NaN mask to add to other fields                        --
    #-----------------------------------------------------------------------
    mask = numpy.zeros( cc_field.shape, dtype='<f4' )

    # add the nodes which are error nodes to the mask
    mask[ numpy.where( kinematics[ :, 11 ] != 0 ) ] = numpy.nan


    if data.cc_threshold == "auto":
        # if we have a data.cc_threshold set, add this to the mask
        data.cc_threshold = cc_autothreshold( cc_field )

    if data.cc_threshold == None:
        data.cc_threshold = -1.0 #why do we need this?

    else:
        # if data.cc_threshold != None, calculate and apply mask
        data.cc_threshold = float( data.cc_threshold )
        # ...and mask with data.cc_threshold
        mask[ numpy.where( cc_field < data.cc_threshold ) ] = numpy.nan


    #-----------------------------------------------------------------------
    #-  Done generating the mask...                                       --
    #-----------------------------------------------------------------------
    # Clean up the kinematics with the mask
    for i in [ 4,5,6,7,8,9 ]: kinematics[ :, i ] += mask

    # Remove outliers
    if data.remove_outliers_filter_size != None:
      if data.remove_outliers_filter_size > 0:
          print "\tprocess_results: Removing outliers"#%0.1f (3 means ±1)"%( data.kinematics_median_filter )
          try:
            #kinematics[ :, 4:10 ] = data.kinematics_median_filter_fnc( kinematics[ :, 1:4 ], kinematics[ :, 4:10 ], data.kinematics_median_filter )
            [ kinematics[ :, 4:10 ], mask_outliers ] = kinematics_remove_outliers( kinematics[ :, 1:4 ], kinematics[ :, 4:10 ], \
                data.remove_outliers_filter_size, data.remove_outliers_threshold, data.remove_outliers_absolut_threshold, data.remove_outliers_filter_high, data.filter_base_field )
            #mask[ numpy.where(mask_outliers==1) ] = 0
          except Exception as exc:
            print exc.message
            pass

    # filter kinematics...
    if data.kinematics_median_filter != None:
      if data.kinematics_median_filter > 0:
          print "\tprocess_results: Applying a Kinematics Median filter of %0.1f (3 means ±1)"%( data.kinematics_median_filter )
          try:
            kinematics[ :, 4:10 ] = kinematics_median_filter_fnc( kinematics[ :, 1:4 ], kinematics[ :, 4:10 ], data.kinematics_median_filter )
          except Exception as exc:
            print exc.message
            pass

    if data.pixel_size_ratio != 1:
      if data.image_centre is not None:
          kinematics = correct_pixel_size_changing( kinematics, data.pixel_size_ratio, data.image_centre )
      else:
          raise Exception('Image centre needed to correct pixel size ratio')

    print "  -> Writing output files to %s/%s..."%( data.DIR_out, data.output_name )

    # 2015-01-27 EA and ET: TODO: These could be optional one day...
    if data.saveTIFF:
      if data.saveError: imsave( data.DIR_out + "/%s-error-field-%04ix%04ix%04i.tif"%( data.output_name, len(nodes_x), len(nodes_y), len(nodes_z) ), kinematics[ :, 11 ].reshape( ( len(nodes_z), len(nodes_y), len(nodes_x) ) ).astype( '<f4' ) )
      if data.saveCC:    imsave( data.DIR_out +    "/%s-cc-field-%04ix%04ix%04i.tif"%( data.output_name, len(nodes_x), len(nodes_y), len(nodes_z) ),            cc_field.reshape( ( len(nodes_z), len(nodes_y), len(nodes_x) ) ).astype( '<f4' ) )
      if data.saveMask:  imsave( data.DIR_out +        "/%s-mask-%04ix%04ix%04i.tif"%( data.output_name, len(nodes_x), len(nodes_y), len(nodes_z) ),                mask.reshape( ( len(nodes_z), len(nodes_y), len(nodes_x) ) ).astype( '<f4' ) )
    if data.saveRAW:
      # Save RAW Files
      if data.saveError: kinematics[ :, 11 ].astype( '<f4' ).tofile( data.DIR_out + "/%s-error-field-%04ix%04ix%04i.raw"%( data.output_name, len(nodes_x), len(nodes_y), len(nodes_z)) )
      if data.saveCC:    cc_field.astype( '<f4' ).tofile(           data.DIR_out + "/%s-cc-field-%04ix%04ix%04i.raw"%( data.output_name, len(nodes_x), len(nodes_y), len(nodes_z)) )
      if data.saveMask:   mask.astype( '<f4' ).tofile(               data.DIR_out + "/%s-mask-%04ix%04ix%04i.raw"%( data.output_name, len(nodes_x), len(nodes_y), len(nodes_z)) )
    if data.saveVTK:
      #print "\tprocess_results:VTK output not implemented yet"
      headersEndPosition = WriteVTK_headers( data.DIR_out + "/%s.vtk"%( data.output_name ), kinematics[ :, 1:4 ], mask )
      if data.saveCC: WriteVTK_data( data.DIR_out + "/%s.vtk"%( data.output_name ), 'correlation_coefficient', cc_field,          mask, 'POINT_DATA' )
      if data.saveError:
        WriteVTK_headers( data.DIR_out + "/%s_errors.vtk"%( data.output_name ), kinematics[ :, 1:4 ] )
        WriteVTK_data( data.DIR_out + "/%s_errors.vtk"%( data.output_name ), 'error'                  , kinematics[ :, 11 ], [], 'POINT_DATA')

    if data.saveDispl:
      if data.saveTIFF:
        if not data.images_2D: imsave( data.DIR_out + "/%s-z-field-%04ix%04ix%04i.tif"%(  data.output_name, len(nodes_x), len(nodes_y), len(nodes_z)),     kinematics[ :, 4 ].reshape( ( len(nodes_z), len(nodes_y), len(nodes_x) ) ).astype( '<f4' ) )
        imsave( data.DIR_out + "/%s-y-field-%04ix%04ix%04i.tif"%(  data.output_name, len(nodes_x), len(nodes_y), len(nodes_z)),     kinematics[ :, 5 ].reshape( ( len(nodes_z), len(nodes_y), len(nodes_x) ) ).astype( '<f4' ) )
        imsave( data.DIR_out + "/%s-x-field-%04ix%04ix%04i.tif"%(  data.output_name, len(nodes_x), len(nodes_y), len(nodes_z)),     kinematics[ :, 6 ].reshape( ( len(nodes_z), len(nodes_y), len(nodes_x) ) ).astype( '<f4' ) )
      if data.saveRAW:
        # Save RAW Files
        if not data.images_2D: kinematics[ :, 4 ].astype( '<f4' ).tofile( data.DIR_out + "/%s-z-field-%04ix%04ix%04i.raw"%(  data.output_name, len(nodes_x), len(nodes_y), len(nodes_z)) )
        kinematics[ :, 5 ].astype( '<f4' ).tofile( data.DIR_out + "/%s-y-field-%04ix%04ix%04i.raw"%(  data.output_name, len(nodes_x), len(nodes_y), len(nodes_z)) )
        kinematics[ :, 6 ].astype( '<f4' ).tofile( data.DIR_out + "/%s-x-field-%04ix%04ix%04i.raw"%(  data.output_name, len(nodes_x), len(nodes_y), len(nodes_z)) )
      if data.saveVTK:
        #print "\tprocess_results:VTK output not implemented yet"
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

    if data.calculate_strain:
          #try:
              if    data.strain_mode == "smallStrains":
                  [ strain, rot ] = regular_strain_small_strain( kinematics[:,1:4], kinematics[:,4:7] )
                  if data.saveVTK:
                    # resample strain in a regular grid - not implemented yet
                    print "WARNING: saving VTK with mode smallStrains is not implemented yet"
                    data.saveVTK = False

              elif  data.strain_mode == "largeStrains":
                  [ strain, rot ] = regular_strain_large_strain( kinematics[:,1:4], kinematics[:,4:7] )
                  if data.saveVTK:
                    # resample strain in a regular grid - not implemented yet
                    print "WARNING: saving VTK with mode largeStrains is not implemented yet"
                    data.saveVTK = False
              elif  data.strain_mode == "largeStrainsCentred":
                  [ strain, rot ] = regular_strain_large_strain_centred( kinematics[:,1:4], kinematics[:,4:7], 1 )
                  if data.saveVTK:
                    # resample strain in a regular grid - not implemented yet
                    print "WARNING: saving VTK with mode largeStrains is not implemented yet"
                    data.saveVTK = False

              elif  data.strain_mode == "tetrahedralStrains":
                  [ strain, rot, connectivity, coordinates ] = tetrahedral_elements_strain( kinematics[:,1:4], kinematics[:,4:7], mask = mask )

                  print "max strain = ", strain.max()
                  print "coordinates.shape = ",coordinates.shape
                  if data.saveTIFF or data.saveRAW:
                    ## resample strain in a regular grid - not implemented yet
                    #print "WARNING: saving TIFF or RAW with mode tetrahedralStrains is not implemented yet"
                    #data.saveTIFF = False
                    #data.saveRAW = False
                    
                    interpolate_strain = True
               


              strain = strain.astype( '<f4' )
              rot    = rot.astype(    '<f4' )

              ## Extract strain tensor components
              if len(strain.shape) == 5 :
                  zz = numpy.array( strain[ :, :, :, 0, 0 ] )
                  zy = numpy.array( strain[ :, :, :, 0, 1 ] )
                  zx = numpy.array( strain[ :, :, :, 0, 2 ] )
                  yy = numpy.array( strain[ :, :, :, 1, 1 ] )
                  yx = numpy.array( strain[ :, :, :, 1, 2 ] )
                  xx = numpy.array( strain[ :, :, :, 2, 2 ] )
                  dimZ = strain.shape[0]
                  dimY = strain.shape[1]
                  dimX = strain.shape[2]
              elif len(strain.shape) == 3 :
                  zz = numpy.array( strain[ :, 0, 0 ] )
                  zy = numpy.array( strain[ :, 0, 1 ] )
                  zx = numpy.array( strain[ :, 0, 2 ] )
                  yy = numpy.array( strain[ :, 1, 1 ] )
                  yx = numpy.array( strain[ :, 1, 2 ] )
                  xx = numpy.array( strain[ :, 2, 2 ] )



              if data.saveVTK:
                #print "\tprocess_results:VTK output not implemented yet"
                WriteVTK_maesh( data.DIR_out + "/%s.vtk"%( data.output_name ), connectivity, headersEndPosition )
                WriteVTK_data( data.DIR_out + "/%s.vtk"%( data.output_name ), '', [], data_type = 'CELL_DATA', nPoints = len( connectivity ) )
                if data.saveStrain[0]: WriteVTK_data( data.DIR_out + "/%s.vtk"%( data.output_name ), 'strain_zz', zz )
                if data.saveStrain[1]: WriteVTK_data( data.DIR_out + "/%s.vtk"%( data.output_name ), 'strain_zy', zy )
                if data.saveStrain[2]: WriteVTK_data( data.DIR_out + "/%s.vtk"%( data.output_name ), 'strain_zx', zx )
                if data.saveStrain[3]: WriteVTK_data( data.DIR_out + "/%s.vtk"%( data.output_name ), 'strain_yy', yy )
                if data.saveStrain[4]: WriteVTK_data( data.DIR_out + "/%s.vtk"%( data.output_name ), 'strain_yx', yx )
                if data.saveStrain[5]: WriteVTK_data( data.DIR_out + "/%s.vtk"%( data.output_name ), 'strain_xx', xx )
                if data.saveStrain[6]:
                    # Volumetric Strain is the trace
                    volumetric_strain     = zz + yy + xx
                    WriteVTK_data( data.DIR_out + "/%s.vtk"%( data.output_name ), 'vol_strain', volumetric_strain )
                if data.saveStrain[7]:
                    # Steve's Maximum Shear Strain, see: Ando (2013) Phd, and Hall et al. 2009
                    maximum_shear_strain  = ( 1/3.0 ) * numpy.sqrt( 2*( xx-yy )**2  +  2*(xx-zz)**2  +  2*(yy-zz)**2 + \
                                                                    3*yx**2         +  3*zx**2       +  3*zy**2 )
                    WriteVTK_data( data.DIR_out + "/%s.vtk"%( data.output_name ), 'max_shear', maximum_shear_strain )
                    
              if interpolate_strain:
                    print "Interpolation strain data into a regular grid to save TIF/RAW (This can take some time...)",
                    zz_int = numpy.ones_like(mask)*numpy.nan
                    zy_int = numpy.ones_like(mask)*numpy.nan
                    zx_int = numpy.ones_like(mask)*numpy.nan
                    yy_int = numpy.ones_like(mask)*numpy.nan
                    yx_int = numpy.ones_like(mask)*numpy.nan
                    xx_int = numpy.ones_like(mask)*numpy.nan
                    zz_int[numpy.where(~numpy.isnan(mask))] = griddata( coordinates, zz, kinematics[numpy.where(~numpy.isnan(mask)),1:4] )
                    zy_int[numpy.where(~numpy.isnan(mask))] = griddata( coordinates, zy, kinematics[numpy.where(~numpy.isnan(mask)),1:4] )
                    zx_int[numpy.where(~numpy.isnan(mask))] = griddata( coordinates, zx, kinematics[numpy.where(~numpy.isnan(mask)),1:4] )
                    yy_int[numpy.where(~numpy.isnan(mask))] = griddata( coordinates, yy, kinematics[numpy.where(~numpy.isnan(mask)),1:4] )
                    yx_int[numpy.where(~numpy.isnan(mask))] = griddata( coordinates, yx, kinematics[numpy.where(~numpy.isnan(mask)),1:4] )
                    xx_int[numpy.where(~numpy.isnan(mask))] = griddata( coordinates, xx, kinematics[numpy.where(~numpy.isnan(mask)),1:4] )
                    zz =  zz_int.reshape( ( len( nodes_z ), len( nodes_y ), len( nodes_x ) ) )
                    zy =  zy_int.reshape( ( len( nodes_z ), len( nodes_y ), len( nodes_x ) ) )
                    zx =  zx_int.reshape( ( len( nodes_z ), len( nodes_y ), len( nodes_x ) ) )
                    yy =  yy_int.reshape( ( len( nodes_z ), len( nodes_y ), len( nodes_x ) ) )
                    yx =  yx_int.reshape( ( len( nodes_z ), len( nodes_y ), len( nodes_x ) ) )
                    xx =  xx_int.reshape( ( len( nodes_z ), len( nodes_y ), len( nodes_x ) ) )
                    #zz = re_intsampling_irregular_grid( zz, coordinates )
                    #zy = resampling_irregular_grid( zy, coordinates )
                    #zx = resampling_irregular_grid( zx, coordinates )
                    #yy = resampling_irregular_grid( yy, coordinates )
                    #yx = resampling_irregular_grid( yx, coordinates )
                    #xx = resampling_irregular_grid( xx, coordinates )
                    dimZ = zz.shape[0]
                    dimY = zz.shape[1]
                    dimX = zz.shape[2]
                    #print "Warning: Strain not in a regular grid. Can not write TIFF"
                    
              if data.saveTIFF:
                if data.saveStrain[0]: imsave( data.DIR_out + "/%s-strain_zz-field-%04ix%04ix%04i.tif"%( data.output_name, dimX, dimY, dimZ), zz.astype( '<f4' ) )
                if data.saveStrain[1]: imsave( data.DIR_out + "/%s-strain_zy-field-%04ix%04ix%04i.tif"%( data.output_name, dimX, dimY, dimZ), zy.astype( '<f4' ) )
                if data.saveStrain[2]: imsave( data.DIR_out + "/%s-strain_zx-field-%04ix%04ix%04i.tif"%( data.output_name, dimX, dimY, dimZ), zx.astype( '<f4' ) )
                if data.saveStrain[3]: imsave( data.DIR_out + "/%s-strain_yy-field-%04ix%04ix%04i.tif"%( data.output_name, dimX, dimY, dimZ), yy.astype( '<f4' ) )
                if data.saveStrain[4]: imsave( data.DIR_out + "/%s-strain_yx-field-%04ix%04ix%04i.tif"%( data.output_name, dimX, dimY, dimZ), yx.astype( '<f4' ) )
                if data.saveStrain[5]: imsave( data.DIR_out + "/%s-strain_xx-field-%04ix%04ix%04i.tif"%( data.output_name, dimX, dimY, dimZ), xx.astype( '<f4' ) )
                if data.saveStrain[6]:
                    volumetric_strain     = zz + yy + xx
                    imsave( data.DIR_out + "/%s-vol_strain-field-%04ix%04ix%04i.tif"%( data.output_name, dimX, dimY, dimZ), volumetric_strain.astype( '<f4' ) )
                if data.saveStrain[7]:
                    # Steve's Maximum Shear Strain, see: Ando (2013) Phd, and Hall et al. 2009
                    maximum_shear_strain  = ( 1/3.0 ) * numpy.sqrt( 2*( xx-yy )**2  +  2*(xx-zz)**2  +  2*(yy-zz)**2 + \
                                                                    3*yx**2         +  3*zx**2       +  3*zy**2 )
                    imsave( data.DIR_out + "/%s-maximum_shear_strain-field-%04ix%04ix%04i.tif"%( data.output_name, dimX, dimY, dimZ), maximum_shear_strain.astype( '<f4' ) )
                    
              if data.saveRAW:
                # Save RAW Files
                if data.saveStrain[0]: zz.astype( '<f4' ).tofile( data.DIR_out + "/%s-strain_zz-field-%04ix%04ix%04i.raw"%( data.output_name, dimX, dimY, dimZ) )
                if data.saveStrain[1]: zy.astype( '<f4' ).tofile( data.DIR_out + "/%s-strain_zy-field-%04ix%04ix%04i.raw"%( data.output_name, dimX, dimY, dimZ) )
                if data.saveStrain[2]: zx.astype( '<f4' ).tofile( data.DIR_out + "/%s-strain_zx-field-%04ix%04ix%04i.raw"%( data.output_name, dimX, dimY, dimZ) )
                if data.saveStrain[3]: yy.astype( '<f4' ).tofile( data.DIR_out + "/%s-strain_yy-field-%04ix%04ix%04i.raw"%( data.output_name, dimX, dimY, dimZ) )
                if data.saveStrain[4]: yx.astype( '<f4' ).tofile( data.DIR_out + "/%s-strain_yx-field-%04ix%04ix%04i.raw"%( data.output_name, dimX, dimY, dimZ) )
                if data.saveStrain[5]: xx.astype( '<f4' ).tofile( data.DIR_out + "/%s-strain_xx-field-%04ix%04ix%04i.raw"%( data.output_name, dimX, dimY, dimZ) )
                if data.saveStrain[6]:
                    volumetric_strain     = zz + yy + xx
                    volumetric_strain.astype( '<f4' ).tofile( data.DIR_out + "/%s-vol_strain-field-%04ix%04ix%04i.raw"%( data.output_name, dimX, dimY, dimZ) )
                if data.saveStrain[7]:
                    # Steve's Maximum Shear Strain, see: Ando (2013) Phd, and Hall et al. 2009
                    maximum_shear_strain  = ( 1/3.0 ) * numpy.sqrt( 2*( xx-yy )**2  +  2*(xx-zz)**2  +  2*(yy-zz)**2 + \
                                                                    3*yx**2         +  3*zx**2       +  3*zy**2 )
                    maximum_shear_strain.astype( '<f4' ).tofile( data.DIR_out + "/%s-max_shear-field-%04ix%04ix%04i.raw"%( data.output_name, dimX, dimY, dimZ) )

                            
              if data.saveRotFromStrain:
                # 2014-10-13 EA: calc     ulation of rotation
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
                        print "Warning: Strain not in a regular grid. Can not write TIFF"
                if data.saveRAW:
                    # Save RAW Files
                    if len(strain.shape) == 5 :
                        RotAngle.astype( '<f4' ).tofile( data.DIR_out + "/%s-rot_angle-%04ix%04ix%04i.raw"%( data.output_name, dimX, dimY, dimZ) )
                    else:
                        print "Warning: Strain not in a regular grid. Can not write RAW"
                if data.saveVTK:
                    #print "\tprocess_results:VTK output not implemented yet"
                    #WriteVTK_data( data.DIR_out + "/%s.vtk"%( data.output_name ), 'rot_angle', RotAngle )
                    pass


          #except Exception as exc:
              #print exc
              #pass
