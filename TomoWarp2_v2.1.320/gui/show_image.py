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

from Tkinter import *
from tools.tsv_tools import ReadTSV
import numpy
from colormap import Fire
from tools.print_variable import pv
import matplotlib.pyplot as plt

VERBOSE=False

class plot_component(Frame):
  """
  Function that plot an input matrix with its label and a colorbar with adjustable contrast
  """
  def __init__(self, master, data, labelText="", dataMin=None, dataMax=None):

      Frame.__init__(self, master)
        
      self.data_original = numpy.transpose( data.copy() )
      # If constrast limit are not passed they are set ot the min and max value of data matrix
      try:
        min_data = data[numpy.where( numpy.isfinite( data ) )].min() if (dataMin is None) else dataMin
        max_data = data[numpy.where( numpy.isfinite( data ) )].max() if (dataMax is None) else dataMax
      except ValueError:
        min_data = 0
        max_data = 254
      
      # If all the pixels have the same value they are set to zero otherwise values are 
      #   converted to 0-255 values where 255 represents Nan values and 0-254 is adjusted
      #   according to the contrast
      if not (max_data - min_data) == 0:
        data = ( self.data_original - min_data ) / ( max_data - min_data ) * 254
        with numpy.errstate(invalid='ignore'):
            data[numpy.where( data < 0   )] = 0
            data[numpy.where( data > 254 )] = 254
        data[numpy.where( numpy.isnan(data) )] = 255
      else:
        data = numpy.zeros_like(self.data_original)
     
      # Initialization of internal variables for dataMin and dataMax to update the image
      #   when the values are changed by the user
      self.dataMin = DoubleVar()
      self.dataMax = DoubleVar()
      self.dataMin.set(min_data)
      self.dataMax.set(max_data)
      self.dataMin.trace( 'w', self.adjust_contrast)
      self.dataMax.trace( 'w', self.adjust_contrast)
      
      # Variables to store dataMin and dataMax values so that it can be read from other functions
      self.dataMinFixed = dataMin
      self.dataMaxFixed = dataMax
      
      # Set colormap for the color bar 
      #  Fire is construct so that value 255, which correspond to NaNs, is ciano
      # TODO implement other colormaps
      self.colormap = Fire()

      currentRow=0
      currentCol=0
      
      # In the first row the label of the image is printed
      Label(self, text=labelText).grid( row=currentRow, column=currentCol, sticky=W+E, padx=5, pady=(0,10), columnspan=3)
      currentRow += 1
      
      ###############################################
      ###  Image of the data                      ###
      ###############################################
      # The image is stored in a PhotoImage and it is constructed by the function "built_im_tuple"
      self.im = PhotoImage(width=data.shape[0], height=data.shape[1])
      self.im.put( self.built_im_tuple( data ) )
      # The PhotoImage is inserted into a Label 
      self.w = Label(self, image=self.im, bd=0)
      self.w.grid( row=currentRow, column=currentCol, sticky=W+E, padx=5, pady=(0,10), columnspan=3)
      #self.w.image=self.im
      currentRow += 1
      
      ###############################################
      ###  Colorbar                               ###
      ###############################################
      # The colorbar is stored in a PhotoImage and it is constructed by the function "built_im_tuple"
      self.bar = PhotoImage(width=data.shape[0], height=1)
      # array containing a range of value 0-255 
      dataBar = numpy.array(range(data.shape[0])).astype('float')/data.shape[0]*255
      self.bar.put( self.built_im_tuple( dataBar ) )
      ###tkinter wants a list of pixel where each item is a tk colour specification (e.g. "#120432").  
      ###map the data to a list of strings with 3 components in hexadecimal, and convert the list to a tuple
      ###self.bar.put( (tuple(map(lambda v: "#%02x%02x%02x" % (self.colormap[v][1], self.colormap[v][2], self.colormap[v][3]), dataBar.astype('int') ) ),) )
      # set the hight of the bar to 1/10 of the length (which is the same as the image)
      self.bar = self.bar.zoom(1, max(data.shape[0]/10,5) )
      # The PhotoImage is inserted into a Label 
      self.wbar = Label(self, image=self.bar, bd=0)
      self.wbar.grid( row=currentRow, column=currentCol, sticky=W+E, columnspan=3)
      #self.wbar.image=self.bar
      currentRow += 1
      
      ###############################################
      ###  Contrast regulation entries            ###
      ###############################################
      self.dataMinEntry = Entry(self, textvariable=self.dataMin, width=5)
      self.dataMaxEntry = Entry(self, textvariable=self.dataMax, width=5)
      self.dataMinEntry.grid( row=currentRow, column=0, sticky=W, padx=5)
      self.dataMaxEntry.grid( row=currentRow, column=2, sticky=E, padx=5)
 
      
  def built_im_tuple( self, data ):
      # tkinter wants a list of pixel where each item is a tk colour specification (e.g. "#120432").  
      # map the data to a list of strings with 3 components in hexadecimal, and convert the list to a tuple      
      im_data = ()
      try:
        for i in range(data.shape[1]):
          im_data = im_data + (tuple (map(lambda v: "#%02x%02x%02x" % (self.colormap[v][1], self.colormap[v][2], self.colormap[v][3]), data[:,i].astype('int') ) ),)
      except IndexError:
          im_data = (tuple (map(lambda v: "#%02x%02x%02x" % (self.colormap[v][1], self.colormap[v][2], self.colormap[v][3]), data.astype('int') ) ),)

      return im_data
    
    
  def adjust_contrast( self, *args ):
    
    try:
      # Get new extreme values
      min_data = self.dataMin.get()
      max_data = self.dataMax.get()
      
      # Re-generate images value in range 0-255
      if not (max_data - min_data) == 0:
        new_data = ( self.data_original - min_data ) / ( max_data - min_data ) * 254
        with numpy.errstate(invalid='ignore'):
          new_data[numpy.where( new_data < 0   )] = 0
          new_data[numpy.where( new_data > 254 )] = 254
        new_data[numpy.where( numpy.isnan( new_data ) )] = 255
      else:
        new_data = numpy.zeros_like(self.data_original)

      # Re-build image with new values
      self.im.put( self.built_im_tuple( new_data ) )
      self.im_zoom = self.im.zoom(self.master.zoom, self.master.zoom)
      self.w.configure(image=self.im_zoom)

      # Variables to pass values to main function
      self.dataMinFixed = min_data
      self.dataMaxFixed = max_data
    
    except Exception as inst:
       if VERBOSE: print type(inst), inst.args
    

