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


import os, sys, time, getopt

from tools.print_help import help_process_results
from tools.tsv_tools import ReadTSV
from postproc.process_results import process_results
from tools.input_parameters_read import Bunch


# 2017-03-09 EA and JD: Process results in current form takes a data object which needs to be created, 
#   So we're importing "Bunch" and trying to create it on the fly.

# Make sure prints come out straight away
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
time_start = time.time()


if __name__ == "__main__":
    data = {}
    data['output_name'] = "DIC"
    data['cc_threshold'] = None
    data['calculate_strain'] = True
    data['saveTIFF'] = True
    data['saveRAW'] = False
    data['saveVTK'] = False
    data['kinematics_median_filter'] = 0
    data['remove_outliers_filter_size']         = 0 
    data['remove_outliers_threshold']          = 2 
    data['remove_outliers_absolut_threshold']   = False 
    data['remove_outliers_filter_high']         = True
    data['pixel_size_ratio'] = 1
    data['image_centre'] = "none"
    data['strain_mode'] = "largeStrains"
    
    # 2015-04-23 EA: adding defaults for kinematics output
    data['saveDispl']    = True
    data['saveRot']      = True
    data['saveRotFromStrain'] = False
    data['saveError']    = True
    data['saveCC']       = True
    data['saveMask']     = True
    data['saveStrain']   = [ False, False, False, False, False, False, True, True ]
    data['images_2D']    = False


    argv = sys.argv[1:]
    if len(argv) == 0:
        help_process_results()
        sys.exit(2)

    try:
        opts, args = getopt.gnu_getopt(argv,"hp:o:d:c:RTV",[ "prefix=", "output_name=" "dir-out=", "cc-threshold=", \
                                    "no-strain","kinematics_median_filter=","correct_pixel_size=", \
                                    "strain_mode=", "saveRAW", "saveTIFF", "saveVTK" ])
    except getopt.GetoptError as e:
        print (str(e))
        help_process_results()
        sys.exit(2)

    if len(args) != 1:
        help_process_results()
        sys.exit(2)

    file_kinematics = args[0]
    data['DIR_out'] = os.path.dirname(file_kinematics)
    if not data['DIR_out']: data['DIR_out'] = "."

    for opt, arg in opts:
        if opt == '-h':
            help_process_results()
            sys.exit()
        elif opt in ("-p", "--prefix", "-o", "--output_name"):
            data['output_name'] = arg
        elif opt in ("-T", "--saveTIFF"):
            data['saveTIFF'] = True
        elif opt in ("-R", "--saveRAW"):
            data['saveRAW'] = True
        elif opt in ("-V", "--saveVTK"):
            data['saveVTK'] = True
        elif opt in ("-d", "--dir-out"):
            data['DIR_out'] = arg
        elif opt in ("-c", "--cc-threshold"):
            data['cc_threshold'] = arg
        elif opt in ("--no-strain"):
            data['calculate_strain'] = False
        elif opt in ("--kinematics_median_filter"):
            data['kinematics_median_filter'] = int( float( arg ) )
        elif opt in ("--strain_mode"):
            if arg == "smallStrains" or arg == "largeStrains" or arg == 'tetrahedralStrains' or arg == 'largeStrainsCentred':
                data['strain_mode'] = arg
                print "tomowarp_process_results(): Strain mode {} selected".format( data['strain_mode'] )
        elif opt in ("--correct_pixel_size"):
            exec ("correct_pixel_size ="+arg )
            data['pixel_size_ratio'] = correct_pixel_size[0]
            data['image_centre'] = correct_pixel_size[1:4]


    print "  -> Reading a kinematics field..."
    kinematics = ReadTSV( file_kinematics,  "NodeNumber", [ "Zpos", "Ypos", "Xpos", "Zdisp", "Ydisp", "Xdisp",  "Zrot", "Yrot", "Xrot", "CC", "Error" ], [1,0] ).astype( '<f4' )

    # Create data object
    data = Bunch(data)
    
    process_results(  kinematics, data )
