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

# mems stuff

# cal files
# files to store in "$HOME/.firstctrl/calmems"
#MIRRORNUM = 'FSC37-01-11-0308'  # for Paris lab
#DRIVERNUM = '04160165'  # for Paris lab

MIRRORNUM = 'FSC37-02-01-0907'  # for SUBARU
DRIVERNUM = '11140044'  # for SUBARU

NSEGMENTS = 37
#FIRSTSEGS = [15,16,17,19,20,24,29,33,37]
FIRSTSEGS = [15,19,16,29,17,20,33,24,37]
#FIRSTSEGS = [15,29,16,33,17,24,20,33,37]

TIPTILTMIN = -2  # in units given to the mems
TIPTILTMAX = 2  # in units given to the mems
PISTONMIN = -1  # in units given to the mems
PISTONMAX = 1  # in units given to the mems


# the box-size when clicking the fibers-boxes
FIBERSBOXSIZE = [15, 15]  # pixels
# do you want to see the full andor image in Andor control process
SHOWANDORBIGIMAGE = True
# how much bigger you want to see the fibers-subimages
ZOONFACTORSUBIMG = 3
# how much spacing between subimgs
MARGIN = 5  # px

# lags to give time to camera and mems during the loop
IMGLAG = 0.05  # lag to get the image from andor
MEMSLAG = 0.05  # lag to move mems

# camera stuff
CAMERACOOLING = True
CAMERATEMP = -5  # celcius
DEFAULTEXPOSURETIME = 100  # ms


####################################################
# Are you sure you should change this below?

DISPLAYLOG = "Log-view: {log}\nClims: [{min:5.1f}, {max:5.1f}]\n"\
             "Auto-Cmap: {auto}\nDark: {dark}\n"
for seg in FIRSTSEGS:
    DISPLAYLOG += "#%2d cts: {sum%s:8.1f}, max: {max%s:5.1f}\n" % (seg, seg, seg)
DISPLAYLOG += "\n\n\n"


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

