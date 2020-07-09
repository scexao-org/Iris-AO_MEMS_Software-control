#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
#  
#  FIRSTCTRL - Pupil remapping control software
#  Copyright (C) 2016  Guillaume Schworer
#  
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#  
#  For any information, bug report, idea, donation, hug, beer, please contact
#    guillaume.schworer@gmail.com
#
###############################################################################

# cal files
MIRRORNUM = 'FSC37-01-11-0308'
DRIVERNUM = '04160165'
NSEGMENTS = 37
FIRSTSEGS = [37, 9, 24, 35, 7, 4, 33, 15, 28]#[5, 11, 17, 20, 22, 27, 29, 31, 36]

IMGLAG = 0.05  # lag to get image from andor
MEMSLAG = 0.05  # lag to move mems

TIPTILTMIN = -5  # in units given to the mems
TIPTILTMAX = 5  # in units given to the mems
PISTONMIN = -3  # in units given to the mems
PISTONMAX = 3  # in units given to the mems

# where the calibration files are to be found
# relative to HOME
PATHCALMEMS = ['.firstctrl', 'calmems']

# where to save the saved calibrations and boxes files
# relative to HOME
PATHCONFIGFILE = ['.firstctrl']

# the format of the name for the files that contain the saved calibrations
SHAPEFILENAME = '{name}_%Y%m%dT%H%M%S-%f.shape'
SHAPEONFILENAME = '{name}_%Y%m%dT%H%M%S-%f.shapeon'
SHAPEOFFFILENAME = '{name}_%Y%m%dT%H%M%S-%f.shapeoff'
# the format of the name for the files that contain the coordinates of the boxes
BOXESFILENAME = "{name}_%Y%m%dT%H%M%S-%f.boxes"


# where to save the saved calibrations and boxes files
# relative to HOME
PATHIMG = ['andorsnaps']
# the format of the name for the files that contain the coordinates of the boxes
IMGFILENAME = "{name}_%Y%m%dT%H%M%S-%f.fits"
