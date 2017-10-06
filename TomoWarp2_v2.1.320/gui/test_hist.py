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

import random
import matplotlib, sys
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import numpy as np
from Tkinter import *
import ttk


#root
root = Tk()
root.title("Sample Size and the Normal Distribution")

#mainframe
mainframe = ttk.Frame(root, padding = "3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

def create_list(sampleSize, upperLimit):
    numbList = []
    sampleSize = int(sample.get())
    upperLimit = int(upper.get())
    while sampleSize > 0:
        sampleSize -= 1
        randomNum = random.randrange(0,upperLimit+1)
        numbList.append(randomNum)
    numbList.sort(key=int)
    return numbList

def medians_variance(median_list):
    sum_of_medians = sum(median_list)
    variance = sum_of_medians / len(median_list)
    return variance


def median(numbList):

        srtd = sorted(numbList)
        mid = len(numbList)//2
        if len(numbList) % 2 == 0:
            return (srtd[mid-1] + srtd[mid]) / 2.0
        else:
            return srtd[mid]


def main():

    number_lists = 10
    lists = []
    median_list = []

    binsize = 10

    for i in range(number_lists):
        lists.append(create_list(sampleSize, upperLimit))

    for current_list in lists:
        current_median = median(current_list)
        median_list.append(current_median)
        median_list.sort(key=float)


    plt.hist(median_list, binsize)

    plt.xlabel('Median Value', fontsize = 15)
    plt.ylabel('Frequency', fontsize = 15)

    plt.show()


    med = median(median_list)
    std = np.std(median_list)
    var = (std**2)


#sampleSize Entry
sample = StringVar()
sampleSize = ttk.Entry(mainframe, width = 7, textvariable = sample)
sampleSize.grid(column = 2, row = 1, sticky =(W, E))

#upperLimit Entry
upper = StringVar()
upperLimit = ttk.Entry(mainframe, width = 7, textvariable = upper)
upperLimit.grid(column = 2, row = 3, sticky = (W, E))

#binsize Entry
Bin = StringVar()
binsize = ttk.Entry(mainframe, width = 7, textvariable = Bin)
binsize.grid(column = 2, row = 5, sticky = (W, E))

#sampleSize and upperLimit Labels
ttk.Label(mainframe, text="Sample Size ").grid(column = 1, row = 1, sticky = W)
ttk.Label(mainframe, text="Upper Limit ").grid(column = 1, row = 3, sticky = W)
ttk.Label(mainframe, text="Bin Size").grid(column = 1, row = 5, sticky = W)

#histogram embed
f = Figure(figsize = (5,4), dpi=100)

#button for new histogram
button = ttk.Button(mainframe, text="New Histogram", command=main).grid(column=1, row=7, sticky=W)

#scale
scale = Scale(mainframe, from_=0, to=10, orient=HORIZONTAL,length=400).grid(column = 5, row = 12, sticky= S)

for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)

sampleSize.focus()
upperLimit.focus()
root.bind('<Return>', main)

root.mainloop()