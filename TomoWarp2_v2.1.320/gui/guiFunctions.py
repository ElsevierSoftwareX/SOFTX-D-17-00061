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
from Tkinter import *
import tkFileDialog
from PIL import Image, ImageTk
import numpy

from tools.print_variable import pv


class Bunch(dict):
    def __init__(self, kw):
        dict.__init__(self, kw)
        self.__dict__ = self

    def __getstate__(self):
        return self

    def __setstate__(self, state):
        self.update(state)
        self.__dict__ = self

def save_inputFile(filename, data):
    # Function that save all the variables in data structure in a text file
    parametersFile = open(filename, 'w') # wb is important
    for key in sorted( data.iterkeys() ):
        string = pv([data[key]],'',False,key,False)+"\n"
        parametersFile.write(string)
    parametersFile.close


def entries_row(win, variable, currentRow, pritnLabel=True, width=15, currentColumn=1):
    # Function that generates a row of entries, one for each item in the variable list
    #  optionally it prints in a previous row a label, with the field name, for each entry
    entries = {}
    for field in sorted(variable, reverse=True):
        if pritnLabel:
          lab = Label(win, width=width, text=field+": ", anchor='w')
          lab.grid(row=currentRow-1, column=currentColumn)
        ent = Entry(win, width=width, textvariable=variable[field])
        ent.grid(row=currentRow, column=currentColumn, sticky=W+E, padx=5)
        entries[field] = ent
        currentColumn += 1
    return entries

def centre_win(win, winsize = None):
    # Function that centre a window on the screen and optionally changes its size
    win.update_idletasks()

    if winsize is None:
      width = win.winfo_width()
      height = win.winfo_height()
    else:
      width  = winsize[0]
      height = winsize[1]
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()




def coord2index(varCoord, fields):
    # Variable list in the GUI are saved as dictionary where the fields are the coordinates
    #  This function transform dictionaries into list
    if len(varCoord) == 6:

        varIndex = [[None, None], [None, None], [None, None]]
        varIndex[0][0] = varCoord[ fields[0] ].get()
        varIndex[0][1] = varCoord[ fields[1] ].get()
        varIndex[1][0] = varCoord[ fields[2] ].get()
        varIndex[1][1] = varCoord[ fields[3] ].get()
        varIndex[2][0] = varCoord[ fields[4] ].get()
        varIndex[2][1] = varCoord[ fields[5] ].get()

    else:

        varIndex = []
        for field in fields:
            varIndex.append( varCoord[ field ].get() )

    return varIndex




def index2coord(varIndex, fields):
    # Variable list in the GUI are saved as dictionary where the fields are the coordinates 
    #  This function transform list into dictionaries
    varCoord={}
    for field in fields:
        varCoord[field] = IntVar()

    if len(fields) == 6:

        varCoord[ fields[0] ].set( varIndex[0][0] )
        varCoord[ fields[1] ].set( varIndex[0][1] )
        varCoord[ fields[2] ].set( varIndex[1][0] )
        varCoord[ fields[3] ].set( varIndex[1][1] )
        varCoord[ fields[4] ].set( varIndex[2][0] )
        varCoord[ fields[5] ].set( varIndex[2][1] )

    else:

      for idx, field in enumerate(fields):

        varCoord[ field ].set( varIndex[idx] )

    return varCoord




def update_variable(app, data):
    # Function that store variables in the frame "app" into the data structure
    try:
      # If app is the minimal_frame the SW, CW and NS are converted in list
      app.Basic2Advance()
    except:
      pass

    for varName in app.variables:
        try:
            if type(app.variables[varName]) is dict:
                var = {}
                data[varName] = coord2index(app.variables[varName], sorted(app.variables[varName], reverse=True))
            else:
                data[varName] = app.variables[varName].get()
            # prior_file cannot be a voide string
            if data['prior_file'] == 'None' or data['prior_file'] == '': data['prior_file'] = None
        except ValueError as errorString:
            if 'None' in errorString.message:
                data[varName] = None
            elif 'auto' in errorString.message:
                data[varName] = 'auto'
            else:
                raise Exception("something went wrong with variable: %s"%(varName))

    if data['ROI_corners'] is not None: data['ROI_corners'] = map( list, zip(*data['ROI_corners']) )
    try:
      # If RAW images are slices size in Z are set to 0. The first item of the size is then deleted so that the program can recognize this case
      if data['image_1_size'][0] == 0: del(data['image_1_size'][0])
      if data['image_2_size'][0] == 0: del(data['image_2_size'][0])
    except:
      pass

    return data




class StaticMessage(Toplevel):
    # Function that shows a fixed message on top of the main window
    def __init__(self, parent, message = 'Hello!'):
        
        Toplevel.__init__(self, parent)
        
        self.configure(bg='White')
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.transient(parent)
        self.update()
        self.geometry("%dx%d%+d%+d" % (400, 50, parent.winfo_x()+parent.winfo_width()/2-200, parent.winfo_y()+parent.winfo_height()/2-25))
        Label(self, text=message, font=('Times', 16), justify=CENTER, bg='White').grid( row=0, column=0, sticky=W+E )
        self.update()
       
       
       
       
class ShowInfo(Toplevel):
    # Function that shows a message with an "OK" button on top of the main window
    def __init__(self, parent, title = 'Info', message = 'Hello!'):

        Toplevel.__init__(self, parent)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        self.geometry("%dx%d%+d%+d" % (width, height, self.master.winfo_x()+self.master.winfo_width()/2-width/2, self.master.winfo_y()+self.master.winfo_height()/2-height/2))
        self.geometry('')
        
        self.title( title )
        Label(self, text=message, font=("Times 14 bold")).grid(row=0, column=0, sticky=W+E, padx=25, pady=10)
        Button(self, text="OK", command=self.ok).grid(row=1, column=0, padx=25, pady=10)
        self.update()

    def ok(self):
    # When the button OK is pressed the window is destroyed
        self.destroy()