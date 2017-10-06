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

import sys
import getopt
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='gTomoWarp2 - A GUI for TomoWarp2')
    parser.add_argument('inputfile', nargs='?')
    parser.add_argument('--notab', action='store_true')
    args = parser.parse_args()
    if args.notab:
        from gui.gTomoWarp2 import buildGUI
    else:
        from gui.gTomoWarp2_ttk import buildGUI

#    argv = sys.argv[1:]

#    try:
#        opts, args = getopt.gnu_getopt(argv,"")
#    except getopt.GetoptError as e:
#        print (str(e))
#
#    if len(args) != 0:
#        inputfile = args[0]
#    else:
#        inputfile = None

    buildGUI( args.inputfile )
