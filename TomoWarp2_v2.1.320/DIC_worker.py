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
Worker to pocess nodes one after the other and do pixel_search, refinement, etc...

INPUTS:
  - workerNumber
  - q_nodes to receive info on nodes
  - q_results to comunicate correlation result
  - q_data_requests to ask for data to data_delivery_worker
  - q_data to receive data from data_delivery_worker
  - "data" structure
"""

import time
import numpy
import logging

# This is our pixel_search C-code
from pixel_search.c_code import pixel_search
from sub_pixel.cc_interpolation import cc_interpolation_local, \
    cc_interpolation_local_2D
from sub_pixel.image_interpolation_translation_rotation import \
    image_interpolation_translation_rotation
#from print_variable import pv


def DIC_worker( workerNumber, q_nodes, q_results, q_data_requests, q_data, data ):

    time.sleep( 1 )
    try: logging.log.info("DIC_worker %i: Started up"%( workerNumber ))
    except: print "DIC_worker %i: Started up"%( workerNumber )

    while True:
        #time.sleep( 1 )
        setupMessage = q_nodes.get()

        if setupMessage[0] == "STOP":
            try: logging.log.info("DIC_worker %i: Got a request to stop, quitting."%( workerNumber ))
            except: "DIC_worker %i: Got a request to stop, quitting."%( workerNumber )
            return -1

        else:
            # Treat this node...
            nodeNumber  = setupMessage[0]
            extent      = setupMessage[1]

            # Make a data request to data_delivery_worker, just with worker number data extents
            q_data_requests.put( [ "DataRequest", workerNumber, extent ] )

            # Get message back from data_delivery_worker, hopefully containing image data:
            dataMessage = q_data.get()

            # Define these high up to be able to return them, even if everything goes wrong.
            error   = 0
            cc      = 0.0
            nodeDisplacement = numpy.array( [ 0.0, 0.0, 0.0 ] )
            nodeDispSubpixel = numpy.array( [ 0.0, 0.0, 0.0 ] )
            nodeRotSubpixel  = numpy.array( [ 0.0, 0.0, 0.0 ] )

            if  dataMessage[0] == "Error":
                # Error fetching the data from the data_delivery_worker, return nothing but a data error (#1)
                error += 1

            elif dataMessage[0] == "Data":
                # Reinitialise all important variables
                im1     = dataMessage[1]
                im1Dim  = im1.shape
                im2     = dataMessage[2]
                im2Dim  = im2.shape

                # Get images out of the reply from data_delivery_worker
                #   NOTE: im2 should be bigger than im1 if the search range is not zero. (it is checked in data_delivery_worker)

                # 2015-01-19 EA: Check that the mean value of the reference im1 is greater than the grey_threshold
                if im1.mean() < data.grey_threshold[0] or im1.mean() > data.grey_threshold[1]:
                    # outside the range of interesting gray values, don't correlate, return error = 2
                    error += 2

                else:
                    # we're within grey threshold... continue...

                    # --- Run C-code PIXEL SEARCH ---
                    # get displacement of this node from returns...

                    returns = pixel_search.pixel_search( im1, im2, 4 )
                    # -------------------------------

                    nodeDisplacement = returns[0:3]
                    cc               = returns[3]


                    # We're doing a subpixel search -- either CC or Image Interpolation!
                    if any( data.subpixel_mode ):

                        # ==================================
                        # === data check for CC and II-T ===
                        # ==================================

                        # Both CC and translation-only image interpolation take im2 = im1+-1 pixel, so prepare it in case we're in this case:
                        if ( data.subpixel_mode[0] ) or ( data.subpixel_mode[1] and not data.subpixel_mode[2] ):
                            cornerOffset = 1
                            im2Pm1 = im2[  int(nodeDisplacement[0])-cornerOffset:int(nodeDisplacement[0])+im1Dim[0]+cornerOffset,\
                                           int(nodeDisplacement[1])-cornerOffset:int(nodeDisplacement[1])+im1Dim[1]+cornerOffset,\
                                           int(nodeDisplacement[2])-cornerOffset:int(nodeDisplacement[2])+im1Dim[2]+cornerOffset  ]

                            # === Step 1: Measure the dimensions of image 1 ===
                            im2Pm1Dim = numpy.array( im2Pm1.shape )
                            # 2015-12-17 EA: adding Check for 2D images, the z-dimension will always be 1...
                            if im1.shape[0] == 1 and im2.shape[0] == 1:
                                # then we're dealing with a 2D image
                                if ( im2Pm1Dim[1] - im1Dim[1] ) != 2*cornerOffset or  ( im2Pm1Dim[2] - im1Dim[2] ) != 2*cornerOffset:
                                    # We don't have enough data (i.e. +- 1 px) to do a CC interpolation, quit.
                                    error           += 32

                            else:
                                # We're in 3D
                                if not all( ( im2Pm1Dim - im1Dim ) == 2*cornerOffset ):
                                    # We don't have enough data (i.e. +- 1 px) to do a CC interpolation, quit.
                                    error           += 32

                        # ==================================


                        # ==================================
                        # === data check for II-Rotation ===
                        # ==================================
                        # Also check the data extents for the rotation...
                        if ( data.subpixel_mode[1] and data.subpixel_mode[2] ):
                            cornerOffsetRot = int( ( ( numpy.sqrt(3) * max( im1Dim ) ) - max( im1Dim ) + 1 ) / 2.0 )

                            im2Rot = im2[  nodeDisplacement[0]-cornerOffsetRot:nodeDisplacement[0]+im1Dim[0]+cornerOffsetRot,\
                                           nodeDisplacement[1]-cornerOffsetRot:nodeDisplacement[1]+im1Dim[1]+cornerOffsetRot,\
                                           nodeDisplacement[2]-cornerOffsetRot:nodeDisplacement[2]+im1Dim[2]+cornerOffsetRot  ]

                            # === Step 1: Measure the dimensions of image 1 ===
                            im2RotDim = numpy.array( im2Rot.shape )

                            if not all( ( im2RotDim - im1Dim ) == 2*cornerOffsetRot ):
                                # We don't have enough data (i.e. +- 1 px) to do a CC interpolation. asking for more data

                                newExtent = extent.copy()
                                newExtent[1,0] = [  nodeDisplacement[0]-cornerOffsetRot+extent[1,0,0], \
                                                    nodeDisplacement[1]-cornerOffsetRot+extent[1,0,1], \
                                                    nodeDisplacement[2]-cornerOffsetRot+extent[1,0,2] ]

                                newExtent[1,1] = [  nodeDisplacement[0]+cornerOffsetRot+extent[1,0,0]+im1Dim[0], \
                                                    nodeDisplacement[1]+cornerOffsetRot+extent[1,0,1]+im1Dim[1], \
                                                    nodeDisplacement[2]+cornerOffsetRot+extent[1,0,2]+im1Dim[2] ]

                                # Make a data request to data_delivery_worker, just with worker number data extents
                                q_data_requests.put( [ "DataRequest", workerNumber, newExtent ] )
                                dataMessage = q_data.get()

                                if  dataMessage[0] == "Error":
                                    # Error fetching the data from the data_delivery_worker, return nothing but a data error (#1)
                                    error += 1

                                elif dataMessage[0] == "Data":
                                    im2Rot     = dataMessage[2]
                                    im2RotDim  = numpy.array( im2Rot.shape )

                                    if not all( ( im2RotDim - im1Dim ) == 2*cornerOffsetRot ):
                                        #Got more data but it was the wrong shape
                                        error           += 32

                        # ==================================

                        # ===========================
                        # === CC INTERPOLATION ======
                        # ===========================
                        # OK, let's do the CC interpolation if we've been asked to do it!
                        if data.subpixel_mode[0] and error == 0:

                            if im1.shape[0] == 1 and im2.shape[0] == 1:
                                returns = cc_interpolation_local_2D(  im1, im2Pm1, \
                                                                      data.subpixel_CC_refinement_step_threshold, \
                                                                      data.subpixel_CC_max_refinement_iterations, \
                                                                      data.subpixel_CC_max_refinement_step  )
                            else:
                                returns = cc_interpolation_local(     im1, im2Pm1, \
                                                                      data.subpixel_CC_refinement_step_threshold, \
                                                                      data.subpixel_CC_max_refinement_iterations, \
                                                                      data.subpixel_CC_max_refinement_step  )

                            nodeDispSubpixel = returns[0:3]
                            ccSubpixel       = returns[3]
                            iterations       = returns[4]
                            error           += returns[5]

                            if ccSubpixel >= cc and error == 0: cc = ccSubpixel
                            else:               error += 1024
                        # ===========================


                        # ===========================
                        # === IMAGE INTERPOLATION ===
                        # ===========================
                        if data.subpixel_mode[1] and error == 0:
                            if data.subpixel_mode[2]:
                                #Doing Image Interpolation with Translation AND Rotation!
                                guess = numpy.hstack( ( nodeDispSubpixel, nodeRotSubpixel) )

                                returns = image_interpolation_translation_rotation( im1, im2Rot, guess, cornerOffsetRot, data.subpixel_II_interpolationMode, data.subpixel_II_interpolation_order, data.subpixel_II_optimisation_mode )

                                nodeDispSubpixel = returns[0][0:3]
                                nodeRotSubpixel  = returns[0][3:6]
                                ccSubpixel       = returns[1]
                                iterations       = returns[2]
                                error           += returns[3]

                                cc = ccSubpixel

                            else:
                                #Doing Image Interpolation with Translation!
                                returns = image_interpolation_translation_rotation( im1, im2Pm1, nodeDispSubpixel, cornerOffset, data.subpixel_II_interpolationMode, data.subpixel_II_interpolation_order, data.subpixel_II_optimisation_mode )

                                nodeDispSubpixel = returns[0]
                                ccSubpixel       = returns[1]
                                iterations       = returns[2]
                                error           += returns[3]

                                cc = ccSubpixel
                        # ===========================

            # In any case send something on the q_results
            q_results.put( [ nodeNumber, nodeDispSubpixel + nodeDisplacement, nodeRotSubpixel, cc, error ]  )