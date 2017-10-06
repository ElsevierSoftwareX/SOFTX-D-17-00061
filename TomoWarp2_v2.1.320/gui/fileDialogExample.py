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

import Tkinter, Tkconstants, tkFileDialog

#class TkFileDialogExample(Tkinter.Frame):

  #def __init__(self, root):

    #Tkinter.Frame.__init__(self, root)

    ## options for buttons
    #button_opt = {'fill': Tkconstants.BOTH, 'padx': 5, 'pady': 5}

    ## define buttons
    ##Tkinter.Button(self, text='askopenfile', command=self.askopenfile).pack(**button_opt)
    ##Tkinter.Button(self, text='askopenfilename', command=self.askopenfilename).pack(**button_opt)
    ##Tkinter.Button(self, text='asksaveasfile', command=self.asksaveasfile).pack(**button_opt)
    #Tkinter.Button(self, text='asksaveasfilename', command=self.asksaveasfilename).pack(**button_opt)
    ##Tkinter.Button(self, text='askdirectory', command=self.askdirectory).pack(**button_opt)
    
    ## define options for opening or saving a file
    #self.file_opt = options = {}
    #options['defaultextension'] = '.txt'
    #options['filetypes'] = [('all files', '.*'), ('text files', '.txt')]
    #options['initialdir'] = './'
    #options['initialfile'] = 'myfile.txt'
    #options['parent'] = root
    #options['title'] = 'This is a title'

    ## This is only available on the Macintosh, and only when Navigation Services are installed.
    ##options['message'] = 'message'

    ## if you use the multiple file version of the module functions this option is set automatically.
    ##options['multiple'] = 1

    ## defining options for opening a directory
    #self.dir_opt = options = {}
    #options['initialdir'] = './'
    #options['mustexist'] = False
    #options['parent'] = root
    #options['title'] = 'This is a title'

  ##def askopenfile(self):
    ##"""Returns an opened file in read mode."""
    ##return tkFileDialog.askopenfile(mode='r', **self.file_opt)

  ##def askopenfilename(self):
    ##"""Returns an opened file in read mode.
    ##This time the dialog just returns a filename and the file is opened by your own code.
    ##"""
    ### get filename
    ##filename = tkFileDialog.askopenfilename(**self.file_opt)

    ### open file on your own
    ##if filename:
      ##return open(filename, 'r')

  ##def asksaveasfile(self):
    ##"""Returns an opened file in write mode."""
    ##return tkFileDialog.asksaveasfile(mode='w', **self.file_opt)

  #def asksaveasfilename(self):
    #"""Returns an opened file in write mode.
    #This time the dialog just returns a filename and the file is opened by your own code.
    #"""
    ## get filename
    #fileName = tkFileDialog.asksaveasfilename(**self.file_opt)
    ## open file on your own
    ##if filename:
      ##return open(filename, 'w')
    #print fileName
    
    #var   = Tkinter.StringVar()
    #label = Tkinter.Message( root, textvariable=var )
    #var.set( "Your filename is %s"%(fileName))
    #label.pack() 
  
  

  ##def askdirectory(self):
    ##"""Returns a selected directoryname."""
    ##return tkFileDialog.askdirectory(**self.dir_opt)




#if __name__=='__main__':
  #root = Tkinter.Tk()
  #TkFileDialogExample(root).pack()
  
  ##var = StringVar()
  ##label = Message( root, textvariable=var, relief=RAISED )
  ##var.set("Hey!? How are you doing?")
  ##label.pack()

  #root.mainloop()



# 2015-02-18 EA and ET: Testing out idea of GUI

# Starting with examples from:
#   - http://tkinter.unpythonic.net/wiki/tkFileDialog
#   - http://code.activestate.com/recipes/438123-file-tkinter-dialogs/

import Tkinter, tkFileDialog
import os.path

root = Tkinter.Tk()

currentRow = 0

# ======== Select a directory:
# load the default from somewhere...
DIR_image_1 = "."

def chooseDIR_image_1(  ):
    DIR_image_1 = tkFileDialog.askdirectory(parent=root,initialdir=os.path.expanduser("~"),title='Please select a directory for Image 1')
    if len( DIR_image_1 ) > 0:
        print "You chose %s" % DIR_image_1
        entryDIR_image_1.delete( 0, Tkinter.END )
        entryDIR_image_1.insert( 0, DIR_image_1 )
    return DIR_image_1

labelDIR_image_1 = Tkinter.Label( root, text="Image 1 Directory" )
labelDIR_image_1.grid( row=currentRow, column=0 )

entryDIR_image_1 = Tkinter.Entry( root )
entryDIR_image_1.grid( row=currentRow, column=1 )
entryDIR_image_1.delete( 0, Tkinter.END )
entryDIR_image_1.insert( 0, DIR_image_1 )

buttonDIR_image_1 = Tkinter.Button( root, text="Choose directory for Image 1", command=chooseDIR_image_1 )
buttonDIR_image_1.grid( row=currentRow, column=2 )


## ======== Select a directory:
currentRow += 1
# load the default from somewhere...
DIR_image_2 = "."

def chooseDIR_image_2(  ):
    DIR_image_2 = tkFileDialog.askdirectory(parent=root,initialdir=os.path.expanduser("~"),title='Please select a directory for Image 2')
    if len( DIR_image_2 ) > 0:
        print "You chose %s" % DIR_image_2
        entryDIR_image_2.delete( 0, Tkinter.END )
        entryDIR_image_2.insert( 0, DIR_image_2 )
    return DIR_image_2

labelDIR_image_2 = Tkinter.Label( root, text="Image 2 Directory" )
labelDIR_image_2.grid( row=currentRow, column=0 )

entryDIR_image_2 = Tkinter.Entry( root )
entryDIR_image_2.grid( row=currentRow, column=1 )
entryDIR_image_2.delete( 0, Tkinter.END )
entryDIR_image_2.insert( 0, DIR_image_2 )

buttonDIR_image_2 = Tkinter.Button( root, text="Choose directory for Image 2", command=chooseDIR_image_2 )
buttonDIR_image_2.grid( row=currentRow, column=2 )


# ======== Binary checkbox:
currentRow += 1


CheckVar1 = Tkinter.IntVar( False )
C1 = Tkinter.Checkbutton( root, text = "Output CC field in %", variable = CheckVar1, \
                 onvalue = 1, offvalue = 0, height=5, \
                 width = 20)
C1.grid( row=currentRow, column=0 )



# ======== Menu for Image Mode:
currentRow += 1

class MyOptionMenu(  Tkinter.OptionMenu ):
    def __init__(self, master, status, *options):
        self.var = Tkinter.StringVar(master)
        self.var.set(status)
        Tkinter.OptionMenu.__init__(self, master, self.var, *options)
        #self.config(font=('calibri',(10)),bg='white',width=12)
        #self['menu'].config(font=('calibri',(10)),bg='white')


labelImage_format = Tkinter.Label( root, text="Image Format" )
labelImage_format.grid( row=currentRow, column=0 )

optionMenuImage_format = MyOptionMenu( root, 'Image Type', 'auto', 'Tiff', 'Raw', 'EDF' )
optionMenuImage_format.grid( row=currentRow, column=1 )

print (optionMenuImage_format.var).get()


# ======== Button to print chosen variables:
currentRow += 1

class MyOptionMenu(  Tkinter.OptionMenu ):
    def __init__(self, master, status, *options):
        self.var = Tkinter.StringVar(master)
        self.var.set(status)
        Tkinter.OptionMenu.__init__(self, master, self.var, *options)
        #self.config(font=('calibri',(10)),bg='white',width=12)
        #self['menu'].config(font=('calibri',(10)),bg='white')

buttonDIR_image_2 = Tkinter.Button( root, text="Print chosen variables", command=print_varibales )
buttonDIR_image_2.grid( row=currentRow, column=2 )



root.mainloop()




## ======== Select a file for opening:
#file = tkFileDialog.askopenfile(parent=root,mode='rb',title='Choose a file')
#if file != None:
    #data = file.read()
    #file.close()
    #print "I got %d bytes from this file." % len(data)


## ======== "Save as" dialog:
#myFormats = [
    #('Windows Bitmap','*.bmp'),
    #('Portable Network Graphics','*.png'),
    #('JPEG / JFIF','*.jpg'),
    #('CompuServer GIF','*.gif'),
    #]
#fileName = tkFileDialog.asksaveasfilename(parent=root,filetypes=myFormats ,title="Save the image as...")
#if len(fileName ) > 0:
    #print "Now saving under %s" % nomFichier


