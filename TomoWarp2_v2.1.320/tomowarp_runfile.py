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
Run file that starts and stop data_delivery_worker, calls the DIC_setup function, 
save kinematics results and run the post process.
"""

import os, sys, time, getopt
import re, traceback
import numpy
import multiprocessing
import logging
from tools.tifffile import imsave

from DIC_setup import DIC_setup
from data_delivery_worker import data_delivery_worker
from prior_field.layout_nodes import layout_nodes
from prior_field.regular_prior_interpolator import regular_prior_interpolator
from postproc.process_results import process_results

from tools.print_variable import pv
from tools.tsv_tools import ReadTSV, WriteTSV
from tools.input_parameters import input_parameters
from tools.input_parameters_read import input_parameters_read
from tools.input_parameters_update import input_parameters_update
from tools.print_help import help_continuum_slices, \
    help_continuum_slices_inputfile


def tomowarp_runfile( data ):
    # Get the starting time for the calculation.
    data.timeStart = time.time()

    if data['log2file']:
      # Setting the logging files if requested
      fh_log = logging.FileHandler(data.DIR_out+"/"+data.output_name+"_"+time.strftime( "%Y%m%d%H%M", \
        time.localtime( data.timeStart ) )+".log")
      logging.log.addHandler(fh_log)
      if data['jointFiles']:
        fh_err = fh_log
      else:
        fh_err = logging.FileHandler(data.DIR_out+"/"+data.output_name+"_"+time.strftime( "%Y%m%d%H%M", \
          time.localtime( data.timeStart ) )+".err")
      logging.err.addHandler(fh_err)
    
    # Reading parameters from input file
    data = input_parameters( data )
    # 2015-04-28 -- Update all automatic variables in data
    input_parameters_update( data )

    logging.log.info('\n')
    try:
      # Setting the message format in logging file to show time and type of message
      fh_log.setFormatter( logging.Formatter('%(asctime)s - %(levelname)s - %(message)s') )
    except:
      pass

    
    # ===============================================================
    # ==========  Creating Queues and running worker  ===============
    # ===============================================================
    # -------------------------------------
    # 2015-01-30 start workerQueues here, since they can only be passed as function variables
    workerQueues = [ None ] * data.nWorkers
    for workerNumber in xrange( data.nWorkers ):
        workerQueues[ workerNumber ] = multiprocessing.Queue( )

    # Setup the data queue and start the data delivery worker ===
    # This queue will contain requests for data extents from DIC workers to the data delivery worker
    q_data_requests = multiprocessing.Queue( )

    # Launch a data_delivery_worker
    ddw = multiprocessing.Process( target=data_delivery_worker, args=( q_data_requests , workerQueues, ) )
    ddw.start()
    # -------------------------------------
    # ===============================================================


    if not (data.usePriorCoordinates) or data.prior_file == None:
        # Generating a grid of points if not given
        kinematics, nodes_z, nodes_y, nodes_x = layout_nodes( data.node_spacing, data.ROI_corners[0] )
        nodesToProcess = numpy.array( range( 0, kinematics.shape[0] ) )

        logging.log.info( "* Identified "+str(int(kinematics[-1,0]+1))+" Node(s)\n" \
                          "   * Node positions Z:"+str( nodes_z )+"\n"          \
                          "   * Node positions Y:"+str( nodes_y )+"\n"          \
                          "   * Node positions X:"+str( nodes_x )+"\n" )

    if data.prior_file != None:

        # Load a prior file and try to figure out whether the node spacing is the the same as what we want...
        logging.log.info( " Loading Prior file: %s"%(data.prior_file) )
        prior = ReadTSV( data.prior_file,  "NodeNumber", [ "Zpos", "Ypos", "Xpos", "Zdisp", "Ydisp", "Xdisp",  "Zrot", "Yrot", "Xrot","CC", "Error" ], [1,0] )

        # sort the prior to be sure it is organised
        # can be needed if the prior comes from elsewhere
        # here it is important that the prior is sorted in the z direction
        prior = prior[numpy.argsort(prior, axis=0, kind='mergesort')[:,3]]
        prior = prior[numpy.argsort(prior, axis=0, kind='mergesort')[:,2]]
        prior = prior[numpy.argsort(prior, axis=0, kind='mergesort')[:,1]]

        if data.usePriorCoordinates:
            kinematics = prior
            # Selecting point from the prior that have
            # - an error in a specific range (Default value for the range is [-Inf Inf] so that all the points are considered)
            # - a correlation coefficient smaller than a specified value (Default is Inf)
            reprocessCondition = numpy.zeros( ( 2, kinematics.shape[0] ) )
            reprocessCondition[0,:] = numpy.logical_and( kinematics[:,11] >= data.errorLimit[0], kinematics[:,11] <= data.errorLimit[1] )
            reprocessCondition[1,:] = kinematics[:,10] < data.prior_cc_threshold

            nodesToProcess = numpy.where( sum( reprocessCondition ) )[0]

            # Reset values for nodes to reprocess .
            kinematics[ nodesToProcess, 4:12 ] = [ 0, 0, 0, 0, 0, 0, 0, 0 ]

        else:
            kinematics = regular_prior_interpolator( prior,  kinematics, data.priorSmoothing )
            nodesToProcess = numpy.array( range( 0, kinematics.shape[0] ) )

            if not data.images_2D: imsave( data.DIR_out + "/%s-prior-z-field-%04ix%04ix%04i.tif"%(  data.output_name, len(nodes_x), len(nodes_y), len(nodes_z)),     kinematics[ :, 4 ].reshape( ( len(nodes_z), len(nodes_y), len(nodes_x) ) ).astype( '<f4' ) )
            imsave( data.DIR_out + "/%s-prior-y-field-%04ix%04ix%04i.tif"%(  data.output_name, len(nodes_x), len(nodes_y), len(nodes_z)),     kinematics[ :, 5 ].reshape( ( len(nodes_z), len(nodes_y), len(nodes_x) ) ).astype( '<f4' ) )
            imsave( data.DIR_out + "/%s-prior-x-field-%04ix%04ix%04i.tif"%(  data.output_name, len(nodes_x), len(nodes_y), len(nodes_z)),     kinematics[ :, 6 ].reshape( ( len(nodes_z), len(nodes_y), len(nodes_x) ) ).astype( '<f4' ) )


    logging.log.info( "Nodes To Process = %i"%(nodesToProcess.shape[0]) )

    if nodesToProcess.shape[0] != 0:
      try:
        kinematics[ nodesToProcess,: ] = DIC_setup( kinematics[ nodesToProcess,: ], data, q_data_requests , workerQueues )
      except Exception as exc:
        raise Exception(exc)

    # === Send stop message to the data delivery worker =============
    q_data_requests.put( [ "STOP" ] )
    # ===============================================================

    try:
        outFile = data.DIR_out+"/"+data.output_name+".tsv"
        if os.path.isfile(outFile):
          outFile = data.DIR_out+"/"+data.output_name+"_"+time.strftime( "%Y%m%d%H%M", time.localtime( data.timeStart ) )+".tsv"
        WriteTSV( outFile, [ "NodeNumber", "Zpos", "Ypos", "Xpos", "Zdisp", "Ydisp", "Xdisp",  "Zrot", "Yrot", "Xrot", "CC", "Error" ], kinematics )
    except Exception as exc:
      raise Exception(exc)          

    try:
        process_results(  kinematics, data )
    except Exception as exc:
      raise Exception(exc)          

    time_end = time.time()
    runTime = time_end - data.timeStart

    hours = int(runTime/(60*60) )
    minutes = int(runTime/(60) ) - 60*hours
    seconds = runTime - 60*60*hours - 60*minutes
    logging.log.info( "TIME: I think I ran for: %02i:%02i:%02i"%( hours, minutes, seconds ) )
    
    try:
      logging.log.removeHandler(fh_log)
      #logging.err.removeHandler(fh_err)
    except:
      pass
    
    return kinematics, outFile