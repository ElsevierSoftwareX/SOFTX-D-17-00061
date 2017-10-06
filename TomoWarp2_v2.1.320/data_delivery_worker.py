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
This is the worker that loads data and send it to the different workers asking for data
This allows slice-loading, max memory limits as well as facilitating the structural 
passage to MPI

2015-01-28 ET and EA: Changing this function to be considerably less context aware.
  We will only be given an extent to work on, and service data requests from nodes in 
  absolute coordinates.
  The objective is for this data delivery to be run at the beginning from the main file 
  and NOT to close at the end of each DIC setup -- getting ready for multiple passes 
  through the data, as well as unstructured data.
  
INPUTS:
  - q_data_requests for incoming communications
  - workerQueues list of queues that allows comunication of data to DIC_worker

Inputs on the IN pipes:
  - "NewData":     new "data" to work on.      # This will come from each run of DIC_setup
  - "NewExtents":  new extents to load         # If not in full Volume mode this will come
                                                  a few times from each DIC_setup run
  - "DataRequest": data requests from nodes    # This will come #nodes times for each 
                                                  DIC_setup
  - "STOP":        to stop the process
"""

import sys
import logging
from tools.load_slices import load_slices

VERBOSE = True

# to unpickle our pipes to the DIC workers, otherwise they can't be send by pipe, see
#   http://stackoverflow.com/questions/1446004/python-2-6-send-connection-object-over-queue-pipe-etc

def data_delivery_worker( pipe_data_requests_out, workerQueues ):
  
  
    if VERBOSE: logging.log.info( "data_delivery_worker: Started." )

    # Initialise current z-extents and empty images
    zExtents_im1_current = [ -1, -1 ]
    zExtents_im2_current = [ -1, -1 ]

    # initialise empty initial images
    im1 = None
    im2 = None

    # Outside loop -- listen for:
    #   Message A1: "NewData": new data array/dict
    #   Message A2: "NewPipe": one new pipe..       2015-01-30 -- Deprecated: queues now passed on startup
    #   Message B: new extents
    #   Message C: data request
    #   Message D: STOP and close data_delivery_worker at the end of the main
    while True:

        # Get a message from the pipe_data_requests
        message = pipe_data_requests_out.get()

        if message[0] == "NewData":
            # Here we are expecting a new DATA array, and individual pipes to workers
            data              = message[1]

        elif message[0] == "NewExtents":

            if VERBOSE: logging.log.info( "data_delivery_worker(): message = "+str( message ) )
            # Here we are expecting two arrays with a new top and bottom z slices numbers for im1 and im2
            zExtents_im1_new = message[1][0]
            zExtents_im2_new = message[1][1]

            try:
              # load new slices, if any, and update current z extents.
              if VERBOSE: logging.log.info( "data_delivery_worker(): Loading data..." )
              zExtents_im1_current, im1 = load_slices( zExtents_im1_new, zExtents_im1_current, im1, 1, data )
              zExtents_im2_current, im2 = load_slices( zExtents_im2_new, zExtents_im2_current, im2, 2, data )
              if VERBOSE: logging.log.info( "data_delivery_worker(): Done" )
            except Exception as exc:
              #raise Exception(exc)
              logging.err.error( exc.message )
              im1=[]
              im2=[]

        elif message[0] == "DataRequest":

            # Here we are expecting a worker number (in order to reply on the right queue), an im1 top and bottom corner, and im2 top and bottom corner
            workerNumber = message[1]
            nodeExtent   = message[2]

            # Node extents are in absolute coordinates:
            #   First: Add crop in horizontal directions, -- the loaded ROI is still in absolute image coordinates
            nodeExtent[ 0, :, 1:3 ] = nodeExtent[ 0, :, 1:3 ] - data.ROI_corners[0,0,1:3]
            nodeExtent[ 1, :, 1:3 ] = nodeExtent[ 1, :, 1:3 ] - data.ROI_corners[1,0,1:3]

            # Second, add z_extent for this row of nodes.
            nodeExtent[0,:,0]       = nodeExtent[0,:,0]       - zExtents_im1_current[0]
            nodeExtent[1,:,0]       = nodeExtent[1,:,0]       - zExtents_im2_current[0]

            # 2015-11-18 EA: There is a strange error of im2.shape failing because im2 is a list...
            #   putting in a light check to avoid this...
            try:
                im1.shape
                im2.shape

                for i_d in range(3):
                    # crop the extent of requested volume to fit in the available volume (i_d = index for dimensions)
                    nodeExtent[ 0, nodeExtent[0,:,i_d]  <  0,        i_d      ] = 0
                    nodeExtent[ 0, nodeExtent[0,:,i_d]  >  im1.shape[i_d], i_d] = im1.shape[i_d]
                    nodeExtent[ 1, nodeExtent[1,:,i_d]  <  0,        i_d      ] = 0
                    nodeExtent[ 1, nodeExtent[1,:,i_d]  >  im2.shape[i_d], i_d] = im2.shape[i_d]

                im1_subvolume = im1[  nodeExtent[0,0,0]:nodeExtent[0,1,0]+1,\
                                      nodeExtent[0,0,1]:nodeExtent[0,1,1]+1,\
                                      nodeExtent[0,0,2]:nodeExtent[0,1,2]+1 ].copy()

                im2_subvolume = im2[  nodeExtent[1,0,0]:nodeExtent[1,1,0]+1,\
                                      nodeExtent[1,0,1]:nodeExtent[1,1,1]+1,\
                                      nodeExtent[1,0,2]:nodeExtent[1,1,2]+1 ].copy()

                # make sure that we have enough data to send at least for a correlation window.
                if im1_subvolume.shape != tuple([ x*2+1 for x in data.correlation_window]) or im2_subvolume.shape < tuple([ x*2+1 for x in data.correlation_window]):
                    workerQueues[ workerNumber ].put( [ "Error", None, None] )

                else:
                    # Reply with data into the worker's data queue
                    workerQueues[ workerNumber ].put( [ "Data", im1_subvolume, im2_subvolume ] )
            except:
                workerQueues[ workerNumber ].put( [ "Error", None, None] )


        elif message[0] == "STOP":
            logging.log.info( "data_delivery_worker: Received stop, stopping" )
            return -1
