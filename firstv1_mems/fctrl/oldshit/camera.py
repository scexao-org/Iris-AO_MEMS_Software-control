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


import andorsdk
import astropy.io.fits as pf

from . import core
np = core.np
from .fiber import Fiber


__all__ = ['Camera']

class Camera(andorsdk.Andor):
    def __init__(self, mode):
        """
        Initializes the camera

        Args:
          * mode (str): can be 'single' or 'video'
        """
        super(Camera, self).__init__()
        if str(mode).lower() == 'video':
            self.Acquire.Video()
            self._video = True
        else:
            self.Acquire.Single()
            self._video = False

    def save():
        
    def get_image(self, full_light=False, noise=False):
        # replace that stuff with real image acquisition et remove
        # full_light + noise parameters
        if full_light:
            img = self._fiber.make_img(i_blobs=self._fiber.i_blobs)
        else:
            if not self._mems:
                tip, tilt = np.random.normal(0, 1, size=(2,8))
            else:
                tip, tilt, piston = self._mems.get_pos(elm='first')
            img = self._fiber.cam_img(tip=tip, tilt=tilt)
        if noise:
            img = self._fiber.add_noise(img)
        return img

    def get_dark(self):
        # replace that stuff with real image acquisition and
        # remove full_light + noise parameters
        empty = np.zeros((self._fiber.imgpx, self._fiber.imgpx))
        return self._fiber.add_noise(empty)
