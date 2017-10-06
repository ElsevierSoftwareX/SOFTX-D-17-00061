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
from optionalFrame import *

from tools.print_variable import pv


class Minimal_setup(Frame):

    # Definition of coordinates dimensions label
    coordLabelExt = ( 'z low', 'z high', 'y low', 'y high', 'x low', 'x high' )
    coordLabel = ( 'z', 'y', 'x' )
    coordLabelRid = ( 'y', 'x' )
    variables = {}

    def choose_dir(self,var):
      # Function to select a folder and set the corresponding variable
      initDir = self.variables[var].get()
      if initDir == expanduser( "~" ): initDir = self.master.master.homeDir
      chosenDir = tkFileDialog.askdirectory( parent=self.master, initialdir=initDir, title='Please select a directory' )
      self.variables[var].set( chosenDir )
      self.master.master.homeDir = chosenDir

    def createWidgets(self):
        # Set a standard size for widgets
        self.labelWidth = 15
        self.entryWidth = 15
        self.buttonWidth = 5

        currentRow = 0
        
        ### TITLE ###
        Label(self, text="Required Parameters", font=("bold")).grid(row=currentRow, column=0, columnspan=3, pady = 10 )
        currentRow += 1

        ### INPUT FOLDER 1 ###
        Label( self, text="Image 1 Directory", width=self.labelWidth, anchor=W                            ).grid( row=currentRow, column=0, sticky=W  , padx=5 )
        Entry( self, textvariable=self.variables['DIR_image1']                                            ).grid( row=currentRow, column=1, sticky=W+E, padx=5 )
        Button(self,text="Browse",command= lambda: self.choose_dir('DIR_image1'), width=self.buttonWidth  ).grid( row=currentRow, column=2, sticky=E  , padx=5 )
        currentRow += 1

        ### INPUT FOLDER 2 ###
        Label( self, text="Image 2 Directory", width=self.labelWidth, anchor=W                            ).grid( row=currentRow, column=0, sticky=W  , padx=5 )
        Entry( self, textvariable=self.variables['DIR_image2']                                            ).grid( row=currentRow, column=1, sticky=W+E, padx=5 )
        Button(self,text="Browse",command= lambda: self.choose_dir('DIR_image2'), width=self.buttonWidth  ).grid( row=currentRow, column=2, sticky=E  , padx=5 )
        currentRow += 1

        ### OUTPUT FOLDER ###
        Label( self, text="Output Directory", width=self.labelWidth, anchor=W                             ).grid( row=currentRow, column=0, sticky=W  , padx=5 )
        Entry( self, textvariable=self.variables['DIR_out']                                               ).grid( row=currentRow, column=1, sticky=W+E, padx=5 )
        Button(self,text="Browse",command= lambda: self.choose_dir('DIR_out'), width=self.buttonWidth     ).grid( row=currentRow, column=2, sticky=E  , padx=5 )
        currentRow += 1

        ### DVC PARAMETERS ###
        # Basic2Advance function create a frame with entries for search_window, correlation_window, and, node_spacing
        self.Basic2Advance()
        currentRow += 1
        self.checkAdvance =  Checkbutton( self, text="Avanced input mode", variable=self.variables['Advanced'], command=self.Basic2Advance)
        self.checkAdvance.grid( row=currentRow, column=0, columnspan=2, sticky=W)
        currentRow += 1

        ### IMAGE FORMAT ###
        Label( self, text="Image Format", width=self.labelWidth, anchor=W                                      ).grid( row=currentRow, column=0, sticky=W, padx=5 )
        OptionMenu( self, self.variables['image_format'], *self.extDict.keys(), command=self.imageFormatChange ).grid( row=currentRow, column=1, sticky=W, padx=5 )
        self.imageFormatChange( self.variables['image_format'].get() )
        currentRow += 1

    def imageFormatChange(self, option):

        # in extDict each image format is associated to a extension. This is update to the optional tab 
        try: Optional_setup.variables['image_ext'].set( self.extDict[option] )
        except: pass

        if option == 'RAW':
          # If RAW is chosen the image size and data format has to be specified as well
            self.imageSpecFrame = imageSpec( master=self )
            self.imageSpecFrame.grid( row=7, column=0, columnspan=7, sticky=E+W, pady=5 )
        else:
            try:
              self.imageSpecFrame.destroy()
            except:
              pass

    def redefineVariables(self, *args):
      # when changing from simple to advanced mode the single value is copied in all the directions
      
      if not self.variables['Advanced'].get():      
          try:
            srcWin = abs( self.variables['search_window'      ][ self.coordLabelExt[1] ].get() )
            for field in self.coordLabelExt:
                if 'low' in field and srcWin is not None:
                    self.variables['search_window'][field].set( - srcWin )
                else:
                    self.variables['search_window'][field].set(   srcWin )
          except ValueError:
            pass
          
          try:
            corWin = abs( self.variables['correlation_window' ][ self.coordLabel[0] ].get() )
            for field in self.coordLabel:
                    self.variables['correlation_window'][field].set( corWin )
          except ValueError:
            pass
          
          try:
            nsp = abs( self.variables['node_spacing'          ][ self.coordLabel[0] ].get() )
            for field in self.coordLabel:
                    self.variables['node_spacing'][field].set( nsp )
          except ValueError:
            pass

    def Basic2Advance(self, *args):
      # This function destroy and recreate the frame with the DVCparameters (SW, CW, and NP)
        try: self.winframe.destroy()
        except: pass

        self.redefineVariables()
        self.winframe = DVCparameters(master=self)
        self.winframe.grid(row=4, column=0, columnspan=7, sticky=E+W, pady=5)
        
    
    def buid_ouputfilename(self, *args ):
      # To update the output name the variable "name_prefix" is set equal to itself 
      try:
        from optionalFrame import Optional_setup
        Optional_setup.variables['name_prefix'].set( Optional_setup.variables['name_prefix'].get() )
      except:
        pass
      

    def creatVariables(self):

        ### VARIABLES DEFINITION FROM DATA STRUCTURE ###

        self.variables['Advanced'] = IntVar()

        self.extDict = {'auto':'', 'TIFF':"\.[Tt][iI][Ff]{1,2}", 'RAW':'', 'EDF':"\.[Ee][De][Ff]", 'TIFF_PIL':"\.[Tt][iI][Ff]{1,2}"}

        stringList = ['DIR_image1','DIR_image2', 'DIR_out', 'image_format', 'image_data_format' ]

        for field in stringList:
          self.variables[field] = StringVar()
          self.variables[field].set(self.data[field])

        intList = ['log2file', 'jointFiles']

        for field in intList:
          self.variables[field] = IntVar()
          self.variables[field].set(self.data[field])

        dictionariesList = [ 'image_1_size', 'image_2_size']

        for dictField in dictionariesList:
          try:
              self.variables[dictField] = index2coord(self.data[dictField], self.coordLabel)
          except ( IndexError ):
              self.variables[dictField] = index2coord(self.data[dictField], self.coordLabelRid)
          except ( IndexError, TypeError ):
            self.variables[dictField]={}
            for field in self.coordLabel:
              self.variables[dictField][field] = IntVar()
              self.variables[dictField][field].set( self.data[dictField] )

        dictionariesList = ['correlation_window', 'node_spacing']

        for dictField in dictionariesList:
          try:
              self.variables[dictField] = index2coord(self.data[dictField], self.coordLabel)
              self.variables['Advanced'].set(1)
          except:
            self.variables[dictField]={}
            for field in self.coordLabel:
              self.variables[dictField][field] = IntVar()
              self.variables[dictField][field].set( self.data[dictField] )

        dictionariesList = ['search_window']

        for dictField in dictionariesList:
          try:
              self.variables[dictField] = index2coord(self.data[dictField], self.coordLabelExt)
              self.variables['Advanced'].set(1)
          except:
              self.variables[dictField]={}
              for field in self.coordLabelExt:
                self.variables[dictField][field] = IntVar()
                if 'low' in field and self.data[dictField] is not None:
                    self.variables[dictField][field].set( -self.data[dictField] )
                else:
                    self.variables[dictField][field].set( self.data[dictField] )

        # When one of thee variable is changed an action is taken
        self.variables[ 'node_spacing' ][ 'y' ].trace( 'w', self.buid_ouputfilename)
        self.variables[ 'node_spacing'       ][ self.coordLabel[0] ].trace( 'w', self.redefineVariables)
        self.variables[ 'correlation_window' ][ self.coordLabel[0] ].trace( 'w', self.redefineVariables)
        self.variables[ 'search_window'      ][ self.coordLabelExt[1] ].trace( 'w', self.redefineVariables)


    def __init__(self, master=None):

        Frame.__init__(self, master)

        for idx in range(6):
            self.grid_rowconfigure(   idx, weight=1)
            self.grid_columnconfigure(idx, weight=0)
        for idx in range(6,9):
            self.grid_rowconfigure(   idx, weight=10)
        self.grid_columnconfigure(1, weight=1)
        self.configure( bd=1, relief=SUNKEN)

        self.creatVariables()
        self.createWidgets()


