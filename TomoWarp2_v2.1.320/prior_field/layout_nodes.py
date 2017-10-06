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

""""
This function is responsible for laying out REGULARLY SPACED calculation nodes
  within an image.

INPUTS:
- Three-component list of node spacing
- List of corners of the ROI

OUTPUTS:
- Prior including: (Node Number), (Absolute position of nodes), (Prior Guess (zero for the moment))
- Spacing position of nodes in each direction (one vector per direction)
"""
import numpy

def layout_nodes( node_spacing, corners ):

        # Calculate positions of nodes in H
        nodes_h = range(corners[0][0]+int(corners[1][0]%node_spacing[0])/2,corners[1][0]+1,node_spacing[0])
        # Calculate positions of nodes in W
        nodes_w = range(corners[0][1]+int(corners[1][1]%node_spacing[1])/2,corners[1][1]+1,node_spacing[1])
        # Calculate positions of nodes in D
        nodes_d = range(corners[0][2]+int(corners[1][2]%node_spacing[2])/2,corners[1][2]+1,node_spacing[2])

        # With our x,y,z displacement iterate and build the matrix.
        prior = numpy.zeros((len(nodes_h) * len(nodes_w) * len(nodes_d), 12 ), dtype='<f8')
        # Add node number in first column of prior
        for i in range( prior.shape[0] ): prior[i,0]=i

        count = 0
        for h in range(len(nodes_h)):
          for w in range(len(nodes_w)):
            for d in range(len(nodes_d)):
              prior[count,1:4] = ( nodes_h[h], nodes_w[w], nodes_d[d] )
              count += 1

        return prior, nodes_h, nodes_w, nodes_d