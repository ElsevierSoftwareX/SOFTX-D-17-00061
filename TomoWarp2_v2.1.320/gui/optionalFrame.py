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

import os, sys
from os.path import expanduser
from Tkinter import *
import Tkconstants, tkFileDialog, tkMessageBox

from guiFunctions import *

from Frames import *

from tools.print_variable import pv


class Optional_setup(Frame):

    # Definition of coordinates dimensions label
    coordLabelExt = ( 'z low', 'z high', 'y low', 'y high', 'x low', 'x high' )
    #coordLabel = ( 'z', 'y', 'x' )
    interpLabel = ( '3_CC', '2_II', '1_II' )
    variables = {}

    def choose_file( self ):
      # Function to select a prior file and set the corresponding variable
      initDir = os.path.dirname( self.variables['prior_file'].get() )
      if initDir == expanduser( "~" ) or initDir == "": initDir = self.master.master.homeDir
      priorFile = tkFileDialog.askopenfilename( parent=self.master, initialdir=initDir,\
            title='Please select a priof file', filetypes = [ ("Output Files", "*.tsv"), ('All','*') ] )
      self.variables['prior_file'].set( priorFile )
      self.master.master.homeDir = os.path.dirname(priorFile)

    def createWidgets(self):

        # Set a standard size for widgets
        self.labelWidth = 15
        self.entryWidth = 15
        self.buttonWidth = 5

        currentRow = 0

        ### TITLE ###
        Label(self, text="Optional Parameters", font=("bold")).grid(row=currentRow, column=0, columnspan=7, pady = 10 )
        currentRow += 1

        ### IMAGE NAME FILTER AND EXTENSION ###
        Label( self, text="Image 1 filter", width=self.labelWidth, anchor=W               ).grid( row=currentRow,   column=0, sticky=W,   padx=5 )
        Entry( self, textvariable=self.variables['image_1_filter'], width=self.entryWidth ).grid( row=currentRow,   column=1, sticky=W+E, padx=5, columnspan = 2 )
        Label( self, text="Image 2 filter", width=self.labelWidth, anchor=W               ).grid( row=currentRow,   column=3, sticky=W,   padx=5 )
        Entry( self, textvariable=self.variables['image_2_filter'], width=self.entryWidth ).grid( row=currentRow,   column=4, sticky=W+E, padx=5, columnspan = 2 )
        Label( self, text="Images extension", width=self.labelWidth, anchor=E             ).grid( row=currentRow,   column=6, sticky=W,   padx=5 )
        Entry( self, textvariable=self.variables['image_ext'], width=self.entryWidth      ).grid( row=currentRow+1, column=6, sticky=W+E, padx=5 )
        self.grid_rowconfigure(currentRow, pad=2)
        currentRow += 1

        ### IMAGE DIGITS ###
        Label( self, text="Image 1 digits", width=self.labelWidth, anchor=W               ).grid( row=currentRow, column=0, sticky=W,   padx=5 )
        self.Dig1 = Entry( self, textvariable=self.variables['image_1_digits'], width=self.entryWidth )
        self.Dig1.grid( row=currentRow, column=1, sticky=W+E, padx=5 )
        Label( self, text="Image 2 digits", width=self.labelWidth, anchor=W               ).grid( row=currentRow, column=3, sticky=W,   padx=5 )
        self.Dig2 = Entry( self, textvariable=self.variables['image_2_digits'], width=self.entryWidth )
        self.Dig2.grid( row=currentRow, column=4, sticky=W+E, padx=5 )
        currentRow += 1

        ### OUTPUT FILE NAME ###
        Label( self, text="Output filename", width=self.labelWidth, anchor=W            ).grid( row=currentRow, column=0, sticky=W,   padx=5, pady=(10,0) )
        Entry( self, textvariable=self.variables['output_name']                         ).grid( row=currentRow, column=1, sticky=W+E, padx=5, pady=(10,0), columnspan=5)
        ### PRINT CC AS % ###
        Checkbutton( self, text="Print CC as %", variable=self.variables['cc_percent']  ).grid( row=currentRow, column=6, sticky=W,   padx=5, pady=(10,0) )
        self.grid_rowconfigure(currentRow, pad=2)
        currentRow += 1

        ### OUTPUT FILE NAME COMPOSITION ###
        Label( self, text="Sample", width=self.labelWidth, anchor=W                     ).grid( row=currentRow, column=0, sticky=W,   padx=5, pady=(0,10) )
        Entry( self, textvariable=self.variables['name_prefix'], width=self.entryWidth  ).grid( row=currentRow, column=1, sticky=W+E, padx=5, pady=(0,10) )
        Label( self, text="name test 1", width=self.labelWidth, anchor=W                ).grid( row=currentRow, column=2, sticky=W,   padx=5, pady=(0,10) )
        Entry( self, textvariable=self.variables['name_1'], width=self.entryWidth       ).grid( row=currentRow, column=3, sticky=W+E, padx=5, pady=(0,10) )
        Label( self, text="name test 2", width=self.labelWidth, anchor=W                ).grid( row=currentRow, column=4, sticky=W,   padx=5, pady=(0,10) )
        Entry( self, textvariable=self.variables['name_2'], width=self.entryWidth       ).grid( row=currentRow, column=5, sticky=W+E, padx=5, pady=(0,10) )
        self.grid_rowconfigure(currentRow, pad=2)
        currentRow += 1
  
        # Horizontal line
        Frame(self,height=1,width=50,bg="grey").grid(row=currentRow, columnspan=7, sticky=EW, pady=(10,10))
        currentRow += 1

        ### ROI ###
        Label( self, text="ROI corners image 1", width=self.labelWidth, anchor=W ).grid( row=currentRow+1, column=0, sticky=W, padx=5 )
        self.ROI1 = entries_row(self, self.variables['ROI_corners'], currentRow+1, width=self.entryWidth)
        self.grid_rowconfigure(currentRow, pad=2)
        currentRow += 2

        # Horizontal line
        Frame(self,height=1,width=50,bg="grey").grid(row=currentRow, columnspan=7, sticky=EW, pady=(10,10))
        currentRow += 1

        ### PRIOR FILE ###
        Label( self, text="Prior file", width=self.labelWidth, anchor=W                   ).grid( row=currentRow, column=0, sticky=W,   padx=5, pady=(10,0) )
        Entry( self, textvariable=self.variables['prior_file']                            ).grid( row=currentRow, column=1, sticky=W+E, padx=5, pady=(10,0), columnspan=3)
        Button(self, text="Browse",command=self.choose_file, width=self.buttonWidth       ).grid( row=currentRow, column=4, sticky=W  , padx=5, pady=(10,0) )
        ### MEDIAN FILTER###
        Label( self, text="Median filter size", width=self.labelWidth, anchor=W     ).grid( row=currentRow, column=5, sticky=W,   padx=5, pady=(10,0) )
        Entry( self, textvariable=self.variables['priorSmoothing'], width=self.entryWidth ).grid( row=currentRow, column=6, sticky=W+E, padx=5, pady=(10,0) )
        currentRow += 1
        
        ### USE POINT FROM PRIOR ###
        Checkbutton( self, text="Use points from prior", variable=self.variables['usePriorCoordinates'], width=self.entryWidth ).grid( row=currentRow, column=0, sticky=W+E, padx=5, pady=(0,10) )
        Label( self, text="with", width=self.labelWidth                                   ).grid( row=currentRow, column=1, sticky=W+E, padx=5, pady=(0,10) )
        ### ERROR LIMITS ###
        Entry( self, textvariable=self.variables['errorLowLimit'], width=self.entryWidth  ).grid( row=currentRow, column=2, sticky=W+E, padx=5, pady=(0,10) )
        Label( self, text="<= error <=", width=self.labelWidth                              ).grid( row=currentRow, column=3, sticky=W+E, padx=5, pady=(0,10) )
        Entry( self, textvariable=self.variables['errorHighLimit'], width=self.entryWidth ).grid( row=currentRow, column=4, sticky=W+E, padx=5, pady=(0,10) )
        Label( self, text="or     cc <", width=self.labelWidth, anchor=E                  ).grid( row=currentRow, column=5, sticky=E  , padx=5, pady=(0,10) )
        ### CC THRESHOLD ###
        Entry( self, textvariable=self.variables['prior_cc_threshold'], width=self.entryWidth ).grid( row=currentRow, column=6, sticky=W+E, padx=5, pady=(0,10) )
        self.grid_rowconfigure(currentRow, pad=2)
        currentRow += 1

        # Horizontal line
        Frame(self,height=1,width=50,bg="grey").grid(row=currentRow, columnspan=7, sticky=EW, pady=(10,10))
        currentRow += 2

        ### MEMORY LIMIT ###
        Label( self, text="Memory limit (MB)", width=self.labelWidth, anchor=W            ).grid( row=currentRow, column=0, sticky=W,   padx=5 )
        Entry( self, textvariable=self.variables['memLimitMB'], width=self.entryWidth     ).grid( row=currentRow, column=1, sticky=W+E, padx=5 )
        ### NUM OF CPUS ###
        Label( self, text="Number of CPUs", width=self.labelWidth, anchor=W               ).grid( row=currentRow, column=2, sticky=W,   padx=5 )
        Entry( self, textvariable=self.variables['nWorkers'], width=self.entryWidth       ).grid( row=currentRow, column=3, sticky=W+E, padx=5 )
        ### GREY THRESHOLD ###
        Label( self, text="Grey threshold", width=self.labelWidth, anchor=W                ).grid( row=currentRow,   column=4, sticky=W,   padx=5 )
        Label( self, text="Low:", width=self.labelWidth, anchor=W                              ).grid( row=currentRow-1, column=5, sticky=W,   padx=5 )
        Entry( self, textvariable=self.variables['grey_low_threshold'], width=self.entryWidth  ).grid( row=currentRow,   column=5, sticky=W+E, padx=5 )
        Label( self, text="High:", width=self.labelWidth, anchor=W                             ).grid( row=currentRow-1, column=6, sticky=W,   padx=5 )
        Entry( self, textvariable=self.variables['grey_high_threshold'], width=self.entryWidth ).grid( row=currentRow,   column=6, sticky=W+E, padx=5 )
        self.grid_rowconfigure(currentRow, pad=2)
        currentRow += 1

        # Horizontal line
        Frame(self,height=1,width=50,bg="grey").grid(row=currentRow, columnspan=7, sticky=EW, pady=(10,10))
        currentRow += 1

        ### SUBPIXEL REFINEMENT ###
        Label( self, text="Subpixel refinement mode", anchor=W ).grid( row=currentRow, column=0, columnspan=2, sticky=W, padx=5, pady=( 10, 0 ) )
        currentRow += 1
        self.spCheck_CC  = Checkbutton( self, text="Correlation Coefficient",        variable=self.variables['subpixel_mode'][self.interpLabel[0]] )
        self.spCheck_IIt = Checkbutton( self, text="Image Interpolator translation", variable=self.variables['subpixel_mode'][self.interpLabel[1]] )
        self.spCheck_IIt.config( command=self.subpixelMode, state='normal')
        self.spCheck_IIr = Checkbutton( self, text="Image Interpolator rotation",    variable=self.variables['subpixel_mode'][self.interpLabel[2]] )
        self.subpixelMode()
        self.spCheck_CC.grid(  row=currentRow, column=0, columnspan=2, sticky=W )
        self.spCheck_IIt.grid( row=currentRow, column=2, columnspan=2, sticky=W )
        self.spCheck_IIr.grid( row=currentRow, column=4, columnspan=2, sticky=W )
        self.grid_rowconfigure(currentRow, pad=2)

        ### SUBPIXEL REFINEMENT ADVANCED MODE ###
        # This button open a new window
        Button(self, text="Advanced setting",command=lambda: Advanced_setup ( master=self ), width=self.labelWidth ).grid( row=currentRow, column=6, sticky=W  , padx=5 )

        currentRow += 1

    def subpixelMode( self ):
    # This function disable the Image Interpolator rotation option is the translation is not selected
        if self.variables['subpixel_mode'][self.interpLabel[1]].get():
            self.spCheck_IIr.config( state='normal')
        else:
            variable=self.variables['subpixel_mode'][self.interpLabel[2]].set(0)
            self.spCheck_IIr.config( state='disabled')

    def buid_ouputfilename( self, *args ):
    # This function contruct the output filename from "Sample", "name_1", "name_2", and "node_spacing"
        from minimalFrame import Minimal_setup
        if not self.variables['name_prefix'].get() == "":
          output_name = "%s-%s-%s"%( self.variables['name_prefix'].get(), \
                                      self.variables['name_1'].get(), self.variables['name_2'].get() )
          try:
            output_name = "%s-ns=%i"%( output_name, Minimal_setup.variables['node_spacing']['y'].get() )
          except:
            pass
          self.variables['output_name'].set( output_name )
    
    def creatVariables(self):

        ### VARIABLES DEFINITION FROM DATA STRUCTURE ###

        stringList = [ 'name_prefix','name_1', 'name_2', 'output_name', 'image_1_filter', 'image_2_filter',\
                       'image_ext', 'prior_file', 'subpixel_II_optimisation_mode','subpixel_II_interpolationMode' ]

        for field in stringList:
          self.variables[field] = StringVar()
          self.variables[field].set(self.data[field])

        intList = [ 'memLimitMB', 'nWorkers', 'image_1_digits', 'image_2_digits', 'cc_percent', 'priorSmoothing', 'usePriorCoordinates',\
                    'subpixel_CC_max_refinement_step', 'subpixel_CC_max_refinement_iterations', 'subpixel_II_interpolation_order']

        for field in intList:
          self.variables[field] = IntVar()
          self.variables[field].set(self.data[field])

        floatList = ['grey_low_threshold', 'grey_high_threshold', 'subpixel_CC_refinement_step_threshold',\
                      'errorLowLimit', 'errorHighLimit', 'prior_cc_threshold']

        for field in floatList:
          self.variables[field] = DoubleVar()
          self.variables[field].set(self.data[field])

        dictionariesList = ['subpixel_mode']

        for dictField in dictionariesList:
          try:
              self.variables[dictField] = index2coord(self.data[dictField], self.interpLabel)
          except:
            self.variables[dictField]={}
            for field in self.interpLabel:
              self.variables[dictField][field] = IntVar()
              self.variables[dictField][field].set( self.data[dictField] )

        #dictionariesList = []

        #for dictField in dictionariesList:
          #if type(self.data[dictField]) is list:
              #self.variables['Advanced'].set(1)
              #self.variables[dictField] = index2coord(self.data[dictField], self.coordLabel)
          #else:
            #self.variables[dictField]={}
            #for field in self.coordLabel:
              #self.variables[dictField][field] = IntVar()
              #self.variables[dictField][field].set( self.data[dictField] )

        dictionariesList = ['ROI_corners']

        for dictField in dictionariesList:
          try:
                                    # map+zip convert ROI_corners structure to [[zl,zh],[yl,yh],[xl,xh]]
              self.variables[dictField] = index2coord( map( list, zip(*self.data[dictField]) ), self.coordLabelExt)
          except:
            self.variables[dictField]={}
            for field in self.coordLabelExt:
              self.variables[dictField][field] = IntVar()
              self.variables[dictField][field].set( self.data[dictField] )
      
        # When one of thee variable is changed an action is taken
        self.variables[ 'name_prefix'  ].trace( 'w', self.buid_ouputfilename)
        self.variables[ 'name_1'       ].trace( 'w', self.buid_ouputfilename)
        self.variables[ 'name_2'       ].trace( 'w', self.buid_ouputfilename)

    def __init__(self, master=None):

        Frame.__init__(self, master)

        for idx in range(12):
          self.grid_rowconfigure(idx, weight=1)
        for idx in range(7):
            self.grid_columnconfigure(idx, weight=1)

        self.configure( bd=1, relief=SUNKEN)
        self.creatVariables()
        self.createWidgets()


