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
Calculate node spacing of a series of regularly spaced nodes

INPUT:
- matrix of node position

OUTPUT: 
- #n lists of node spacing.
"""

# Date created: 2013-08-20


def calculate_node_spacing( node_positions ):
        number_of_nodes = node_positions.shape[0]

        nodes = [[]]*node_positions.shape[1]

        for i_d in range(node_positions.shape[1]):

            # Initialising nodes lists
            nodes[i_d] = []
            nodes[i_d].append(node_positions[ 0, i_d ])

            # Collect nodes position in each direction
            for i in xrange( number_of_nodes ):
                pos_cur = node_positions[i, i_d]
                if pos_cur > nodes[i_d][ -1 ]: nodes[i_d].append(pos_cur)
                if pos_cur < nodes[i_d][ -1 ]: continue

        return nodes
