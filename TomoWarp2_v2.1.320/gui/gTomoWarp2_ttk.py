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

#!/usr/bin/env python


import os, sys, platform
from os.path import expanduser
from Tkinter import *
import Tkconstants, tkFileDialog, tkMessageBox, ttk

from guiFunctions import *
from Frames import *
from minimalFrame import *
from optionalFrame import *
from postprocFrame import *

from tools.print_variable import pv
from tools.input_parameters import input_parameters
from tools.input_parameters_read import input_parameters_read


def createFrames( root, data ):
    # Function that creates three tabs and the frame inside them
    root.tabs = ttk.Notebook( root )
    root.tabs.grid(row=0, column=0, sticky=E+W+S+N)
    
    # variables in data structure are assigned to the frame class to be available for internal functions
    Minimal_setup.data = data
    # the frame in created
    root.minimal = Minimal_setup(  master=root.tabs )
    # a tab is created for the frame
    root.tabs.add(root.minimal,  text='Required Parameters')

    # variables in data structure are assigned to the frame class to be available for internal functions
    Optional_setup.data = data
    # the frame in created
    root.optional = Optional_setup( master=root.tabs )
    # a tab is created for the frame
    root.tabs.add(root.optional, text='Optional Parameters')

    # variables in data structure are assigned to the frame class to be available for internal functions
    Postproc_setup.data = data
    # the frame in created
    root.postproc = Postproc_setup( master=root.tabs )
    # a tab is created for the frame
    root.tabs.add(root.postproc, text='Post Process')

    # A frame is created in the bottom of the main window to select between 2D image and 3D volume correlation
    # using the class the "ChooseImageDimensions" in Frames.py and the variable are updated
    root.imagesDim = ChooseImageDimensions(  master=root )
    root.imagesDim.grid( row=4, column=0, padx=5, pady=5  )
    ChooseImageDimensions.setvalues(root.imagesDim, root)
    


def defaultValues( root ):
    # Function that restore all the default values
    data = {}
    data = default_parameters( data )
    data = required_parameters( data )
    
    # If existing the frames are destroyed
    try:
      root.tabs.grid_remove()
      root.imagesDim.grid_remove()
    except:
      pass
    # Frames are created
    createFrames( root, data )

def loadFile( root, inputFile=None, data={} ):
    # Function that read an input file and update the variables in the GUI
    try:
        if inputFile==None: 
          inputFile = tkFileDialog.askopenfilename(parent=root, title='Choose a file', initialdir=root.homeDir)
        #if inputFile==None: inputFile = tkFileDialog.askopenfilename(parent=root, title='Choose a file', initialdir=root.minimal.variables['DIR_out'].get())
        if not ( inputFile=='' or inputFile == () ):
          root.homeDir =  os.path.dirname(inputFile)
          try: logging.log.info( pv( [inputFile], '', False ) ); 
          except: print pv( [inputFile], '', False )
          data = input_parameters_read( inputFile, data )
          data = required_parameters(data)
          # If existing the frames are destroyed
          try:
              root.tabs.grid_remove()
              root.imagesDim.grid_remove()
          except:
            pass
    except IOError as exc:
        try: logging.log.warning( exc ); 
        except: print exc
        ShowInfo( root, "TomoWarp2 Error", 'File not found' )
    except:
        try: logging.log.warning( 'File not recognized' ); 
        except: print 'File not recognized'
        ShowInfo( root, "TomoWarp2 Error", 'File not recognized' )
        
    # Frames are created
    if data=={}:
      defaultValues( root )
    else:
      createFrames( root, data )
        
def logSetup( root ):
    # Creates a new windows to set the logging preferences
    #   variables are store in Minimal_setup frame
    log_setup = Toplevel( root )
    width = 230
    height = 70
    #set the size of the window to width and height and centres it with the main window
    log_setup.geometry("%dx%d%+d%+d" % (width, height, root.winfo_x()+root.winfo_width()/2-width/2, root.winfo_y()+root.winfo_height()/2-height/2))
    # Button to choose if a logfile is required
    Checkbutton( log_setup, text = "Write log files"       , variable=Minimal_setup.variables['log2file']  ).grid(row=0, column=0, padx=15, pady=5, sticky=W)
    # Button to choose if log an error shoul be merged in one file
    Checkbutton( log_setup, text = "Join log and err files", variable=Minimal_setup.variables['jointFiles']).grid(row=1, column=0, padx=15, pady=5, sticky=W)


def buildGUI(inputfile=None, data={}):
    #Main function that creates the window with all the buttons and tabs
    
    root = Tk(className="TomoWarp2")
    root.title("TomoWarp2")
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=0)
    
    
    if platform.system() == 'Windows':
        root.wm_iconbitmap(default='%s/gui/TW2-icon.ico'%(sys.path[0]))
    else:
        iconfiles = ['%s/gui/TW2-icon%d%s' % (sys.path[0],size, '.gif') for size in (256, 128, 64, 48, 32, 16)]  
        icons = [PhotoImage(file=iconfile) for iconfile in iconfiles]
        root.call('wm', 'iconphoto', root._w, '-default', *icons)
    
    root.homeDir = expanduser( "~" )

    # a "data" structure is created either using default values or reading an input file
    #   these functions also call "createFrames" to create the tabs and frames
    if inputfile==None: 
      defaultValues( root )
    else:
      loadFile( root, inputfile, data )

    ## Attempt to insert a frame to redirect the console messages to the GUI
    #Messages(       master=root ).grid( row=3, column=0, sticky=E+W,   padx=5, pady=5  )
    
    # Button "Exit", "Save", and "Run" are create using a class in Frame.py
    ControlButton(  master=root ).grid( row=4, column=0, sticky=S+E,   padx=5, pady=5  )

    # Buttons that use function defined here also also created here
    buttons = Frame()
    buttons.grid( row=4, column=0, sticky=W,   padx=5, pady=5  )
    Button( buttons, text="Load input file", command=lambda: loadFile( root ) ).grid( row=0, column=0 )
    Button( buttons, text="Default values",  command=lambda: defaultValues( root ) ).grid( row=0, column=1 )
    Button( buttons, text="Log setup",  command=lambda: logSetup( root ) ).grid( row=0, column=2 )

    # The window is centred in the screen
    centre_win(root)
    root.wm_geometry("")
    
    # The GUI is run and waits for inputs
    root.mainloop()
    root.destroy

if __name__ == "__main__":

    argv = sys.argv[1:]

    try:
        opts, args = getopt.gnu_getopt(argv,"")
    except getopt.GetoptError as e:
        print (str(e))

    if len(args) != 0:
        inputfile = args[0]
    else:
        inputfile = None

    buildGUI( inputfile )