class plot_matrix(Frame):

  def plot_images( self, *args ):

    try:
        currentCol = self.currentCol
        # Get slicing plane
        plane = self.fieldList[self.slice_direction.get()]
        if self.images_2D:
          sliceNum=0
        else:
          # Update the max value to the slide bar 
          self.sliceScale.configure(to=self.matrix.shape[plane]-1)
          # Get the slice number and constrain it to accettable values
          sliceNum = max( min( self.sliceNum.get(), self.matrix.shape[plane]-1), 0)
          # Update slice entry to accettable values
          self.sliceNum.set(sliceNum)

        # For each component select the slice to plot from the general matrix
        for i_displ in range(self.images_2D, self.numberDisplacement):
            if plane == 0:
              data = numpy.squeeze(self.matrix[sliceNum,:,:,i_displ])
            elif plane == 1:
              data = numpy.squeeze(self.matrix[:,sliceNum,:,i_displ])
            elif plane == 2:
              data = numpy.squeeze(self.matrix[:,:,sliceNum,i_displ])    

            try:
                # If existing get min and max value fixed in "plot_component"
                self.dataMin[i_displ] = self.component[i_displ].dataMinFixed
                self.dataMax[i_displ] = self.component[i_displ].dataMaxFixed
                # Destroy the existing images 
                self.component[i_displ].destroy()
            except Exception as inst:
                pass
            
            # Plot the selected slice
            self.component[i_displ]=plot_component(self, data, self.labelText[i_displ], self.dataMin[i_displ], self.dataMax[i_displ] )
            self.component[i_displ].grid( row=self.currentRow, column=currentCol, sticky=W+E, padx=5, pady=(0,10))
            currentCol += 1
        
        # Reset the zoom to the user choice
        self.zoom_apply()
        
    except Exception as inst:
       if VERBOSE: print type(inst), inst.args

      
  def zoom_image_in( self ):
      self.zoom += 1
      self.zoom_apply()
      
  def zoom_image_out( self ):
      self.zoom -= 1
      self.zoom = max(self.zoom,1)
      self.zoom_apply()

  def zoom_apply( self ):
    """
    Function that update the images and the colorbars to the new zoom
    """
    for i_displ in range(self.images_2D, self.numberDisplacement):
      
      self.component[i_displ].im_zoom = self.component[i_displ].im.zoom(self.zoom, self.zoom)
      self.component[i_displ].w.configure(image=self.component[i_displ].im_zoom)
      #self.component[i_displ].w.image=self.component[i_displ].im_zoom
      
      self.component[i_displ].bar_zoom = self.component[i_displ].bar.zoom(self.zoom, 1)
      self.component[i_displ].wbar.configure(image=self.component[i_displ].bar_zoom)
      #self.component[i_displ].wbar.image=self.component[i_displ].bar_zoom
      
  def showHist( self ):
    """
    Function that plot in a new window the stack histograms of the three components
    """
    plt.close()
    for i_displ in range(self.images_2D, self.numberDisplacement):
      # generate a range of 100 values between the extremes values set for the contrast of each component
      bins = numpy.linspace(self.component[i_displ].dataMin.get(), self.component[i_displ].dataMax.get(), 100)
      # generate a subplot for each component
      eval("plt.subplot(13" + str(i_displ+1) + ")")
      plt.hist(numpy.ndarray.flatten(self.matrix[:,:,:,i_displ]),bins)
      plt.title(self.labelText[i_displ])
      plt.grid(True)
      
    plt.show()
      
  def __init__(self, master, matrix, images_2D=False):

      Frame.__init__(self, master)
      
      for idx in range(2):
        self.grid_rowconfigure(idx, weight=1)

      for idx in range(3):
          self.grid_columnconfigure(idx, weight=1)

      # Variable Initialization
      self.matrix = matrix
      self.images_2D = images_2D
      self.sliceNum = IntVar()
      self.slice_direction = StringVar()
      self.slice_direction.set('planeXY')
      self.fieldList = { 'planeXY':0, 'planeXZ':1, 'planeYZ':2 }
      self.labelText=['Z diplacements', 'Y diplacements', 'X diplacements']
      
      self.numberDisplacement = matrix.shape[3]
      self.component = [0]*self.numberDisplacement
      self.dataMin = [None]*self.numberDisplacement
      self.dataMax = [None]*self.numberDisplacement
      
      # The images are plotted each time the slice number of the place direction is changed
      self.sliceNum.trace( 'w', self.plot_images)
      self.slice_direction.trace( 'w', self.plot_images)    
      
      # Set the initial size of the images to at least 300 px
      self.zoom = max( 1, int(300/matrix.shape[2]))

      self.currentRow=0
      self.currentCol=0

      commandFrame = Frame(self)
      commandFrame.grid(row=self.currentRow, column=self.currentCol, sticky=W+E, columnspan=3)
      
      ###############################################
      ###  Zoom control                           ###
      ###############################################
      zoomFrame = Frame(commandFrame)
      zoomFrame.grid( row=0, column=0, sticky=W+E+S, padx=(0,25), pady=(0,10))
      Label( zoomFrame, text='Zoom:'                          ).grid( row=0, column=0, sticky=W+E )
      Button(zoomFrame, text="-", command=self.zoom_image_out ).grid( row=0, column=1, sticky=W+E )
      Button(zoomFrame, text="+", command=self.zoom_image_in  ).grid( row=0, column=2, sticky=W+E )

      ###############################################
      ###  Slice control                          ###
      ###############################################
      if not images_2D:
        sliceFrame = Frame(commandFrame)
        sliceFrame.grid( row=0, column=1, sticky=W+E+S, padx=25, pady=(0,10))
        # Selection of the slice number throught a slidebar or a text entry
        Label(sliceFrame, text='Slice number').grid(row=0, column=0, columnspan=2, sticky=W+E)
        self.sliceScale = Scale(sliceFrame, variable=self.sliceNum, from_=0, to=max(self.matrix.shape)-1, orient=HORIZONTAL, showvalue=False )
        self.sliceScale.grid( row=1, column=0, sticky=W+E )
        sliceEntry = Entry( sliceFrame, textvariable=self.sliceNum, width = 5 )
        sliceEntry.grid( row=1, column=1, sticky=W+E )
        # Selection of the slicing plane throught a menu
        OptionMenu( sliceFrame, self.slice_direction, *self.fieldList.keys() ).grid( row=1, column=2, sticky=W, padx=5 )
      
      ###############################################
      ###  Show Hitograms control                 ###
      ###############################################  
      Button( commandFrame, text="Show Stack Histograms", command=self.showHist ).grid( row=0, column=2, sticky=W+E+S, padx=(50,0), pady=(0,10) )
      self.currentRow += 1
      
      self.currentCol = 0
      # Setting the slice number will plot the images
      self.sliceNum.set(int(matrix.shape[0]/2))