class DVCparameters(Frame):
    # Frame with one or several entries for each DVC parameter
    def __init__(self, master=None):

      Frame.__init__(self, master)
      self.grid_columnconfigure(1, weight=0)
      for col in range(1,7):
          self.grid_columnconfigure(col, weight=1)

      currentRow = 0

      if self.master.variables['Advanced'].get():
        Label( self, text="Search Window", width=master.labelWidth, anchor=W      ).grid( row=currentRow+1, column=0, sticky=W, padx=5 )
        self.SWEntry = entries_row(self, master.variables['search_window'],      currentRow+1, width=master.entryWidth)
        currentRow += 2
        Label( self, text="Correlation Window", width=master.labelWidth, anchor=W ).grid( row=currentRow+1, column=0, sticky=W, padx=5 )
        self.CWEntry = entries_row(self, master.variables['correlation_window'], currentRow+1, width=master.entryWidth)
        currentRow += 2
        Label( self, text="Node Spacing", width=master.labelWidth, anchor=W       ).grid( row=currentRow,   column=0, sticky=W, padx=5 )
        self.NSEntry = entries_row(self, master.variables['node_spacing'],       currentRow, width=master.entryWidth, pritnLabel=False)
      else:
        Label( self, text="Search Window", width=master.labelWidth, anchor=W                                            ).grid( row=currentRow, column=0, sticky=W, padx=5 )
        Entry(self, width=master.entryWidth, textvariable=master.variables['search_window'][master.coordLabelExt[1]]    ).grid( row=currentRow, column=1, sticky=W, padx=5 )
        currentRow += 1
        Label( self, text="Correlation Window", width=master.labelWidth, anchor=W                                       ).grid( row=currentRow, column=0, sticky=W, padx=5 )
        Entry(self, width=master.entryWidth, textvariable=master.variables['correlation_window'][master.coordLabel[0]]  ).grid( row=currentRow, column=1, sticky=W, padx=5 )
        currentRow += 1
        Label( self, text="Node Spacing", width=master.labelWidth, anchor=W                                             ).grid( row=currentRow, column=0, sticky=W, padx=5 )
        Entry(self, width=master.entryWidth, textvariable=master.variables['node_spacing'][master.coordLabel[0]]        ).grid( row=currentRow, column=1, sticky=W, padx=5 )
            

