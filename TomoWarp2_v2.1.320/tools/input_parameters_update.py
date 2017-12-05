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
2015-04-28 Edward Ando -- This function updates the last parameters in case they cannot be
  done in input_parameters by default (for example the grey_thresholds that are set to inf
  cannot be written and read as such. This will also allow the number of workers to remain
  saved as auto and loaded now).
  
The input to this file must be the Packaged (in lists)version of data
"""

import numpy, logging

from cpu_set import cpu_set_count

def input_parameters_update( data ):
    # 2015-03-02 EA: Adding an automatic measurement of number of available CPUs
    #   Using the cpu_set.py file written by Rémi, which is able to pick up the number of
    #   CPUs that are given by OAR
    # 2015-04-01 EA: Changing cpuset to cpu_set to avoid a python conflict
    # 2015-04-09 EA: Simple test shows that nWorkers = numberOfCPUs is faster than numberOfCPUs - 1
    if data.nWorkers == "auto":
        numberOfCPUs = cpu_set_count()
        try: logging.log.info("input_parameters_setup(): Number of CPUs %i"%( numberOfCPUs ))
        except: print "input_parameters_setup(): Number of CPUs %i"%( numberOfCPUs )

        data.nWorkers = max( 1, numberOfCPUs )


    # memLimitMB has to be checked here because if set to numpy.inf it will become inf during printing
    data.memLimitSlices = min(data.image_slices_extent[0,1], data.image_slices_extent[1,1] )
    if data.memLimitMB is not None:
        # the images are converter in 32 bit in load_slices
        memSlice1 = data.image_size[0,-2] * data.image_size[0,-1] * 4 
        memSlice2 = data.image_size[1,-2] * data.image_size[1,-1] * 4 
        #memSlice1 = data.image_size[0,-2] * data.image_size[0,-1] * int( data.image_data_format[-1] )
        #memSlice2 = data.image_size[1,-2] * data.image_size[1,-1] * int( data.image_data_format[-1] )
        data.memLimitSlices =  min( data.memLimitSlices, data.memLimitMB  * 1024 * 1024  / ( memSlice1 + memSlice2 ) )

        try:
          logging.log.info("memory limit:                  %.1f MB"%(data.memLimitMB)        )
          logging.log.info("memory of one slice of image1: %.1f MB"%(memSlice1 / 1024 / 1024))
          logging.log.info("memory of one slice of image2: %.1f MB"%(memSlice2 / 1024 / 1024))
        except:
          print "memory limit:                  %.1f MB"%(data.memLimitMB)        
          print "memory of one slice of image1: %.1f MB"%(memSlice1 / 1024 / 1024)
          print "memory of one slice of image2: %.1f MB"%(memSlice2 / 1024 / 1024)


    # grey thresholds -- update them if they're None.
    if data.grey_threshold[0] == None: data.grey_threshold[0] = -numpy.inf
    if data.grey_threshold[1] == None: data.grey_threshold[1] =  numpy.inf

    # Range of error from prior update if they're None
    if data.errorLimit[0] == None: data.errorLimit[0] = -numpy.inf
    if data.errorLimit[1] == None: data.errorLimit[1] =  numpy.inf