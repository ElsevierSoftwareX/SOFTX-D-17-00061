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

# -*- coding: utf-8 -*-
import os, sys
from os.path import expanduser
import logging
from Tkinter import *
import Tkconstants, tkFileDialog, tkMessageBox

from Frames import *
from guiFunctions import *
from minimalFrame import *
from optionalFrame import *

from tools.print_variable import pv
from tools.tsv_tools import ReadTSV, WriteTSV
from tools.calculate_node_spacing import calculate_node_spacing
from tools.kinematic_filters import kinematics_remove_outliers, kinematics_median_filter_fnc
from postproc.process_results import process_results, construct_mask
from show_image import plot_matrix


class Postproc_setup(Frame):

    variables = {}
    coordLabel = ( 'y', 'x' )
    strainLabel = ( 'eps zz', 'eps zy', 'eps zx', 'eps yy', 'eps yx', 'eps xx', 'Volumetric Strain', 'Max Shear Strain' )

    def choose_dir( self ):
      # Function to select a folder and set the corresponding variable
      initDir = self.variables['DIR_out'].get()
      if initDir == expanduser( "~" ) or initDir == '': initDir = self.master.master.homeDir
      chosenDir = tkFileDialog.askdirectory( parent=self.master, initialdir=initDir, title='Please select a directory' )
      self.variables['DIR_out'].set( chosenDir )
      self.master.master.homeDir = chosenDir

    def choose_file( self ):
      # Function to select an output file and set the corresponding variable
      initDir = os.path.dirname( self.variables['file_kinematics'].get() )
      if initDir == expanduser( "~" ) or initDir == "": initDir = self.master.master.homeDir
      file_kinematics = tkFileDialog.askopenfilename( parent=self.master, initialdir=initDir,\
            title='Please select DIC output file', filetypes = [ ("Output Files", "*.tsv"), ('All','*') ] )
      self.variables['file_kinematics'].set( file_kinematics )
      self.master.master.homeDir = os.path.dirname(file_kinematics)
        
    def createWidgets(self):

        # Set a standard size for widgets
        self.labelWidth = 0
        self.entryWidth = 15
        self.buttonWidth = 5

        currentRow = 0

        ### TITLE ###
        Label(self, text="Post Process Parameters", font=("bold")).grid(row=currentRow, column=0, columnspan=7, pady = 10 )
        currentRow += 1

        ### CC THRESHOLD ###
        Label( self, text="Correlation Coefficient Threshold", width=self.labelWidth, anchor=W      ).grid( row=currentRow, column=0, sticky=W,   padx=5 )
        Entry( self, textvariable=self.variables['cc_threshold'], width=self.entryWidth             ).grid( row=currentRow, column=1, sticky=W, padx=5 )
        ### OUTPUT FILE FORMAT ###
        Label( self, text="Save as", width=self.labelWidth, anchor=E                                ).grid( row=currentRow, column=2, sticky=W, padx=5, pady=(10,0) )
        Checkbutton(self, text='TIFF', variable=self.variables['saveTIFF']                          ).grid( row=currentRow, column=3, sticky=W, padx=5, pady=(10,0) )
        Checkbutton(self, text='RAW',  variable=self.variables['saveRAW']                           ).grid( row=currentRow, column=4, sticky=W, padx=5, pady=(10,0) )
        Checkbutton(self, text='VTK',  variable=self.variables['saveVTK']                           ).grid( row=currentRow, column=5, sticky=W, padx=5, pady=(10,0) )
        currentRow += 1

        ### STRAIN CALCULATION ###
        Checkbutton( self, text="Calculate Strain", variable=self.variables['calculate_strain']     ).grid( row=currentRow, column=0, sticky=W, padx=5, pady=(10,0) )
        Label( self, text="Strain Mode", width=self.labelWidth, anchor=E                            ).grid( row=currentRow, column=1, sticky=W, padx=5, pady=(10,0) )
        OptionMenu( self, self.variables['strain_mode'], *self.modeList                             ).grid( row=currentRow, column=2, sticky=W, padx=5, pady=(10,0) )
        currentRow += 1
        ### FILTERS ###
        Label( self, text="Remove Outliers:\tFilter Size", width=self.labelWidth, anchor=W             ).grid( row=currentRow, column=0, sticky=W,   padx=5, pady=(10,0) )
        Entry( self, textvariable=self.variables['remove_outliers_filter_size'], width=self.entryWidth ).grid( row=currentRow, column=1, sticky=W+E, padx=5, pady=(10,0) )
        Label( self, text="Threshold", width=self.labelWidth, anchor=W                                 ).grid( row=currentRow, column=2, sticky=E,   padx=5, pady=(10,0) )
        Entry( self, textvariable=self.variables['remove_outliers_threshold'], width=self.entryWidth   ).grid( row=currentRow, column=3, sticky=W+E, padx=5, pady=(10,0) )
        Checkbutton(self, text='absolut threshold', variable=self.variables['remove_outliers_absolut_threshold']    ).grid( row=currentRow, column=4, sticky=W, padx=5, pady=(10,0) )
        Checkbutton(self, text='Bright', variable=self.variables['remove_outliers_filter_high']        ).grid( row=currentRow, column=5, sticky=W, padx=5, pady=(10,0) )
        OptionMenu( self, self.filter_base_field_option, *self.fieldList.keys(), command=self.update_filter_base_field ).grid( row=currentRow, column=6, sticky=W, padx=5, pady=(10,0) )
        currentRow += 1
        Label( self, text="Median Filter:\tFilter Size", width=self.labelWidth, anchor=W         ).grid( row=currentRow, column=0, sticky=W,   padx=5, pady=(10,10) )
        Entry( self, textvariable=self.variables['kinematics_median_filter'], width=self.entryWidth ).grid( row=currentRow, column=1, sticky=W+E, padx=5, pady=(10,10) )
        currentRow += 1

        # Horizontal line
        Frame(self,height=1,width=50,bg="grey").grid(row=currentRow, columnspan=7, sticky=EW, pady=(0,10))
        currentRow += 1

        ### SAVE SELECTION ###
        Label( self, text="Save files for:", width=self.labelWidth, anchor=E ).grid( row=currentRow, column=0, columnspan=3, sticky=W, padx=5, pady=(0,10) )
        currentRow += 1
        Checkbutton( self, text="Displacements",          variable=self.variables['saveDispl']                       ).grid( row=currentRow,   column=0,  sticky=W, padx=5 )
        Checkbutton( self, text="Rotations",              variable=self.variables['saveRot']                         ).grid( row=currentRow+1, column=0,  sticky=W, padx=5 )
        Checkbutton( self, text="Rotations from strain",  variable=self.variables['saveRotFromStrain']               ).grid( row=currentRow+2, column=0,  sticky=W, padx=5 )
        self.Str_zz = Checkbutton( self, text=self.strainLabel[0], variable=self.variables['saveStrain'][self.strainLabel[0]] )
        self.Str_zz.grid( row=currentRow+2, column=3, sticky=W, padx=5, pady=(0,10) )
        self.Str_zy = Checkbutton( self, text=self.strainLabel[1], variable=self.variables['saveStrain'][self.strainLabel[1]] )
        self.Str_zy.grid( row=currentRow+2, column=2, sticky=W, padx=5, pady=(0,10) )
        self.Str_zx = Checkbutton( self, text=self.strainLabel[2], variable=self.variables['saveStrain'][self.strainLabel[2]] )
        self.Str_zx.grid( row=currentRow+2, column=1, sticky=W, padx=5, pady=(0,10) )
        Checkbutton( self, text=self.strainLabel[3], variable=self.variables['saveStrain'][self.strainLabel[3]] ).grid( row=currentRow+1, column=2, sticky=W, padx=5 )
        Checkbutton( self, text=self.strainLabel[4], variable=self.variables['saveStrain'][self.strainLabel[4]] ).grid( row=currentRow+1, column=1, sticky=W, padx=5 )
        Checkbutton( self, text=self.strainLabel[5], variable=self.variables['saveStrain'][self.strainLabel[5]] ).grid( row=currentRow,   column=1, sticky=W, padx=5 )
        Checkbutton( self, text=self.strainLabel[6], variable=self.variables['saveStrain'][self.strainLabel[6]] ).grid( row=currentRow,   column=4, sticky=W, padx=5 )
        Checkbutton( self, text=self.strainLabel[7], variable=self.variables['saveStrain'][self.strainLabel[7]] ).grid( row=currentRow+1, column=4, sticky=W, padx=5, pady=(0,10) )
        Checkbutton( self, text="Correlation Coefficient", variable=self.variables['saveCC']                    ).grid( row=currentRow,   column=5,  sticky=W, padx=5 )
        Checkbutton( self, text="Errors",            variable=self.variables['saveError']                       ).grid( row=currentRow+1, column=5,  sticky=W, padx=5 )
        Checkbutton( self, text="Mask",              variable=self.variables['saveMask']                        ).grid( row=currentRow+2, column=5,  sticky=W, padx=5 )
        currentRow += 3

        # Horizontal line
        Frame(self,height=1,width=50,bg="grey").grid(row=currentRow, columnspan=7, sticky=EW, pady=(10,10))
        currentRow += 1

        ### PIXEL SIZE CHANGE ###
        Label( self, text="Pixel Size Ratio", width=self.labelWidth, anchor=W                       ).grid( row=currentRow+1, column=0, sticky=W, padx=5 )
        Entry( self, textvariable=self.variables['pixel_size_ratio'], width=self.entryWidth         ).grid( row=currentRow+1, column=1, sticky=W, padx=5 )
        Label( self, text="Centre of the image", width=self.labelWidth, anchor=W                    ).grid( row=currentRow+1, column=2, sticky=W, padx=5 )
        entries_row(self, self.variables['image_centre'], currentRow+1, width=self.entryWidth, currentColumn=3)
        currentRow += 2

        # Horizontal line
        Frame(self,height=1,width=50,bg="grey").grid(row=currentRow, columnspan=7, sticky=EW, pady=(10,0))
        currentRow += 1

        ### KINEMATIC FILE NAME ###
        Label( self, text="DIC results file", width=self.labelWidth, anchor=W       ).grid( row=currentRow, column=0, sticky=W,   padx=5, pady=(30,0) )
        Entry( self, textvariable=self.variables['file_kinematics']                 ).grid( row=currentRow, column=1, sticky=W+E, padx=5, pady=(30,0), columnspan=5)
        Button(self, text="Browse",command=self.choose_file, width=self.buttonWidth ).grid( row=currentRow, column=6, sticky=W  , padx=5, pady=(30,0) )
        self.grid_rowconfigure(currentRow, pad=2)
        currentRow += 1

        ### OUTPUT FILE DIRECTORY ###
        Label( self, text="Output Directory", width=self.labelWidth, anchor=W      ).grid( row=currentRow, column=0, sticky=W  , padx=5 )
        Entry( self, textvariable=self.variables['DIR_out']                        ).grid( row=currentRow, column=1, sticky=W+E, padx=5, columnspan=5 )
        Button(self,text="Browse",command= self.choose_dir, width=self.buttonWidth ).grid( row=currentRow, column=6, sticky=W  , padx=5 )
        currentRow += 1

        ### OUTPUT FILE PREFIX ###
        Label( self, text="Output filename prefix", width=self.labelWidth, anchor=W ).grid( row=currentRow, column=0, sticky=W,   padx=5, pady=(0,10) )
        Entry( self, textvariable=self.variables['output_name']                          ).grid( row=currentRow, column=1, sticky=W+E, padx=5, pady=(0,10), columnspan=5)
        currentRow += 1

        ### COMMAND BUTTONS ###
        Button(self,text="Reload file",command=lambda: self.get_kinematics(True)).grid( row=currentRow, column=1, columnspan=2, sticky=W, padx=5, pady=10 )
        Button(self,text="show displacements",command=self.show_displacements).grid( row=currentRow, column=2, columnspan=2, sticky=W, padx=5, pady=10 )
        Button(self,text="Run Post Process",command=self.run).grid( row=currentRow, column=5, columnspan=2, sticky=W, padx=5, pady=10 )

    def creatVariables(self):

        ### VARIABLES DEFINITION FROM DATA STRUCTURE ###

        self.variables['file_kinematics'] = StringVar()
        self.variables['DIR_out']         = StringVar()
        self.variables['output_name']     = StringVar()
        self.filter_base_field_option     = StringVar()
        self.loaded_file = ''
        self.fieldList = { 'Z displacements':0, 'Y displacements':1, 'X displacements':2 }

        self.modeList = [ 'largeStrains', 'largeStrainsCentred', 'tetrahedralStrains', 'smallStrains']

        stringList = [ 'strain_mode']


        for field in stringList:
          self.variables[field] = StringVar()
          self.variables[field].set(self.data[field])

        intList = [ 'kinematics_median_filter', 'remove_outliers_filter_size', 'remove_outliers_threshold', 'remove_outliers_absolut_threshold', \
                    'remove_outliers_filter_high', 'filter_base_field', 'calculate_strain', 'saveDispl', 'saveRot', 'saveRotFromStrain', 'saveCC', \
                    'saveError', 'saveMask',  'saveTIFF', 'saveRAW', 'saveVTK', 'images_2D']

        for field in intList:
          self.variables[field] = IntVar()
          self.variables[field].set(self.data[field])
          
        if self.variables['images_2D']:
          self.filter_base_field_option.set('Y displacements')
        else:
          self.filter_base_field_option.set('Z displacements')

        floatList = ['cc_threshold', 'pixel_size_ratio']

        for field in floatList:
          self.variables[field] = DoubleVar()
          self.variables[field].set(self.data[field])

        dictionariesList = [ 'saveStrain' ]

        for dictField in dictionariesList:
          try:
              self.variables[dictField] = index2coord(self.data[dictField], self.strainLabel)
          except:
            self.variables[dictField]={}
            for field in self.strainLabel:
              self.variables[dictField][field] = IntVar()
              self.variables[dictField][field].set( self.data[dictField] )

        dictionariesList = ['image_centre']

        for dictField in dictionariesList:
          if type(self.data[dictField]) is list:
              self.variables['Advanced'].set(1)
              self.variables[dictField] = index2coord(self.data[dictField], self.coordLabel)
          else:
            self.variables[dictField]={}
            for field in self.coordLabel:
              self.variables[dictField][field] = IntVar()
              self.variables[dictField][field].set( self.data[dictField] )

        #dictionariesList = [ ]

        #for dictField in dictionariesList:
          #try:
                                    ## map+zip convert ROI_corners structure to [[zl,zh],[yl,yh],[xl,xh]]
              #self.variables[dictField] = index2coord( map( list, zip(*self.data[dictField]) ), self.coordLabelExt)
          #except:
            #self.variables[dictField]={}
            #for field in self.coordLabelExt:
              #self.variables[dictField][field] = IntVar()
              #self.variables[dictField][field].set( self.data[dictField] )
              
        self.variables[ 'file_kinematics'  ].trace( 'w', self.set_OUTPUT)


    def set_OUTPUT( self, *arg ):
      # This function update output directory and file prefix when output name is changed
        self.variables['DIR_out'].set( os.path.dirname( self.variables['file_kinematics'].get() ) )
        self.variables['output_name'].set( os.path.splitext( os.path.basename( self.variables['file_kinematics'].get() ) )[0] )
    
    def run( self ):
      # This function run the post process analysis
        
        # data structure is update to take into account the values in the gui
        data = update_variable( self, Postproc_setup.data )
        data = Bunch( data )
        # load the kinematic file if different from the last loaded
        self.get_kinematics()
        
        try:
          running=StaticMessage(self.master.master, 'Running Post Process...')
          # running the post process
          process_results(  self.kinematics.copy(), data )
        except Exception as exc:
          try: 
            logging.gui.debug( traceback.format_exc() )
            logging.gui.error( exc.message )
          except:
            print exc.message
          tkMessageBox.showinfo("TomoWarp2 Error", exc.message)
        running.destroy()

      
    def apply_filters( self ):
        # This function apply the filters on the loaded kinematic matrix from the show_displacements window
        
        running=StaticMessage(self.win_plots, 'Applying filters...')
        
        # The filter paramenters are gotten from the filter_control frame
        kinematics_median_filter            = self.filter_control.variables['kinematics_median_filter'         ].get()
        remove_outliers_filter_size         = self.filter_control.variables['remove_outliers_filter_size'      ].get()
        remove_outliers_threshold           = self.filter_control.variables['remove_outliers_threshold'        ].get()
        remove_outliers_absolut_threshold   = self.filter_control.variables['remove_outliers_absolut_threshold'].get()
        remove_outliers_filter_high         = self.filter_control.variables['remove_outliers_filter_high'      ].get()
        filter_base_field                   = self.filter_control.variables['filter_base_field'         ].get()
           
        # Remove outliers
        if remove_outliers_filter_size > 0:
            try: logging.gui.info("process_results(): Removing outliers"); 
            except: print "process_results(): Removing outliers"
            try:
                #kinematics[ :, 4:10 ] = kinematics_median_filter_fnc( kinematics[ :, 1:4 ], kinematics[ :, 4:10 ], kinematics_median_filter )
                [self.kinematics[ :, 4:10 ], mask_outliers] = kinematics_remove_outliers( self.kinematics[ :, 1:4 ], self.kinematics[ :, 4:10 ], \
                    remove_outliers_filter_size, remove_outliers_threshold, remove_outliers_absolut_threshold, remove_outliers_filter_high, filter_base_field )
                # if the filter assign a finit value to a point that had previously an error, thi is set to zero
                self.kinematics[ numpy.isfinite(self.kinematics[:,4]) , 11 ] = 0
                try: logging.gui.info("process_results(): Done!"); 
                except: print "process_results(): Done!"
            except Exception as exc:
                try: logging.gui.warn(exc.message); 
                except: print exc.message

        # filter kinematics...
        if kinematics_median_filter > 0:
            try:
              logging.gui.info("process_results(): Applying a Kinematics Median filter of {:0.1f} (3 means ±1)".format( kinematics_median_filter ))
            except:
              print "process_results(): Applying a Kinematics Median filter of {:0.1f} (3 means ±1)".format( kinematics_median_filter )
            try:
                self.kinematics[ :, 4:10 ] = kinematics_median_filter_fnc( self.kinematics[ :, 1:4 ], self.kinematics[ :, 4:10 ], kinematics_median_filter )
                # if the filter assign a finit value to a point that had previously an error, thi is set to zero
                self.kinematics[ numpy.isfinite(self.kinematics[:,4]) , 11 ] = 0
                try: logging.gui.info("process_results(): Done!"); 
                except: print "process_results(): Done!"
            except Exception as exc:
                try: logging.gui.warn(exc.message); 
                except: print exc.message
            
        intList = [ 'kinematics_median_filter', 'remove_outliers_filter_size', 'remove_outliers_threshold', 'remove_outliers_absolut_threshold', \
                    'remove_outliers_filter_high', 'filter_base_field']

        # The used paramenters are updated to the main window
        for field in intList:
          Postproc_setup.data[field] = self.filter_control.variables[field].get()
        self.master.master.postproc.filter_base_field_option.set( self.filter_control.variables['filter_base_field_option'].get() )
        
        # The show_displacements window is destroyed and created again
        running.destroy()
        self.win_plots.destroy()
        self.show_displacements()
    
    
    def get_kinematics( self, force=False ):
      # This function load a kinematic file and mask the matrix according to cc_threshold and errors
        if self.loaded_file != self.variables['file_kinematics'].get() or force:
            try:
              self.kinematics = ReadTSV( self.variables['file_kinematics'].get(),  "NodeNumber", [ "Zpos", "Ypos", "Xpos", "Zdisp", "Ydisp", "Xdisp",  "Zrot", "Yrot", "Xrot", "CC", "Error" ], [1,0] ).astype( '<f4' )
              mask = construct_mask( self.kinematics, self.variables['cc_threshold'].get() )
              for i in [ 4,5,6,7,8,9 ]: self.kinematics[ :, i ] += mask
              self.loaded_file = self.variables['file_kinematics'].get()
            except OSError:
              tkMessageBox.showinfo("TomoWarp2 Warning", "File doesn't exist")
      
    def save_kinematics( self ):
        try:
          initDir = os.path.dirname( self.variables['file_kinematics'].get() )
          if initDir == expanduser( "~" ) or initDir == "": initDir = self.master.master.homeDir
          outFile = tkFileDialog.asksaveasfilename(initialfile='%s_filtered'%(self.variables['output_name'].get()), \
              initialdir=initDir, defaultextension=".tsv", filetypes = [ ("Output Files", "*.tsv"), ('All','*') ])
        except:
            raise Exception('Please select a file') 
        WriteTSV( outFile, [ "NodeNumber", "Zpos", "Ypos", "Xpos", "Zdisp", "Ydisp", "Xdisp",  "Zrot", "Yrot", "Xrot", "CC", "Error" ], self.kinematics )
        #self.variables['output_name'].set('%s_filtered'%(self.variables['output_name'].get()))
        self.variables['file_kinematics'].set(outFile)
        self.set_OUTPUT()
        self.loaded_file = outFile
        self.master.master.homeDir = os.path.dirname(outFile)

    def show_displacements( self ):
        # This function create a new window to show the output displacements
        
        # load the kinematic file if different from the last loaded
        self.get_kinematics()
      
        number_of_nodes = self.kinematics.shape[0]
        nodes_z, nodes_y, nodes_x = calculate_node_spacing( self.kinematics[:,1:4] )
        displacements = self.kinematics[:,4:7]
        displacements = numpy.array( displacements.reshape( ( len( nodes_z ), len( nodes_y ), len( nodes_x ), 3 ) ) )
      
        self.win_plots=Toplevel(self.master)
        
        currentRow = 0
        currentCol = 0

        ### PLOT IMAGES ###
        # function in show_image.py that plot the displacements and command button for zoom, slice setting, and histograms plotting
        plot_matrix(self.win_plots, displacements, self.variables['images_2D'].get()).grid( row=currentRow, column=currentCol, sticky=W+E, padx=5, pady=(0,10), columnspan=5)
        currentRow += 1
        
        ### FILTERS ###
        # create a frame to control the filters paramenters
        self.filter_control = filterFrame( self.win_plots, self.variables['images_2D'].get() )
        self.filter_control.grid( row=currentRow, column=currentCol, sticky=W+E, padx=5, pady=(0,10), columnspan=5)
        currentRow += 1
        
        ### COMMAND BUTTONS ###
        filterBut = Button(self.win_plots, text="Apply Filters", command=self.apply_filters)
        filterBut.grid( row=currentRow, column=currentCol, sticky=W+E, padx=5, pady=(0,10))
        saveBut = Button(self.win_plots, text="Save Kinematics", command=self.save_kinematics)
        saveBut.grid( row=currentRow, column=currentCol+1, sticky=W+E, padx=5, pady=(0,10))
        saveBut = Button(self.win_plots, text="Close", command=self.win_plots.destroy)
        saveBut.grid( row=currentRow, column=currentCol+4, sticky=W+E, padx=5, pady=(0,10))
        currentRow += 1

        # centre the window on the main one
        self.win_plots.update_idletasks()
        width = self.win_plots.winfo_width()
        height = self.win_plots.winfo_height()
        self.win_plots.geometry("%dx%d%+d%+d" % (width, height, self.master.master.winfo_x()+self.master.master.winfo_width()/2-width/2, self.master.master.winfo_y()+self.master.master.winfo_height()/2-height/2))
        self.win_plots.geometry('')
        
    def update_filter_base_field( self, *args ):
      # Probably useless
        self.variables['filter_base_field'].set(self.fieldList[self.filter_base_field_option.get()])

    def __init__(self, master=None):

        Frame.__init__(self, master)


        for idx in range(4):
          self.grid_rowconfigure(idx, weight=1)
        for idx in range(5,12):
          self.grid_rowconfigure(idx, weight=1)

        for idx in range(5):
            self.grid_columnconfigure(idx, weight=1)
        for idx in range(6,7):
            self.grid_columnconfigure(idx, weight=5)
        self.configure( bd=1, relief=SUNKEN)

        self.creatVariables()
        self.createWidgets()


