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


import astropy.io.fits as pf
import andorsdk
import matplotlib.pyplot as plt
plt.ion()
from . import core
np = core.np
time = core.time
os = core.os
Patiencebar = core.Patiencebar
from .mems import Mems
from .camera import Camera
from .boxcal import BoxCal


__all__ = ['Loop']


class Loop(object):
    _boxcal = BoxCal(nfib=len(core.FIRSTSEGS), with_cam=False)

    def __init__(self):
        print("Initializing Andor Camera .... ") 
        self.cam = andorsdk.Andor()

        print("Cooling down the detector...")
        self.cam.Temperature.setpoint = core.CAMERATEMP  # start cooling
        self.cam.Temperature.cooler = core.CAMERACOOLING
        self.camsize = self.cam.Detector.size
        #self.cam.exposure = core.DEFAULTEXPOSURETIME  # ms
	self.cam.exposure = 20  # ms
        self.cam.Acquire.Single()
        self.camsize = self.cam.Detector.size
        self._dark = np.zeros(self.camsize).astype(np.int16)

        self.mems = Mems()
        # get connection
        self.mems.connect()
        # reset flat
        self.mems.flat()
        print("Connected and flattened mems")

        # needed for boxcal show_boxes
        self._boxcal._szratio = self.camsize[0]*1./self.camsize[1]

        # init the sub img
        self._nsub = [int(np.ceil(np.sqrt(len(core.FIRSTSEGS)))), 0]
        self._nsub[1] = int(np.ceil(len(core.FIRSTSEGS)/self._nsub[0]))

        self._do_boxes()
        
        l = self.boxes_list(ret=True)
        if len(l) > 0:
            self.boxes_load(l[-1])
        else:
            print("You shall first determine a fiver-boxing. Use Boxes program")

    def _do_boxes(self):
        box_pxsize = self._boxcal.box_pxsize
        self._subsize = [self._nsub[0] * (box_pxsize[0] + core.MARGIN)\
                                                             + core.MARGIN,
                         self._nsub[1] * (box_pxsize[1] + core.MARGIN)\
                                                             + core.MARGIN]
        self.lastsubimg = np.zeros(self._subsize).astype(np.int16) * np.nan
        self._subimgboxes = []
        for idx, seg in enumerate(core.FIRSTSEGS):
            ystart = (idx % self._nsub[0]) * (box_pxsize[0] + core.MARGIN)\
                                                                + core.MARGIN
            xstart = (idx // self._nsub[1]) * (box_pxsize[1] + core.MARGIN)\
                                                                + core.MARGIN
            ystop = ystart + box_pxsize[0]
            xstop = xstart + box_pxsize[1]
            self._subimgboxes.append([slice(ystart, ystop),
                                      slice(xstart, xstop)])

    def exit(self):
        """
        Exits everything
        """
        self.mems.exit()
        self.cam.shutdown()

    def boxes_load(self, name):
        """
        Loads a boxes file previously saved

        Args:
          * name (str): the name of the file to load
        """
        self._boxcal.boxes_load(name)
        self._do_boxes()

    boxes_list = _boxcal.boxes_list

    def show_boxes(self, cmap_minmax=None, cmap='gist_earth'):
        """
        Shows the boxes

        Args:
          * cmap_minmax ([float, float] or None): min-max for the color-
            scale, or None for auto-determination
          * cmap (color map object or str): the color map used for
            displaying the image
        """
        self._boxcal.show_boxes(img=self.lastimg, cmap_minmax=cmap_minmax,
                                    cmap=cmap)

    def dark_list(self):
        """
        List dark frames available
        """
        l = core.list_filepath(core.IMGFILENAME, basepath=core.PATHIMG)
        for item in l:
            name = core.make_filepath_nostamp(l, core.IMGFILENAME,
                                              basepath=core.PATHIMG)
            for hdu in pf.open(name):
                if hdu.header['TYPE'].lower() == 'dark':
                    print(l)

    def dark_load(self, name):
        name = core.make_filepath_nostamp(l, core.IMGFILENAME,
                                          basepath=core.PATHIMG)
        if os.path.isfile(name):
            for hdu in pf.open(name):
                if hdu.header['TYPE'].lower() == 'dark':
                    self._dark = hdu.data.copy()
                    print("Loaded '{}'".format(name))
                    break
        else:
            print("File '{}' not found".format(name))

    def acq_dark(self):
        """
        Acquires a dark frame that will be subtracted to the
        current video stream
        """
        #self._dark = self.cam.Acquire.snap().astype(np.int16)
        self._dark = self.cam.Acquire.snap().astype(np.int16).reshape((496,658)).T

    def rm_dark(self):
        """
        Deletes the current dark frame
        """
        self._dark = np.zeros(self.camsize).astype(np.int16)

    @property
    def dark(self):
        return self._dark
    @dark.setter
    def dark(self, value):
        print('Use acq_dark, rm_dark or load_dark instead')

    def optimization(self, elm='first', minmaxtip=(-2, 2), minmaxtilt=(-2, 2),
                           tiptiltsteps=(0.25, 0.25)):
        """
        Carries the injection optimization

        Input argument elm can be:
          * int -> 1 segment
          * list of int -> n segment
          * 'first' -> the first segments

        Others args:
          * minmaxtip (list of 2 floats): min-max range in tip
          * minmaxtilt (list of 2 floats): min-max range in tilt
          * tiptiltsteps (list of 2 floats): step-size in tip and tilt

        Returns:
          * tip values explored
          * tilt values explored
          * segments optimized
          * flux values as a 3D array [tip, tilt, segment]
        """
        if not self.mems.connected:
            self.mems.connect()
        self.mems.flat()
        elm, sz = self.mems._clean_segment(elm)
        if elm is None:
            print('There is an issue with how you wrote your elm input. Done.')
            return
        for i in elm:
            if i not in core.FIRSTSEGS:
                print("Segment '{}' is not a FIRST segment. Done.".format(i))
                return
        minmaxtip = sorted(list(map(float, minmaxtip[:2])))
        minmaxtilt = sorted(list(map(float, minmaxtilt[:2])))
        tiptiltsteps = np.abs(list(map(float, tiptiltsteps[:2])))
        tip = np.arange(minmaxtip[0], minmaxtip[1]*(1+1e-8), tiptiltsteps[0])
        tilt = np.arange(minmaxtilt[0], minmaxtilt[1]*(1+1e-8), tiptiltsteps[1])
        pb = Patiencebar(valmax=tip.size*tilt.size, barsize=50, title="Optimization...")
        # empty result array
        NS = len(core.FIRSTSEGS)
        res = np.zeros((tip.size, tilt.size, NS))
        for tip_idx, tip_i in enumerate(tip):
            for tilt_idx, tilt_i in enumerate(tilt):
                self.mems.set_pos(elm, tip=[tip_i]*NS, tilt=[tilt_i]*NS)
                time.sleep(core.MEMSLAG)
                #img = self.cam.Acquire.snap().astype(np.int16)
                img = self.cam.Acquire.snap().astype(np.int16).reshape((496,658)).T
                time.sleep(core.IMGLAG)
                res[tip_idx, tilt_idx] = self._extract_fluxes(elm, img=img - self.dark)
                pb.update()
        self.mems.flat()
        self.show_opti(tip,tilt,elm,res)
        self.mems.set_current_as_on()
        self.mems.shape_on_save('Optimizer_On_CHECK')
        np.save('LatestOptimizerResults_Tip',tip)
        np.save('LatestOptimizerResults_Tilt',tilt)
        np.save('LatestOptimizerResults_Tip',elm)
        np.save('LatestOptimizerResults_Tip',res)




        #return tip, tilt, elm, res

    def show_opti(self, tip, tilt, elm, fluxes):
        """
        Just give all inputs as optimization puked them
        """
        #for idx, seg in enumerate(segs):
	plt.subplot(3,3,1)
        id_plt=1
        for idx, seg in enumerate(core.FIRSTSEGS):
	    plt.subplot(3,3,id_plt)
            plt.matshow(fluxes[:,:,idx], origin='lower',fignum=0)
            plt.title('#'+str(seg))
            y,x = np.unravel_index(fluxes[:,:,idx].argmax(),
                                   (tip.size, tilt.size))
            print("#{:d} - tip: {:.3f}, tilt: {:.3f}".format(seg,tip[y], tilt[x]))
            id_plt+=1
            for i in elm:
        	self.mems.set_pos(seg,0,tip[y],tilt[x])




    def _extract_fluxes(self, elm, img):
        """
        Extracts the injection-blob flux values from a camera image
        """
        fluxes = []
        for idx, seg in enumerate(core.FIRSTSEGS):
            if seg not in elm:
                continue
            box_y, box_x = self._boxcal.boxes[idx]
            # sums the flux in the box and appends to output
            #fluxes.append(dataimg[box_y, box_x].sum())
            fluxes.append(img[box_y, box_x].sum())
        return fluxes



    # def _find_opti_flux(self, tip, tilt, elm, fluxes):
    # 	"""
    # 	Takes the output of the optimiser and creates a new MEMS ON map, and loads it.
    # 	"""
    # 	ONmap=np.zeros([elm,tip,tilt])
    # 	for i in elm:



