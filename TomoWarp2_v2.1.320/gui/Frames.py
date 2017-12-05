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

import os, sys, time
from Tkinter import *
import Tkconstants, tkFileDialog, tkMessageBox
import re, traceback

from guiFunctions import *
from minimalFrame import *
from optionalFrame import *
from postprocFrame import *

from tools.print_variable import pv
from tools.input_parameters import *
from tools.input_parameters_read import *

from tomowarp_runfile import tomowarp_runfile

class Messages(Frame):
    # Attempt to show the command line output in the GUI
    # NOTE NOT WORKING
    def __init__(self, master=None):

        Frame.__init__(self, master)
        self.varCheck = IntVar()
        self.createWidgets()

    def createWidgets(self):

        self.outputPanel = Text(self, wrap='word', height = 10, width=135)
        self.check = Checkbutton( self, text="Show/Hide output", variable=self.varCheck, command=self.ShowHide)
        self.check.grid( row=0, column=0, sticky=W )

    def ShowHide(self):

        if self.varCheck.get():
            self.outputPanel.grid(row=1, column=0)
            self.oldstdout = sys.stdout
            self.oldstderr = sys.stderr
            sys.stdout = StdoutRedirector(self.outputPanel)
            sys.stderr = StdoutRedirector(self.outputPanel)
            self.master.wm_geometry("")
            #m = re.match("(\d+)x(\d+)([-+]\d+)([-+]\d+)", self.master.geometry())
            #self.master.geometry("%sx%i%s%s"%(m.group(1), int(m.group(2))+self.heightIncrease, m.group(3), m.group(4)))
        else:
            self.outputPanel.grid_remove()
            sys.stdout = self.oldstdout
            sys.stderr = self.oldstderr
            self.master.wm_geometry("")
            #m = re.match("(\d+)x(\d+)([-+]\d+)([-+]\d+)", self.master.geometry())
            #self.master.geometry("%sx%i%s%s"%(m.group(1), int(m.group(2))-self.heightIncrease, m.group(3), m.group(4)))


class StdoutRedirector(object):
    # Attempt to show the command line output in the GUI
    # NOTE NOT WORKING
    def __init__(self, text_area):
        self.text_area = text_area

    def write(self, str):
        self.text_area.insert(END, str)
        self.text_area.see(END)

    def flush(self):
      pass

class ControlButton(Frame):
    # Frame with "Exit", "Save", and "Run" buttun with relative function
    
    ###############################################
    ###  Save function                          ###
    ###############################################  
    def save(self):
        # To save the input file "data" structure is updated with the value of all the variables in the frames
        data = update_variable( self.master.postproc, Postproc_setup.data )
        data = update_variable( self.master.minimal, data )
        data = update_variable( self.master.optional, data )

        self.message.set("Saving...")
        
        # location and file name are asked
        filename = tkFileDialog.asksaveasfilename(initialfile='DIC_input_parameters_DRAFT',defaultextension=".txt")
        # all the variable in data structure are saved in the file
        save_inputFile( filename, data )

        self.message.set("")
        ChooseImageDimensions.setvalues(self.master.imagesDim, self.master)

    ###############################################
    ###  Run function                           ###
    ###############################################  
    def run(self):
        try:
            # Before running the analysis "data" structure is updated with the value of all the variables in the frames
            data = update_variable( self.master.postproc, Postproc_setup.data )
            data = update_variable( self.master.minimal, data )
            data = update_variable( self.master.optional, data )

            self.message.set("Running...")
            
            # data structure is converted into a dictionary
            data = Bunch( data )
            
            try:
              if data.DIR_out:
                # if output directory does not exist it is created
                os.makedirs(data.DIR_out)
              else:
                # if output is not specified it is set to the current directory
                data.DIR_out = "."
            except OSError:
                if not os.path.isdir(data.DIR_out):
                  raise Exception('Check output directory')

            try:
              # Before running the analysis the program asks to save the input parameters
              filename = tkFileDialog.asksaveasfilename(initialfile='DIC_input_parameters',defaultextension=".txt", initialdir=self.master.minimal.variables['DIR_out'].get())
              save_inputFile( filename, data )
            except:
              raise Exception('Please select a file')

            # a static message is prompt until the analysis is done
            running=StaticMessage(self.master, 'Running...')
            # the analysis is started, the output kinematics is saved as variable in the postproc frame to show and filter results
            self.master.postproc.kinematics, outFile = tomowarp_runfile( data )
            running.destroy()
            # a message is prompt when the analysis is finished
            ShowInfo( self.master, 'TomoWarp2',' Congratulations!\nCorrelation completed' )
            # The output file variable in the post process tab is updated
            self.master.postproc.variables['file_kinematics'].set( outFile )

        except Exception as exc:
            # If an error is encountered the running message is destroyed and the error message is shown in a new windows and printed in the logfile 
            try: 
              running.destroy() 
            except: 
              pass
            ShowInfo( self.master, "TomoWarp2 Error", exc.message )
            try:
              logging.err.debug( traceback.format_exc() )
              logging.err.error( exc.message )
              logging.err.removeHandler(fh_err)
            except:
              print exc.message

        self.message.set("")
        ChooseImageDimensions.setvalues(self.master.imagesDim, self.master)

    def createWidgets(self):
        # A message is shown at the left of the buttons while saving or running
        self.messageLabel = Label( self, textvariable=self.message )
        self.messageLabel.grid( row=0, column=0, sticky=W )
        self.button_exit = Button(self,text="Exit",command= lambda: sys.exit('Good bye!!'))
        self.button_exit.grid( row=0, column=1 )
        self.button_run = Button(self,text="Save",command=self.save)
        self.button_run.grid( row=0, column=2 )
        self.button_run = Button(self,text="Run",command=self.run)
        self.button_run.grid( row=0, column=3 )

    def __init__(self, master=None):

        Frame.__init__(self, master)
        self.message = StringVar()
        self.createWidgets()