class filterFrame(Frame):
    # create a frame to control the filters paramenters

    def __init__(self, master, images_2D):

        Frame.__init__(self, master)

        ### VARIABLES DEFINITION ###
        if images_2D:
          self.fieldList = { 'Y displacements':1, 'X displacements':2 }
        else:
          self.fieldList = { 'Z displacements':0, 'Y displacements':1, 'X displacements':2 }
        
        intList = [ 'kinematics_median_filter', 'remove_outliers_filter_size', 'remove_outliers_absolut_threshold', \
                    'remove_outliers_filter_high', 'filter_base_field']
        
        self.variables={}
        for field in intList:
          self.variables[field] = IntVar()
          self.variables[field].set(Postproc_setup.data[field])
          
        self.variables['remove_outliers_threshold']=DoubleVar()
        self.variables['remove_outliers_threshold'].set(Postproc_setup.data['remove_outliers_threshold'])
        
        self.variables['filter_base_field_option']=StringVar()
        self.variables['filter_base_field_option'].set(self.master.master.master.postproc.filter_base_field_option.get())
        
        # Set a standard size for widgets
        self.labelWidth = 0
        self.entryWidth = 15  
        currentRow = 0
        
        # Remove Outliers
        Label( self, text="Remove Outliers:\tFilter Size", width=self.labelWidth, anchor=W             ).grid( row=currentRow, column=1, sticky=W,   padx=5, pady=(10,0) )
        Entry( self, textvariable=self.variables['remove_outliers_filter_size'], width=self.entryWidth ).grid( row=currentRow, column=2, sticky=W+E, padx=5, pady=(10,0) )
        Label( self, text="Threshold", width=self.labelWidth, anchor=W                                 ).grid( row=currentRow, column=3, sticky=E,   padx=5, pady=(10,0) )
        Entry( self, textvariable=self.variables['remove_outliers_threshold'], width=self.entryWidth   ).grid( row=currentRow, column=4, sticky=W+E, padx=5, pady=(10,0) )
        Checkbutton(self, text='absolut threshold', variable=self.variables['remove_outliers_absolut_threshold']    ).grid( row=currentRow, column=5, sticky=W, padx=5, pady=(10,0) )
        Checkbutton(self, text='Bright', variable=self.variables['remove_outliers_filter_high']        ).grid( row=currentRow, column=6, sticky=W, padx=5, pady=(10,0) )
        OptionMenu( self, self.variables['filter_base_field_option'], *self.fieldList.keys(), command=self.update_filter_base_field ).grid( row=currentRow, column=7, sticky=W, padx=5, pady=(10,0) )
        currentRow += 1

        # Median Filter
        Label( self, text="Median Filter:\tFilter Size", width=self.labelWidth, anchor=W         ).grid( row=currentRow, column=1, sticky=W,   padx=5, pady=(10,10) )
        Entry( self, textvariable=self.variables['kinematics_median_filter'], width=self.entryWidth ).grid( row=currentRow, column=2, sticky=W+E, padx=5, pady=(10,10) )
        
    def update_filter_base_field( self, *args ):
        self.variables['filter_base_field'].set(self.fieldList[self.variables['filter_base_field_option'].get()])