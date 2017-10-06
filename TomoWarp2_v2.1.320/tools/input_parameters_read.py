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

# Date created: 2013-12-16

# Functions that read parameters from an input file and set the default values

import os, numpy
from os.path import expanduser
from print_variable import pv


def required_parameters( data={} ):

    home = expanduser( "~" )

    if not ( 'DIR_image1'         in data ): data['DIR_image1']         =  home
    if not ( 'DIR_image2'         in data ): data['DIR_image2']         =  home
    if not ( 'DIR_out'            in data ): data['DIR_out']            =  home
    if not ( 'correlation_window' in data ): data['correlation_window'] =  None
    if not ( 'search_window'      in data ): data['search_window']      =  None
    if not ( 'node_spacing'       in data ): data['node_spacing']       =  None

    return data



def default_parameters( data={} ):

    # Setting of default values for optional parameters in the dictionary "data"
    data['name_prefix']              = ""
    data['name_1']                   = ""
    data['name_2']                   = ""
    data['output_name']              = "DIC"
    data['node_spacing']             = None
    data['image_format']             = "auto"
    data['image_ext']                = ""
    data['image_1_digits']           = None
    data['image_2_digits']           = None
    data['image_1_filter']           = ""
    data['image_2_filter']           = ""
    data['image_data_format']        = None
    data['image_1_size']             = None
    data['image_2_size']             = None
    data['images_2D']                = False
    data['jointFiles']               = True
    data['log2file']                 = True

    data['ROI_corners']              = None
    data['image_1_slices_extent']    = [None, None]
    data['image_2_slices_extent']    = [None, None]

    data['grey_low_threshold']       = None
    data['grey_high_threshold']      = None

    data['cc_percent']               = False           # This one is to show the CC between [ 0, 100% ] rather than [ 0, 1 ]
    data['printPercent']             = 1.0

    data['prior_file']               = None
    data['priorSmoothing']           = 3
    data['prior_cc_threshold']       = 0
    data['errorLowLimit']            = None
    data['errorHighLimit']           = None
    data['usePriorCoordinates']      = False

    data['memLimitMB']               = None
    data['nWorkers']                 = "auto"

    data['cc_threshold']             = 0
    data['kinematics_median_filter'] = 0
    data['remove_outliers_filter_size']         = 0
    data['remove_outliers_threshold']           = 2
    data['remove_outliers_absolut_threshold']   = False
    data['remove_outliers_filter_high']         = True
    data['filter_base_field']        = 0

    data['calculate_strain']         = True
    data['pixel_size_ratio']         = 1
    data['image_centre']             = None
    data['strain_mode']              = "largeStrains"
    data['saveDispl']                = True
    data['saveRot']                  = True
    data['saveRotFromStrain']        = False
    data['saveCC']                   = True
    data['saveError']                = True
    data['saveMask']                 = False
    data['saveStrain']               = [ False, False, False, False, False, False, True, True ]
    data['saveTIFF']                 = True
    data['saveRAW']                  = False
    data['saveVTK']                  = False

    data['subpixel_mode']            = [ True,  False,  False ]  # [ CC,  II_translation,  II_rotation ]
    data['subpixel_CC_max_refinement_step']       = 2
    data['subpixel_CC_refinement_step_threshold'] = 0.0001
    data['subpixel_CC_max_refinement_iterations'] = 15
    data['subpixel_II_interpolationMode']         = "map_coordinates"
    data['subpixel_II_interpolation_order']       = 1
    data['subpixel_II_optimisation_mode']         = "Powell"

    # The following parameters were used by TomoWarp 2.0 (not implemented yet in the last version)
    #data['new_node_spacing']         = None
    #data['search_step']              = 1
    #data['refine_mode']              = False
    #data['resume_z_position']        = None
    #data['z_position']               = None

    return data