class Advanced_setup( Toplevel ):
    # New window to specify subpixel refinement parameters
    def __init__(self, master=None):

        Toplevel.__init__(self, master)

        for idx in range(7):
            self.grid_rowconfigure(   idx, weight=1)
            self.grid_columnconfigure(idx, weight=1)

        self.configure( bd=1, relief=SUNKEN)
        self.interpolatioModeList = [ " pytricubic", "map_coordinates"]
        self.formatList = [ "Nelder-Mead", "Powell", "CG", "BFGS", "Newton-CG", "L-BFGS-B", "TNC", "COBYLA", "SLSQP", "dogleg", "trust-ncg" ,"subPixelSearch"]
        self.createWidgets()
        centre_win( self )


    def createWidgets( self ):

        self.labelWidth = 20
        self.entryWidth = 15
        self.buttonWidth = 5

        currentRow = 0

        ### CC ###
        Label( self, text="Correlation Coefficient Parameters:" ).grid(row=currentRow, column=0, columnspan=2, padx=5, pady=(10,5))
        currentRow += 1

        Label( self, text="Max Refinement Step", width=self.labelWidth, anchor=W                                        ).grid( row=currentRow, column=0, sticky=W,   padx=5 )
        Entry( self, textvariable=self.master.variables['subpixel_CC_max_refinement_step'], width=self.entryWidth       ).grid( row=currentRow, column=1, sticky=W+E, padx=5, columnspan = 2 )
        currentRow += 1
        Label( self, text="Refinement Step Threshold", width=self.labelWidth, anchor=W                                  ).grid( row=currentRow, column=0, sticky=W,   padx=5 )
        Entry( self, textvariable=self.master.variables['subpixel_CC_refinement_step_threshold'], width=self.entryWidth ).grid( row=currentRow, column=1, sticky=W+E, padx=5, columnspan = 2 )
        currentRow += 1
        Label( self, text="Max Refinement Iterations", width=self.labelWidth, anchor=W                                  ).grid( row=currentRow, column=0, sticky=W,   padx=5 )
        Entry( self, textvariable=self.master.variables['subpixel_CC_max_refinement_iterations'], width=self.entryWidth ).grid( row=currentRow, column=1, sticky=W+E, padx=5 )
        currentRow += 1

        ### IMAGE INTERPOLATOR ###
        Label( self, text="Image Interpolator Parameters:" ).grid(row=currentRow, column=0, columnspan=2, padx=5, pady=(10,5))
        currentRow += 1

        Label( self, text="Interpolation Mode", width=self.labelWidth, anchor=W                                  ).grid( row=currentRow, column=0, sticky=W,   padx=5 )
        OptionMenu( self, self.master.variables['subpixel_II_interpolationMode'], *self.interpolatioModeList                ).grid( row=currentRow, column=1, sticky=W+E, padx=5, columnspan = 2 )
        currentRow += 1
        Label( self, text="Interpolation Order", width=self.labelWidth, anchor=W                                  ).grid( row=currentRow, column=0, sticky=W,   padx=5 )
        Entry( self, textvariable=self.master.variables['subpixel_II_interpolation_order'], width=self.entryWidth ).grid( row=currentRow, column=1, sticky=W+E, padx=5, columnspan = 2 )
        currentRow += 1
        Label( self, text="Optimisation Mode", width=self.labelWidth, anchor=W                                    ).grid( row=currentRow, column=0, sticky=W,   padx=5 )
        OptionMenu( self, self.master.variables['subpixel_II_optimisation_mode'], *self.formatList                ).grid( row=currentRow, column=1, sticky=W+E, padx=5, columnspan = 2 )
        currentRow += 1

        Button(self,text="Close",command=self.destroy).grid( row=currentRow, column=1, sticky=E, padx=5, pady=(10,5) )
        currentRow += 1