class ChooseImageDimensions(Frame):
    
    def setvalues(self, master):
        # If the analysis has to be run in 2D the variables has to assume specific values for the Z dimension
        #  this function set the variables to the correct values and disable the entries
        if master.postproc.variables['images_2D'].get()==1:
            ### Minimal Tab ###
            master.minimal.variables['Advanced'].set(1)
            Minimal_setup.Basic2Advance(master.minimal)
            master.minimal.variables['search_window'     ]['z low' ].set(0)
            master.minimal.variables['search_window'     ]['z high'].set(0)
            master.minimal.variables['correlation_window']['z'     ].set(0)
            master.minimal.variables['node_spacing'      ]['z'     ].set(1)
            master.minimal.winframe.SWEntry['z low'  ].config(state='disabled')
            master.minimal.winframe.SWEntry['z high' ].config(state='disabled')
            master.minimal.winframe.CWEntry['z'      ].config(state='disabled')
            master.minimal.winframe.NSEntry['z'      ].config(state='disabled')
            
            ### Optional Tab ###
            master.optional.variables['image_1_digits'].set(0)
            master.optional.variables['image_2_digits'].set(0)
            master.optional.variables['ROI_corners']['z low' ].set(0)
            master.optional.variables['ROI_corners']['z high'].set(0)
            master.optional.Dig1.config(state='disabled')                   
            master.optional.Dig2.config(state='disabled')
            master.optional.ROI1['z low'  ].config(state='disabled')
            master.optional.ROI1['z high' ].config(state='disabled')   
            
            ### Post Process Tab ###
            master.postproc.variables['saveStrain']['eps zz'].set(0)
            master.postproc.variables['saveStrain']['eps zy'].set(0)
            master.postproc.variables['saveStrain']['eps zx'].set(0)
            master.postproc.Str_zz.config(state='disabled')
            master.postproc.Str_zy.config(state='disabled')
            master.postproc.Str_zx.config(state='disabled')
        else:
            try:
                master.minimal.winframe.SWEntry['z low'  ].config(state='normal')
                master.minimal.winframe.SWEntry['z high' ].config(state='normal')
                master.minimal.winframe.CWEntry['z'      ].config(state='normal')
                master.minimal.winframe.NSEntry['z'      ].config(state='normal')
                master.optional.Dig1.config(state='normal')                   
                master.optional.Dig2.config(state='normal')
                master.optional.ROI1['z low'  ].config(state='normal')
                master.optional.ROI1['z high' ].config(state='normal')
                master.postproc.Str_zz.config(state='normal')
                master.postproc.Str_zy.config(state='normal')
                master.postproc.Str_zx.config(state='normal')   
            except:
                pass

    def __init__(self, master=None):

        Frame.__init__(self, master)
        
        self.images_2D = IntVar()
        self.images_2D.set(0)
        
        Label(self, text='Image dimensions:').grid( row=0, column=1 )
        Radiobutton(self, text="2D", variable=master.postproc.variables['images_2D'], value=1, command=lambda: self.setvalues(master)).grid( row=0, column=2 )
        Radiobutton(self, text="3D", variable=master.postproc.variables['images_2D'], value=0, command=lambda: self.setvalues(master)).grid( row=0, column=3 )