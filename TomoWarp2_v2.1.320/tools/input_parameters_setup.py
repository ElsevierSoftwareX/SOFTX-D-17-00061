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
2015-01-26 this function takes dirty data and creates all the necessary parameters
"""

import sys, time, numpy

def input_parameters_setup( data ):

    # Defining a list of REQUIRED parameters (there is not default for these parameters)
    list_parameters = [ "DIR_image1",
                        "DIR_image2",
                        "correlation_window",
                        "search_window",
                        ]

    # Checking that all required parameters are given
    for opt in list_parameters:
      if not( opt in data) or any( x is None for x in [data[opt]] ):
        raise Exception('Error: Missing input parameter: %s'%(opt))

    # Setting default value for max_search_window if not found in inputfile
    if not( 'max_search_window' in data ): data['max_search_window'] = data['search_window']

    if type( data.search_window ) == int:
        data.search_window = [ [ -data.search_window, data.search_window ], [ -data.search_window, data.search_window ], [ -data.search_window, data.search_window] ]
    if type( data.max_search_window ) == int:
        data.max_search_window = [ [ -data.max_search_window, data.max_search_window], [ -data.max_search_window, data.max_search_window ], [ -data.max_search_window, data.max_search_window ] ]

    # If node_spacing is an integer it define a tuple
    try:
      if type( data.node_spacing ) == int:
        data.node_spacing = [ data.node_spacing, data.node_spacing, data.node_spacing ]
    except:
      pass

    # Check that either node_spacing or prior_file are defined
    if data.prior_file is None:
      if all( i is None for i in data.node_spacing):
        raise Exception('Error: Neither node_spacing nor prior_file are defined ')
    # If new_node_spacing is an integer it define a tuple
    try:
      if type( data.new_node_spacing ) == int:
        data.new_node_spacing = [ data.new_node_spacing, data.new_node_spacing, data.new_node_spacing ]
    except:
      pass

    # 2014-03-19 -- adding the same for the correlation_window
    try:
      if type( data.correlation_window ) == int:
        data.correlation_window = [ data.correlation_window, data.correlation_window, data.correlation_window ]
    except:
      pass

    # 2014-03-19 -- adding the same for the search_step
    try:
      if type( data.search_step ) == int:
        data.search_step = [ data.search_step, data.search_step, data.search_step ]
    except:
      pass

    # 2014-05-22 -- making sure that if we have the RAW file defined, that data_format is also defined
    # 2014-06-20 -- we also need image_raw_size IF we have some crop values set.
    if data['image_format'] == 'RAW':
      try:
        data['image_data_format']
      except NameError:
        raise  Exception( "parameters_definition(): \'image_format\' was set to \'RAW\', but \'image_data_format\' was not set." )

    if data.image_1_size  == None: data.image_1_size  = [None, None]
    if data.image_2_size  == None: data.image_2_size  = [None, None]
    if data.ROI_corners   == None: data.ROI_corners = [[None,None,None],[None,None,None]]

        # 2014-07-25 -- formal parameters for mesh refinement for pierre's calculations.
    try:
        data.node_spacing_refined
        # if a refined node spacing is define, first turn it into a tuple, if it is an int
        if type( data.node_spacing_refined ) == int:
            data.node_spacing_refined = [ data.node_spacing_refined, data.node_spacing_refined, data.node_spacing_refined ]
        # if a node spacing refined is defined, then check that a refined search window is also given.
        # if so use it, otherwise, set to +-2 in each direction
        try:
          data.search_window_refined
          pass
        except:
          data.search_window_refined = [ [-2,2], [-2,2], [-2,2] ]
    except:
      pass

    # 2015-01-26: If data.name_prefix is set, update output filename
    if data.name_prefix != "" and data.output_name == "":
        data.output_name = "%s-%s-%s-ns=%i"%( data.name_prefix, data.name_1, data.name_2, data.node_spacing[1] )

    # 2015-03-19 EA: If all the components of data['saveStrain'] are false, set calculate_strain to False
    if numpy.array( data.saveStrain ).sum() == 0:
        data.calculate_strain = False

    if not data.subpixel_mode[2]: data.saveRot = False

    # 2015-04-28 EA: Logic for grey_threshold:
    data['grey_threshold'] = [ data['grey_low_threshold'], data['grey_high_threshold'] ]

    # 2015-10-13 ET:
    data['errorLimit'] = [ data['errorLowLimit'], data['errorHighLimit'] ]

    data.image_slices_extent        = numpy.array([ data.image_1_slices_extent, data.image_2_slices_extent])
    data.image_digits               = numpy.array([ data.image_1_digits, data.image_2_digits ] )
    data.DIR_image                  = numpy.array([ data.DIR_image1, data.DIR_image2 ])
    data.image_filter               = numpy.array([ data.image_1_filter, data.image_2_filter ]  )
    data.image_size                 = numpy.array([ data.image_1_size, data.image_2_size ]  )


    del data. image_1_slices_extent, data.image_2_slices_extent
    del data.image_1_digits, data.image_2_digits
    del data.DIR_image1, data.DIR_image2
    del data.image_1_filter, data.image_2_filter
    del data.image_1_size, data.image_2_size
    del data.grey_low_threshold, data.grey_high_threshold


    return data
