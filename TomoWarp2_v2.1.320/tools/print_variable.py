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

""" 
Functions that print a variable in the form "variableName: variableValue"

Input:

  1. variable to be printed - IT HAS TO BE A LIST EVEN IF ONLY ONE VARIABLE IS PASSED
  2. tabulator to be printed between the variables
  3. If the name of the function is printed or not
  4. variable name if not found automatically
"""

import sys
import inspect
import numpy

            
def pv(variables, tabulator = '\t', print_function = True, varName = None, _print = True):

        if not type(variables) is list:
            sys.exit('print_variable: Input has to be a list')

        # List of the local variables in the calling function
        callers_local_vars = inspect.currentframe().f_back.f_locals.items()

        string = ""
        if print_function:
            # Getting the name of the calling function
            curframe = inspect.currentframe()
            calframe = inspect.getouterframes(curframe, 2)
            string += '\nin %s():\n'%(str(calframe[1][3]))

        # For every variable in the list look for its name and print it
        for var in variables:
            # Initialising FoundVarName
            FoundVarName = None
            #Check in every local variable
            for var_name, var_val in callers_local_vars:
                # If the desired variable is inside the data dictionary another loop is needed
                if var_name == "data":
                  try:
                    for item in var_val:
                        if var_val[item] is var:
                            # Check if more than one variable has the same value
                            if FoundVarName == None:
                                FoundVarName = item
                            # In this case the variable name is se to VariableValueNotUnique
                            elif varName == None:
                                FoundVarName = "VariableValueNotUnique"
                            # Unless a variable name is given in input...
                            else:
                                FoundVarName = varName
                  except:
                    pass
                elif var_val is var: 
                    if FoundVarName == None:
                        FoundVarName = var_name
                    elif varName == None:
                        FoundVarName = "VariableValueNotUnique"
                    else:
                        FoundVarName = varName

            if FoundVarName == None: FoundVarName = "VariableValueNotUnique"

            # If the variable is a string '' are added 
            if type(var) is str:
                string +=  FoundVarName+" = '"+var+"'"
            else:
                # In order to copy and paste the printed value arrays are changed to list
                #   so that a comma is printed between values
                string += FoundVarName+" = "+str( numpy.array(var).tolist() )

            if numpy.array(var == variables[-1]).flatten().all():
                pass
            else:
                string += tabulator

        if _print: print string,

        return string