class imageSpec(Frame):
    # Frame to specify image size and image data format when RAW images are selected
    def __init__(self, master=None):

        Frame.__init__(self, master)
        for col in range(7):
            self.grid_columnconfigure(col, weight=1)

        self.dataFormat = StringVar(self, 'Custom')
        self.littleEndian= StringVar(self, '<')
        self.formatDict = {'8-bit':'i1', '16-bit Signed':"i2", '16-bit Unsigned':'u2', '32-bit Signed':'i4',\
                            '32-bit Unsigned':'u4', '32-bit Real':'f4', '64-bit Real':'f8', 'Custom':''}

        ### IMAGE SIZE ###
        Label(self, text="Image Size:", width=master.labelWidth, anchor=W ).grid(row=0, column=0, sticky=W, padx=5 )
        Label(self, text="Image 1:"   , width=master.labelWidth, anchor=W ).grid(row=1, column=0, sticky=W, padx=5 )
        Label(self, text="Image 2:"   , width=master.labelWidth, anchor=W ).grid(row=2, column=0, sticky=W, padx=5 )
        entries_row(self, master.variables['image_1_size'], 1, width=master.entryWidth )
        entries_row(self, master.variables['image_2_size'], 2, width=master.entryWidth, pritnLabel=False )

        Label(self, text=" ", width=master.labelWidth).grid(row=1, column=5)

        ### IMAGE DATA FORMAT ###
        Label(self, text="Image data format:", width=master.labelWidth).grid(row=1, column=6, sticky=W, padx=5 )
        OptionMenu(   self, self.dataFormat, *self.formatDict.keys(), command=self.imageFormat).grid(row=1, column=7, sticky=E+W, padx=5 )
        Checkbutton(  self, text="Little-endian byte order", variable=self.littleEndian, onvalue='<', offvalue='>', \
                      command=lambda: self.imageFormat(self.dataFormat.get())).grid(row=2, column=6, sticky=W,)
        self.dataFormatEntry = Entry(self, width=master.entryWidth, textvariable=master.variables['image_data_format'])
        self.dataFormatEntry.grid(row=2, column=7, sticky=W, padx=5 )

    def imageFormat( self, option):

        if option == 'Custom': self.dataFormatEntry.config( state='normal')
        else:                  self.dataFormatEntry.config( state='disabled')
        self.master.variables['image_data_format'].set( self.littleEndian.get() + self.formatDict[option] )
