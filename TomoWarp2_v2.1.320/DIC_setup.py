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
INPUTS:
  - kinematics
  - "data" structure
  - q_data_requests to comunicate with data_delivery_worker
  - workerQueues list of queues that allows comunication of data from data_delivery_worker 
    to DIC_worker
  
OUTPUTS:
  - filled-in kinematics
"""

import sys, time
import numpy
import multiprocessing
import logging

from DIC_worker import DIC_worker
from tools.print_variable import pv

VERBOSE = True

# 2015-01-28 EA and ET: we need to pickle the DIC_worker pipes, that we are sending into a pipe to data_delivery_worker
#   See: http://stackoverflow.com/questions/1446004/python-2-6-send-connection-object-over-queue-pipe-etc
#        http://jodal.no/post/3669476502/pickling-multiprocessing-connection-objects/

# 2016-01-05 Adding full time output with code from Brian Visel's answer from:
#   http://stackoverflow.com/questions/4048651/python-function-to-convert-seconds-into-minutes-hours-and-days
intervals = (
    ('weeks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),    # 60 * 60 * 24
    ('hours', 3600),    # 60 * 60
    ('minutes', 60),
    ('seconds', 1),
    )

def display_time(seconds, granularity=2):
    result = []

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format( int( value ), name))
    return ', '.join(result[:granularity])


# ===========================
# === Program Starts Here ===
# ===========================
def DIC_setup( kinematics, data, q_data_requests, workerQueues ):

    # Wake up the data_delivery_worker with a new "data" array.
    q_data_requests.put( [ "NewData", data ] )

    # --- Define the extent of data we need to ask for ---
    # ----- i.e., generate extents matrix ----------------
    # 2014-10-04 EA and ET: updating extents matrix to a 4D array, with { node number }, { im_number 0,1 }, { top, bottom }, { z, y, x }
    extents = numpy.zeros( ( kinematics.shape[0], 2, 2, 3 ), dtype=numpy.int )

    #                     position            correlation_window            top extent of search window     prior displacement
    # --- Handling im1_lo
    extents[:,0,0] = kinematics[:,1:4] - data.correlation_window
    # --- Handling im1_hi
    extents[:,0,1] = kinematics[:,1:4] + data.correlation_window
    # --- Handling im2_lo
    extents[:,1,0] = kinematics[:,1:4] - data.correlation_window + numpy.array( data.search_window )[:,0] +  kinematics[:,4:7]
    # --- Handling im2_hi
    extents[:,1,1] = kinematics[:,1:4] + data.correlation_window + numpy.array( data.search_window )[:,1] +  kinematics[:,4:7]
    # ----------------------------------------------------

    # Extents can not exceed the image_slices_extents
    extents[:,:,0,0] = numpy.maximum( extents[:,:,0,0], numpy.ones_like(extents[:,:,0,0]) * data.image_slices_extent[:,0] )
    extents[:,:,1,0] = numpy.minimum( extents[:,:,1,0], numpy.ones_like(extents[:,:,1,0]) * data.image_slices_extent[:,1] )


    # --- Set Up Queues ---
    # This queue will contain the nodes for the DIC workers to process
    q_nodes         = multiprocessing.Queue()

    # This queue will contain the results for each node
    q_results       = multiprocessing.Queue( )


    # --- Launch DIC worker nodes  ---
    for workerNumber in range( data.nWorkers ):
        p = multiprocessing.Process( target=DIC_worker, args=( workerNumber, q_nodes, q_results, q_data_requests, workerQueues[ workerNumber ], data ) )
        p.start()
    # ----------------------------------

    # Calculate the highest slice we need
    currentTopSlice_image1 = min(extents[:,0,0,0])
    currentTopSlice_image2 = max( min( min(extents[:,1,0,0] ) - int( data.subpixel_mode[2]*max(data.correlation_window)*numpy.sqrt(3)+1 ), data.image_slices_extent[1,1]), 0 )

    # Current bottom slice is the minimum between the lowest slice given by the max on the extents
    #   and the current bottom slice due to memory limit
    currentBottomSlice_image1 = min( max(extents[:,0,1,0]), currentTopSlice_image1 + data.memLimitSlices)
    currentBottomSlice_image2 = min( max(extents[:,1,1,0]) + int( data.subpixel_mode[2]*max(data.correlation_window)*numpy.sqrt(3)+1 ), currentTopSlice_image2 + data.memLimitSlices)

    # Initializing a node done table
    nodeDoneTable = numpy.zeros( ( kinematics.shape[0], 1 ), dtype = bool )

    # Make sure no node data extents are larger than the memory limit in the vertical direction
    extentsCheck = (extents[:,:,1,0] - extents[:,:,0,0]) > data.memLimitSlices

    if extentsCheck.any() :
      logging.err.error("DIC_setup(): The memory limit set does not fulfil the required vertical extents for at least one node")
      for workerNumber in range( data.nWorkers ):
          q_nodes.put( [ "STOP" ] )
      return

    # If this is the case mark this node as done so it is not processed and give an error
    #TODO: could conditionally accept these nodes
    nodeDoneTable[ numpy.logical_or( extentsCheck[:,0], extentsCheck[:,1] ) ] = True
    kinematics[    numpy.logical_or( extentsCheck[:,0], extentsCheck[:,1] ), 11 ] += 512

    # --- Variables for receive queue management ---
    nNodes_to_correlate = kinematics[ :, 0 ].shape[0] - sum( nodeDoneTable )
    nodesProcessedTotal  = 0
    printInterval   = max( 1, int(nNodes_to_correlate*data.printPercent/100.0) )
    # ----------------------------------------------

    # --- These two variables are to have a calculation time ---
    calculationTimeA = time.time()
    prevNodesProcessed = 0
    # ----------------------------------------------------------


    #Outside loop continues until there are no nodes left
    while not nodeDoneTable.all():

        # --- update NewExtents for the data_delivery_worker for the newly added nodes ---
        q_data_requests.put( [ "NewExtents", [ [ currentTopSlice_image1, currentBottomSlice_image1 ], [ currentTopSlice_image2, currentBottomSlice_image2 ] ] ] )
        # --------------------------------------------------

        # reset node counter -- in order to know when to stop...
        nodesToProcess = 0

        # For every node check if it has been done and if not whether it is inside the current block of data
        for nodeNumber in range( kinematics.shape[0] ):
            nodeExtent = extents[ nodeNumber ]
            if not nodeDoneTable[ nodeNumber ]  and nodeExtent[0,0,0] >= currentTopSlice_image1    \
                                                and nodeExtent[0,1,0] <= currentBottomSlice_image1 \
                                                and nodeExtent[1,0,0] >= currentTopSlice_image2    \
                                                and nodeExtent[1,1,0] <= currentBottomSlice_image2 :

                # Adding the node to the queue for the DIC_worker and update nodeDoneTable
                q_nodes.put( [ nodeNumber, nodeExtent ] )
                nodeDoneTable[ nodeNumber ] = True
                # Add one to node counter...
                nodesToProcess += 1

        # Checking if all nodes have been sent to the worker add STOP to queue to stop the DIC_workers
        if nodeDoneTable.all():
            for workerNumber in range( data.nWorkers ):
                q_nodes.put( [ "STOP" ] )

        # Updating current slices
        # Calculate the highest slice from NOT done nodes
        if ( nodeDoneTable == False ).any():
            currentTopSlice_image1 = min( extents[ numpy.where( nodeDoneTable == False )[0], 0, 0, 0] )
            currentTopSlice_image2 = max( min( min( extents[ numpy.where( nodeDoneTable == False )[0], 1, 0, 0] - int( data.subpixel_mode[2]*max(data.correlation_window)*numpy.sqrt(3)+1 ) ), data.image_slices_extent[1,1]), 0 )

        # Current bottom slice is the minimum between the lowest slice given by the max on the extents
        #   and the current bottom slice due to memory limit
        currentBottomSlice_image1 = min( max(extents[:,0,1,0]), currentTopSlice_image1 + data.memLimitSlices)
        currentBottomSlice_image2 = min( max(extents[:,1,1,0]) + int( data.subpixel_mode[2]*max(data.correlation_window)*numpy.sqrt(3)+1 ), currentTopSlice_image2 + data.memLimitSlices)


        # Loop until all workers have hanged up
        #while finishedThreads < data.nWorkers:
        while nodesToProcess > 0:

            message = q_results.get()

            nodesProcessedTotal  += 1
            nodesToProcess       -= 1
            
            if nodesProcessedTotal%printInterval == 0:
              
                  print "\r\tCompleted node number %05i  ( %2.2f %% )"%( nodesProcessedTotal, 100*(nodesProcessedTotal)/float(nNodes_to_correlate) ),

                  # --- Calculation of remaining time ---
                  calculationTimeB = time.time()
                  nodesProcessedTotalThisStep = nodesProcessedTotal - prevNodesProcessed
                  secondsForThisStep      = calculationTimeB - calculationTimeA
                  try:
                    nodesPerSecond         = nodesProcessedTotalThisStep / float( secondsForThisStep )
                  except ZeroDivisionError:
                    nodesPerSecond         = nodesProcessedTotalThisStep
                  nodesRemaining          = nNodes_to_correlate - nodesProcessedTotal
                  secondsRemaining        = ( nodesRemaining / float( nodesPerSecond ) )[0]


                  # 2014-10-03 EA: Estimating computation time between printouts...
                  print "\tTime remaining = ~%s\033[K"%( display_time( secondsRemaining ) ),
                  sys.stdout.flush()

                  # update counters:
                  calculationTimeA       = time.time()
                  prevNodesProcessed     = nodesProcessedTotal
                  # -------------------------------------

            # Extract result of this thread's result
            nodeNumber = message[0]

            #  Since C-code pixel search doesn't know about the prior field and the search window, add these back in now, in order for the
            #   displacement to be absolute.
            message[1][0] += extents[nodeNumber,1,0,0] - extents[nodeNumber,0,0,0]
            message[1][1] += extents[nodeNumber,1,0,1] - extents[nodeNumber,0,0,1]
            message[1][2] += extents[nodeNumber,1,0,2] - extents[nodeNumber,0,0,2]

            # Copy into relevant results matrices...
            kinematics[ nodeNumber, 4  ]  = message[1][0]
            kinematics[ nodeNumber, 5  ]  = message[1][1]
            kinematics[ nodeNumber, 6  ]  = message[1][2]
            kinematics[ nodeNumber, 7  ]  = message[2][0]
            kinematics[ nodeNumber, 8  ]  = message[2][1]
            kinematics[ nodeNumber, 9  ]  = message[2][2]
            kinematics[ nodeNumber, 10 ]  = message[3]
            kinematics[ nodeNumber, 11 ] += message[4]     # Error is additive

            # 2015-07-30 - EA: cc_percent badly applied, applying it differently, this is not elegant, but at least not wrong:
            if data.cc_percent:
              kinematics[ nodeNumber, 10 ]  = kinematics[ nodeNumber, 10 ] * 100

    return kinematics
