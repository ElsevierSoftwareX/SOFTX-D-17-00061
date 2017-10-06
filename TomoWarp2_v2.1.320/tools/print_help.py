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

# Date created: 2013-10-03

# Functions that print help for running files


def help_process_results():
  print 'Use: tomowarp_process_results [options] <inputfile>'
  print '  -o  --output_name   output file prefix (Default: "DIC")'
  print '  -p  --prefix        output file prefix (Default: "DIC")'
  print '  -d  --dir-out       output diretcory (Default: directory of the input file)'
  print '  -T  --saveTIFF      save outputs as TIFF files (Default = False)'
  print '  -R  --saveRAW       save outputs as RAW  files (Default = False)'
  print '  -V  --saveVTK       save outputs as VTK  files (Default = False)'
  print '  -c  --cc-threshold  threshold for the correlation coefficient'
  print '                      can be a number, "auto" (Default: none)'
  print '      --no-strain     if specified strains are not calculated'
  print '      --kinematics_median_filter'
  print '                      kinematics are median filtered, with their nearest neighbours.'
  print '                      Smoothed fields are output, and strain is calculated on smoothed fields.'
  print '                      (can improve strain results a lot).'
  print '                      Default = 0, good option = 3 (means one neighbour in each direction).'
  print '      --correct_pixel_size'
  print '                      correction for pixel size changing as:'
  print '                      [pixel_size_ratio, image_centre_z, image_centre_y, image_centre_x]'
  print '      --strain_mode'
  print '                      Whether strains should be calculated in the "largeStrains" or "smallStrains"'
  print '                      or "largeStrainsCentred". "largeStrains" is recommended, and is default'

  
def help_continuum_slices():

  print 'Use: tomowarp_continuum_slices  [options] <inputfile>'
  print '  -p  --prior         prior file path, if empty a new grid is generated (Default: empty)'
  print '  -d  --dir-out       output diretcory (Default: directory of the input file)'
  print '  -c  --cc-threshold  threshold for the correlation coefficient'
  print '                      can be a number, "auto" or "none" (Default: "auto")'
  print '      --dir1          directory of references images'
  print '      --dir2          directory of deformed images'
  print '      --desktop       start a GUI'
  print '  -h                  print this help.'
  print '      --help          with argument "input" print an help on the inputfile'
  print '\nAttention! Parameters defined in inputfile are replaced with values given as options in the command line\n'
  
  
def help_continuum_slices_inputfile():
  print 'The inputfile has to be a text file where parameters are defined as:'
  print '\nparameter_name = parameter_value\n'
  print 'Comments can be added in a new line or after the parameter definition'
  print 'Blank lines are allowed'
  print '\nRequired Parameters:'
  print '  image_1_prefix        '
  print '  image_2_prefix        '
  print '  image_1_zeros         '
  print '  image_2_zeros         '
  print '  correlation_window    '
  print '  search_window         '
  print '  first_image_1_number  '
  print '  first_image_2_number  '
  print '  image_size            '
  print '\nOptional parameters:'
  print '  subpixel_refinement_mode   Can be None or "CC"(Default: None)'
  print '  new_node_spacing           (Default: None)'
  print '  search_step                (Default: 1)'
  print '  EXTRA_PADDING              (Default: 2)'
  print '  max_search_window          (Default: 2 * search_window)'
  print '  number_of_threads          (Default: 1)'
  print '  max_refinement_step        (Default: 2)'
  print '  refinement_step_threshold  (Default: 0.0001)'
  print '  max_refinement_iterations  (Default: 15)'
  print '  image_1_x_crop             (Default: 0)'
  print '  image_1_y_crop             (Default: 0)'
  print '  image_2_x_crop             (Default: 0)'
  print '  image_2_y_crop             (Default: 0)'
  print '  grey_threshold             (Default: 0)'
  print '  refine_mode                boolean variable (Default: False)'
  print '  resume_z_position          (Default: None)/not required'
  print '  node_spacing               (Default: None) Required if prior_file is not defined'
  print '  prior_file                 (Default: None)/not required'
  print '  cc_threshold               Can be a number or "auto" (Default: 0)'
  print '  file_out                   (Default: "sub_pixel_measurement.tsv")'
  print '  DIR_out                    (Default: directory of the input file)'
  print '  DIR_image1                 (it has to be defined either in the inputfile'
  print '                               or as an option in the command line)' 
  print '  DIR_image2                 (it has to be defined either in the inputfile'
  print '                               or as an option in the command line)'
  print '  image_format               (Selects a type of image reader, RAW, EDF, TIFF)'
  print '  image_data_format          REQUIRED if image_format == "RAW" (sets RAW data format with a'
  print '                               numpy-recognisable dtype, e.g., little-endian 32-bit float is \'<f4\')'
  print '  image_raw_size             REQUIRED if image_format == "RAW" and a crop is set'
  print '                               sets the RAW image size with a tuple [y_dim, x_dim]'
  print '  node_spacing_refined       Refined node spacing to use when making a mesh refinement'
  print '  search_window_refined      Refined search window to use when making a mesh refinement'
  print '  cc_percent                 If set to True the correlation coefficient is given in percentage'
  print '  memory_mode      (Default: "FullVolume")'
  print '  memory_size      (Default: None)'
  print '\n'
