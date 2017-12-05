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
import logging, traceback
from tomowarp_runfile import tomowarp_runfile

from tools.print_variable import pv
from tools.tsv_tools import ReadTSV, WriteTSV
from tools.input_parameters import input_parameters
from tools.input_parameters_read import input_parameters_read
from tools.input_parameters_update import input_parameters_update
from tools.print_help import help_continuum_slices, \
    help_continuum_slices_inputfile

def configLogging():
  
  logging.log = logging.getLogger('info')
  logging.log.setLevel(logging.DEBUG)
  logging.err = logging.getLogger('errors')
  logging.err.setLevel(logging.DEBUG)
  logging.gui = logging.getLogger('gui')
  logging.gui.setLevel(logging.DEBUG)
  
  ch = logging.StreamHandler()
  ch.setLevel(logging.DEBUG)
  #logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
  chFormatter = logging.Formatter('%(message)s')
  ch.setFormatter(chFormatter)
  
  logging.log.addHandler(ch)
  logging.err.addHandler(ch)
  logging.gui.addHandler(ch)


if __name__ == "__main__":

    argv = sys.argv[1:]

    #if len(argv) == 0:
      #help_continuum_slices()
      #sys.exit(2)

    try:
      opts, args = getopt.gnu_getopt(argv,"hd:c:p:j",[ "dir1=", "dir2=", "dir-out=", "cc-threshold=", "prior=", "z-position=", "desktop", "help", "log2file="])
    except getopt.GetoptError as e:
      print (str(e))
      help_continuum_slices()
      sys.exit(2)

    data = {}
    inputfile = None
    startGUI = False

    for opt, arg in opts:
      if opt in ("-h", "--help"):
          help_continuum_slices()
          if arg == "input":
            help_continuum_slices_inputfile()
          sys.exit()
      elif opt in ("-d", "--dir-out"):
          data['DIR_out'] = arg
      elif opt in ("-c", "--cc-threshold"):
          data['cc_threshold'] = arg
      elif opt in ("--dir1"):
          data['DIR_image1'] = arg
      elif opt in ("--dir2"):
          data['DIR_image2'] = arg
      elif opt in ("-p","--prior"):
          data['prior_file'] = arg
      elif opt in ("--z-position"):
          exec ("data['z_position'] ="+arg )
      elif opt in ("--desktop"):
          startGUI = True
      elif opt in ("--log2file"):
          data['log2file'] = eval ( arg )
      elif opt in ("-j"):
          data['jointFiles'] = True

    configLogging()
    # Make sure prints come out straight away
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

    if startGUI:
        try:
          inputfile = args[0]
        except:
          pass
          
        from gui.gTomoWarp2_ttk import *
        if len(args)>0: inputfile = args[0]
        buildGUI(inputfile, data)
    else:
        if len(args) != 1:
          help_continuum_slices()
          sys.exit(2)

        inputfile = args[0]
        try:
          print '\nInput file is "%s"\n'%( inputfile )
          data = input_parameters_read( inputfile, data )
        except Exception as exc:
          try: logging.err.error( exc )
          except: print  exc 
          sys.exit(2)
        
        try:
          if data.DIR_out:
            os.makedirs(data.DIR_out)
          else:
            data.DIR_out = "."
        except OSError:
            if not os.path.isdir(data.DIR_out):
              raise

        #data = input_parameters( data )
        try:
          tomowarp_runfile( data )
        except Exception as exc:
          #logging.err.debug( traceback.format_exc() )
          try: logging.err.error( exc.message )
          except: print  exc.message 