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


try:
    import andorsdk
    WITHCAM = True
except ImportError:
    WITHCAM = False

from . import core
from .clickimg import ClickImg
input = core.input
os = core.os
np = core.np
Rectangle = core.Rectangle
gaussian_filter = core.gaussian_filter
plt = core.plt


__all__ = ['BoxCal']


class BoxCal(object):
    def __init__(self, nfib, box_pxsize=core.FIBERSBOXSIZE, with_cam=True):
        """
        Creates a fibers blobs clicking-tool

        Args:
          * nfib (int): the number of fibers
          * box_pxsize (int or [int, int]): the Y-X size of the boxes in px
        """
        self._with_cam = bool(with_cam)
        if self._with_cam and WITHCAM:
            print("Initializing Andor Camera .... ") 
            self.cam = andorsdk.Andor()

            print("Cooling down the detector...")
            self.cam.Temperature.setpoint = core.CAMERATEMP  # start cooling
            self.cam.Temperature.cooler = core.CAMERACOOLING

            #self.cam.exposure = core.DEFAULTEXPOSURETIME  # ms
            self.cam.exposure = 2000  # ms
            
            self.cam.Acquire.Single()

            sz = self.cam.Detector.size
            self._szratio = sz[0]*1./sz[1]

        self._nfib = int(nfib)
        self._boxes = []
        self._centers = np.zeros((self._nfib, 2))
        self.box_pxsize = box_pxsize

    def __del__(self):
        self.exit()

    __exit__ = __del__

    @property
    def box_pxsize(self):
        """
        The size [Y, X] of the boxes in px
        """
        return self._box_pxsize

    @box_pxsize.setter
    def box_pxsize(self, value):
        if not hasattr(value, '__iter__'):
            self._box_pxsize = [int(value), int(value)]
        elif len(value) >= 2:
            self._box_pxsize = [int(value[0]), int(value[1])]
        else:
            print("Can't understand that input. Should be an integer"\
                  " or a list of 2 integers")
            return
        # update the centers with new box size
        self.boxes_update()

    @property
    def centers(self):
        """
        The centers of the boxes
        """
        return self._centers

    @centers.setter
    def centers(self, value):
        if np.shape(value) != (self._nfib, 2):
            print("wrong shape, should be {:d}x2".format(self._nfib))
            return
        self._centers = np.round(value).astype(int)
        self.boxes_update()

    def boxes_update(self):
        """
        Updates the boxes bounds given the centers
        """
        self._boxes = []
        # store Y-X
        for v0, v1 in self._centers:
            ymin = int(max(0, v0-self.box_pxsize[0]//2))
            xmin = int(max(0, v1-self.box_pxsize[1]//2))
            self._boxes.append([slice(ymin, ymin + self.box_pxsize[0]),
                                slice(xmin, xmin + self.box_pxsize[1])])

    @property
    def boxes(self):
        """
        The boxes bounds as shape (nfib, 2)
        """
        return self._boxes

    @boxes.setter
    def boxes(self, value):
        print("Read-only. Set 'centers' instead")

    def show_imgcuts(self, img=None, sigma_blur=3):
        """
        Shows the X and Y-cuts of a fiber-injected image

        Args:
          * img (2d array or None): the image to cut, None to acquire
            a new one
          * sigma_blur (float>0): the semi-major axis of the
            gaussian-blurring
        """
        if not self._with_cam:
            print("No camera initialized")
            return
        if img is None:
            input("No image was provided. An image is going to be acquired. "\
                  "Make sure all fibers are illuminated and press Enter.")
            #img = self.cam.Acquire.snap()
            img = self.cam.Acquire.snap().reshape((496,658)).T
        self._img = img
        img = gaussian_filter(self._img, abs(float(sigma_blur)))
        plt.figure()
        plt.plot(img.max(axis=0), label='X-cut (px)')
        plt.legend()
        plt.figure()
        plt.plot(img.max(axis=1), label='Y-cut (px)')
        plt.legend()

    def clic_boxcal(self, img=None, cmap_minmax=None, cmap='gist_earth'):
        """
        Shows the X and Y-cuts of a fiber-injected image

        Args:
          * img (2d array or None): the image to cut, None to acquire
            a new one
          * cmap_minmax ([float, float] or None): min-max for the color-
            scale, or None for auto-determination
          * cmap (color map object or str): the color map used for
            displaying the image
        """
        if not self._with_cam:
            print("No camera initialized")
            return
        if img is None:
            input("No image was provided. An image is going to be acquired."
                  "Make sure all fibers are illuminated and press Enter.")
            #img = self.cam.Acquire.snap()
            img = self.cam.Acquire.snap().reshape((496,658)).T
        self._img = img
        if cmap_minmax is None:
            cmap_minmax = [img.min(), img.max()]
        else:
            cmap_minmax = list(map(float, cmap_minmax[:2]))
        ClickImg(daddy=self, img=img, cmap_minmax=cmap_minmax, cmap=cmap)
    
    def show_boxes(self, img=None, cmap_minmax=None, cmap='gist_earth'):
        """
        Shows the boxes

        Args:
          * img (2d array or None): the image to cut, None to reuse the
            current one
          * cmap_minmax ([float, float] or None): min-max for the color-
            scale, or None for auto-determination
          * cmap (color map object or str): the color map used for
            displaying the image
        """
        if not self._with_cam and img is None:
            print("No camera initialized")
            return
        if img is None:
            if not hasattr(self, '_img'):
                print("You need to provide an image 'img'")
                return
            img = self._img
        if cmap_minmax is None:
            cmap_minmax = [img.min(), img.max()]
        else:
            cmap_minmax = list(map(float, cmap_minmax[:2]))
        f = plt.figure(figsize=(5,5*self._szratio))
        ax = f.add_axes((0,0,1,1))
        ax.imshow(img, cmap=cmap, vmin=cmap_minmax[0], vmax=cmap_minmax[1],
                  origin='lower', aspect='equal')
        for sy, sx in self._boxes:
            ax.add_patch(Rectangle((sx.start, sy.start), self.box_pxsize[1],
                         self.box_pxsize[0], fill=False, color='r'))

    def boxes_save(self, name, override=False):
        """
        Saves the boxes and boxes size to a file

        Args:
          * name (str): the name of the file
          * override (bool): whether to override a file if already
            existing
        """
        name = core.make_filepath(name, core.BOXESFILENAME)
        if not os.path.isfile(name) or bool(override):
            np.savetxt(name,
                       np.r_[np.array([self._box_pxsize]), self._centers],
                       header="1st row is box_size, then (nfib, 2) shape")
            print("Saved in '{}'".format(name))
        else:
            print("File '{}' already exists".format(name))

    def boxes_list(self, ret=False):
        """
        Shows all available boxes files saved

        Args:
          * ret (bool): whether to print (if False) or return
            the list
        """
        if not ret:
            print("\n".join(core.list_filepath(core.BOXESFILENAME)))
        else:
            return core.list_filepath(core.BOXESFILENAME)

    def boxes_delete(self, name):
        """
        Deletes a boxes file saved

        Args:
          * name (str): the name of the file to delete
        """
        name = core.make_filepath_nostamp(name, core.BOXESFILENAME)
        if os.path.isfile(name):
            os.remove(name)
            print("Removed: '{}'".format(name))
        else:
            print("File '{}' not found".format(name))

    def boxes_load(self, name):
        """
        Loads a boxes file previously saved

        Args:
          * name (str): the name of the file to load
        """
        name = core.make_filepath_nostamp(name, core.BOXESFILENAME)
        if os.path.isfile(name):
            l = np.loadtxt(name)
            self._box_pxsize = list(map(int, l[0]))
            self.centers = l[1:]
            print("Loaded '{}'".format(name))
        else:
            print("File '{}' not found".format(name))

    def exit(self):
        """
        Switches off the camera
        """
        print("Switching off the camera")
        if self._with_cam:
            self.cam.shutdown()
