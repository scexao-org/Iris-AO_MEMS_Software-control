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


from . import core
np = core.np


__all__ = ['Fiber']

class Fiber(object):
    def __init__(self, nfib=8, imgpx=512, i_blobs=None, locx=None, locy=256,
                 nhot=100, blob_centers=(0, 1), blob_minmax=(-2, 2),
                 opt_sig=1.25):
        """
        Simulates the injection of light in the fibers

        Args :
        * nfib (int): number of fibers
        * imgpx (int): number of pixels in the width of square image
        * i_blobs (list of float): integrated intensity of each blob,
          e.g. [5000, 4000, ...]. Size equal to nfib
        * locx (list of int): x-locations of the blobs in pixels,
          e.g. [14, 40, 78, 120, ...]. Size equal to nfib
        * locy (int): y-location of the blobs in pixels, e.g. 256.
        * nhot (int): number of hot pixels on an image
        * blob_centers (tuple of 2 floats): Normal distribution parameters
          (mean, sig) of the optimal tip-tilt values that yield the best
          injection in the fibers. Used to randomly set these values
        * blob_minmax (tuple of 2 floats): (min, max) bounds of where the
          optimal tip-tilt values should lie
        * opt_sig (float): size of the injection gaussian pattern
          obtained with optimization
        """
        self.nfib = int(nfib)
        self.imgpx = int(imgpx)
        self.locy = int(locy) if 0 <= locy < self.imgpx else imgpx//2
        self.locx = list(map(int, locx[: self.nfib]))\
                    if locx is not None\
                    else np.round((np.arange(1, 9)**1.84+1.2)*10).astype(int).tolist()
        self.nhot = int(nhot)
        self.blob_minmax = [int(blob_minmax[0]), int(blob_minmax[1])]
        self.hotpxXY = np.random.randint(low=0, high=self.imgpx,
                                         size=(self.nhot, 2), dtype=int)
        self.best_tiptilt = np.clip(np.random.normal(loc=blob_centers[0],
                                                     scale=blob_centers[1],
                                                     size=(self.nfib, 2)),
                                    self.blob_minmax[0],
                                    self.blob_minmax[1])
        self.i_blobs = list(map(int, i_blobs[: self.nfib]))\
                       if i_blobs is not None\
                       else np.random.randint(low=7000,
                                              high=10000,
                                              size=self.nfib,
                                              dtype=int).tolist()
        self.opt_sig = float(opt_sig)

    def make_img(self, i_blobs=None, pxsz_blob=5):
        # coordinate vector for the 2D-gauss
        pxsz_blob = float(pxsz_blob)
        lin = np.round(np.arange(-2*float(pxsz_blob),
                                 2*float(pxsz_blob))).astype(int)
        # 2D-gauss
        g = core.gauss2D(x=lin, y=lin, a=1., x0=0., y0=0.,
                         sigma=pxsz_blob*0.5, foot=0)
        g /= g.sum()
        sz = lin.size
        # big empty image
        img = np.zeros((self.imgpx, self.imgpx))
        # add the blobs one by one with right intensity
        if i_blobs is None:
            i_blobs = self.i_blobs
        for locx_blob, intensity_blob in zip(self.locx, i_blobs):
            img[self.locy-sz//2:self.locy-sz//2+sz,
                locx_blob+lin.min():locx_blob+lin.min()+sz] = g*intensity_blob
        return img

    def add_noise(self, img, i_hot=1000., bg=(10, 2)):
        """
        ihot = intensity of hot pixels
        bg = (mean, sig) of background dark noise
        """
    	img += np.abs(np.random.normal(float(bg[0]), float(bg[1]),
                      (self.imgpx, self.imgpx)))
    	img[self.hotpxXY[:,0], self.hotpxXY[:,1]] = i_hot
    	return img

    def get_intensity(self, fib, tip, tilt):
        iB = self.i_blobs[int(fib)]
        tipB, tiltB = self.best_tiptilt[int(fib)]
        return core.gaussPt(float(tip), float(tilt), a=iB, x0=tipB, y0=tiltB,
                            sigma=self.opt_sig)

    def cam_img(self, tip, tilt, pxsz_blob=5):
        """
        tip and tilt should be lists of floats, of size nfib
        """
        i_blobs = [self.get_intensity(i, tip[i], tilt[i])\
                   for i in range(self.nfib)]
        return self.make_img(i_blobs=i_blobs, pxsz_blob=float(pxsz_blob))

    def cam_img_noise(self, tip, tilt, i_hot=1000., bg=(10, 2), pxsz_blob=5):
        """
        tip and tilt should be lists of floats, of size nfib
        """
        img = self.cam_img(tip, tilt, pxsz_blob=pxsz_blob)
        return self.add_noise(img, i_hot=i_hot, bg=bg)
