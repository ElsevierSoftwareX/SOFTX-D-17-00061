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
Load only images that are not yet in memory and concatenate them

INPUTS:
- array of desired extent for the image
- array of externt for the image currently in memory
- image current in memory
- imageNumber (indicating reference 0 or deformed 1 image)
- data structure

OUTPUTS:
- new extent
- new image
"""

import numpy
from read_images import read_images


def load_slices( zExtents, zExtents_prev, image, imageNumber, data):

        z_top = zExtents[0]
        z_bot = zExtents[1]
        z_top_prev = zExtents_prev[0]
        z_bot_prev = zExtents_prev[1]

        if (z_top >= z_top_prev):

          if (z_top <= z_bot_prev):
          # this is the most common case: the two interval have an intersection

            # eliminate the slices we don't need anymore
            image = image[ (z_top - z_top_prev)::]

          else:
          # in this case the two interval have not intersection (for instance for large node spacing)

            # set the images to an empty array
            image = []

        else:
        # this is the case where the new intervall starts before the old one

          if z_bot < z_top_prev:
          # in this case the two interval have not intersection (but the new one starts before the old one: I wonder if it will ever happen)

            # set the images to an empty array
            image = []

          elif z_bot < z_bot_prev:

            # if the new z_bot is lower than before it keeps the extra slices and update the z_bot value
            z_bot = z_bot_prev

          # load slices for this interval to fill the gap before the previous interval
          try:
            image_add = read_images( data.image_data_format, data.image_format, data.image_size[imageNumber-1], data.DIR_image[imageNumber-1], \
              data.image_prefix[imageNumber-1], data.image_digits[imageNumber-1], data.image_ext, data.ROI_corners[imageNumber-1], [ z_top, min(z_bot, z_top_prev-1)]  )
          except Exception as exc:
            raise Exception(exc)

          # images have to be converted to float 32b
          # to be investigated!
          image_add = image_add.astype( '<f4' )

          if len(image) > 0:
            image = numpy.concatenate((image_add, image))
          else:
            image = image_add.copy()


        if z_bot > z_bot_prev:

            # load slices for this interval to fill the gap after the previous interval
            image_add = read_images( data.image_data_format, data.image_format, data.image_size[imageNumber-1], data.DIR_image[imageNumber-1], \
              data.image_prefix[imageNumber-1], data.image_digits[imageNumber-1], data.image_ext, data.ROI_corners[imageNumber-1], [ max(z_top,z_bot_prev+1), z_bot]  )

            # images have to be converted to float 32b
            # to be investigated!
            image_add = image_add.astype( '<f4' )

            if len(image) > 0:
              image = numpy.concatenate((image, image_add))
            else:
              image = image_add.copy()

        return ( [ z_top, z_bot ], image )