def input_parameters_read( inputfile, data_input={} ):
    # This function MUST RETURN SEPARATED VARIABLES -- it will unpack if values are packed into lists.

    data = default_parameters()
    
    # Reading the parameters in the input file
    f=open(inputfile)
    for line in f:
        line = line.rstrip()             # remove the trailing newline
        if ( len(line) != 0 ) and ( line[0] != "#" ):
            opt, arg  = line.split( '=', 1 )
            opt       = opt.split(' ',1)[0]
            arg       = arg.split('#',1)[0]

            # 2015-02-27 EA and QV: matching for "inf" is matching anywhere in the string,
            #   so a filename with "goinfre" gets set to inf. We're going to try to replace this with
            #   an exact match.
            #if 'inf' in arg:
            if arg == 'inf':
                data[opt] = numpy.inf
            elif arg == '-inf':
                data[opt] = -numpy.inf
            else:
                try:
                    data[opt] = eval( arg )
                except SyntaxError:
                    data[opt] = arg                     


    if 'DIR_image' in data.keys():
        data['DIR_image1'] = data['DIR_image'][0]
        data['DIR_image2'] = data['DIR_image'][1]
        del data['DIR_image']

    # ET 2016-05-20: To keep compatibility to old input file ROI_1_corners is used if ROI_corners is not set
    if 'ROI_1_corners' in data.keys() and data['ROI_corners'] is None:
        data['ROI_corners'] = data['ROI_1_corners']
        del data['ROI_1_corners']

    try: 
        data['ROI_corners'][0][0][0]
        data['ROI_corners'] = data['ROI_corners'][0]
    except TypeError:
        pass

    if 'image_digits' in data.keys():
        data['image_1_digits'] = data['image_digits'][0]
        data['image_2_digits'] = data['image_digits'][1]
        del data['image_digits']

    if 'image_filter' in data.keys():
        data['image_1_filter'] = data['image_filter'][0]
        data['image_2_filter'] = data['image_filter'][1]
        del data['image_filter']

    if 'image_size' in data.keys():
        data['image_1_size'] = data['image_size'][0]
        data['image_2_size'] = data['image_size'][1]
        del data['image_size']

    if 'grey_threshold' in data.keys():
        try:
          if len( data['grey_threshold'] ) == 2:
            data['grey_low_threshold']  = data['grey_threshold'][0]
            data['grey_high_threshold'] = data['grey_threshold'][1]
          else:
            # In this case grey threshold has more than two elements, or is a list with one element,
            #   bad input in both cases, reset everything
            data['grey_low_threshold']  = None
            data['grey_high_threshold'] = None

          del data['grey_threshold']
        except:
          # otherwise here grey_threshold is just one variable, default behaviour (it's the low one by default)
          # now check whether grey_low_threshold is set:
          try:
            data['grey_low_threshold']
          except:
            data['grey_low_threshold']  = data['grey_threshold']

          # now check whether grey_high_threshold is set:
          try:
            data['grey_high_threshold']
          except:
            data['grey_high_threshold'] = None
          # All set up -- delete grey_threshold
          del data['grey_threshold']

    if 'errorLimit' in data.keys():
        data['errorLowLimit']  = data['errorLimit'][0]
        data['errorHighLimit'] = data['errorLimit'][01]

    if not ('DIR_out' in data):
        data['DIR_out'] = os.path.dirname(inputfile)

    # Replacing parameters given in the command line
    if 'DIR_out' in data_input: data['DIR_out'] = data_input['DIR_out']
    if 'cc_threshold' in data_input: data['cc_threshold'] = data_input['cc_threshold']
    if 'prior_file' in data_input: data['prior_file'] = data_input['prior_file']
    if 'DIR_image1' in data_input: data['DIR_image1'] = data_input['DIR_image1']
    if 'DIR_image2' in data_input: data['DIR_image2'] = data_input['DIR_image2']
    if 'z_position' in data_input: data['z_position'] = data_input['z_position']
    if 'log2file'   in data_input: data['log2file']   = data_input['log2file']
    if 'jointFiles' in data_input: data['jointFiles'] = data_input['jointFiles']

    # Making "data" a dot-accessible dictionary
    data = Bunch( data )

    return data


class Bunch(dict):
    def __init__(self, kw):
        dict.__init__(self, kw)
        self.__dict__ = self

    def __getstate__(self):
        return self

    def __setstate__(self, state):
        self.update(state)
        self.__dict__ = self
