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


import os, sys
from Tkinter import *
import Tkconstants, tkFileDialog, tkMessageBox

from guiFunctions import *
from Frames import *
from minimalFrame import *
from optionalFrame import *
from postprocFrame import *

from TomoWarp2 import tomowarp_runfile

from tools.print_variable import pv
from tools.input_parameters import input_parameters
from tools.input_parameters_read import input_parameters_read


def createFrames( root, data ):

    Minimal_setup.data = data
    root.minimal = Minimal_setup(  master=root )
    root.minimal.grid( row=1, column=0, sticky=N+E+W+S, padx=5, pady=5  )
    ShowHideOpt( root.minCheck.get(), root.minimal )

    Optional_setup.data = data
    root.optional = Optional_setup( master=root )
    root.optional.grid( row=3, column=0, sticky=N+E+W+S, padx=5)
    ShowHideOpt( root.optCheck.get(), root.optional )

    Postproc_setup.data = data
    root.postproc = Postproc_setup( master=root )
    root.postproc.grid( row=5, column=0, sticky=N+E+W+S, padx=5)
    ShowHideOpt( root.ppCheck.get(), root.postproc )

def defaultValues( root ):

    data = {}
    data = default_parameters( data )
    data = required_parameters(data)
    try:
      root.minimal.grid_remove()
      root.optional.grid_remove()
    except:
      pass
    createFrames( root, data )

def loadFile( root, inputFile=None ):

    if inputFile==None: inputFile = tkFileDialog.askopenfilename(parent=root, title='Choose a file')
    pv( [inputFile], '', False )
    try:
        data = input_parameters_read( inputFile )
        data = required_parameters(data)
    except:
        print 'File not recognized'
        raise
    root.minimal.grid_remove()
    root.optional.grid_remove()
    createFrames( root, data )

def ShowHideOpt( var, frame, frame2=None, frame3=None ):

    if not frame2==None:
      frame2[0].set(0)
      frame2[1].grid_remove()
    if not frame3==None:
      frame3[0].set(0)
      frame3[1].grid_remove()

    if var:
        frame.grid( )
        #root.optional.grid( row=2, column=0, sticky=N+E+W, padx=5)
    else:
        frame.grid_remove()


def buildGUI( inputfile=None ):

    root = Tk()
    root.title("TomoWarp2")
    for idx in range(7):
        root.grid_rowconfigure(   idx, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=0)

    root.minCheck = IntVar(root,1)
    root.optCheck = IntVar(root,0)
    root.ppCheck = IntVar(root,0)

    defaultValues( root )
    if not inputfile==None: loadFile( root, inputfile )

    currentRow=0
    Checkbutton( root, text="Show/Hide Minimal Parameters", variable=root.minCheck, command=lambda: \
                                ShowHideOpt( root.minCheck.get(), root.minimal,  [root.optCheck, root.optional], [root.ppCheck, root.postproc] ) \
                                ).grid( row=currentRow, column=0, sticky=W, padx=5, pady=5 )
    currentRow += 2
    Checkbutton( root, text="Show/Hide Optional Parameters", variable=root.optCheck, command=lambda: \
                                ShowHideOpt( root.optCheck.get(), root.optional, [root.minCheck, root.minimal], [root.ppCheck, root.postproc] )  \
                                ).grid( row=currentRow, column=0, sticky=W, padx=5, pady=5 )
    currentRow += 2
    Checkbutton( root, text="Show/Hide Post Process", variable=root.ppCheck,  command=lambda:              \
                                ShowHideOpt( root.ppCheck.get(), root.postproc,  [root.minCheck, root.minimal], [root.optCheck, root.optional] ) \
                                ).grid( row=currentRow, column=0, sticky=W, padx=5, pady=5 )
    currentRow += 2
    #Messages(       master=root ).grid( row=5, column=0, sticky=E+W,   padx=5, pady=5  )
    ControlButton(  master=root ).grid( row=currentRow, column=0, sticky=S+E,   padx=5, pady=5  )

    buttons = Frame()
    buttons.grid( row=currentRow, column=0, sticky=W,   padx=5, pady=5  )
    Button( buttons, text="Load input file", command=lambda: loadFile( root, inputfile ) ).grid( row=0, column=0 )
    Button( buttons, text="Default values",  command=lambda: defaultValues( root ) ).grid( row=0, column=1 )
    
    ChooseImageDimensions(  master=root ).grid( row=4, column=0, padx=5, pady=5  )

    centre_win(root)
    root.wm_geometry("")
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
