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
import joystick as jk
import numpy as np
import time
from datetime import datetime
import andorsdk
import os

from .boxcal import BoxCal
from . import core


__all__ = ['AndorCtrl']


class AndorCtrl(jk.Joystick):
    _infinite_loop = jk.deco_infinite_loop()
    _callit = jk.deco_callit()

    _boxcal = BoxCal(nfib=len(core.FIRSTSEGS), with_cam=False)

    @_callit('before', 'init')
    def _init_data(self, *args, **kwargs):
	
        print("Initializing Andor Camera .... ")
        print(andorsdk.__file__)
        self.cam = andorsdk.Andor()

        print("Cooling down the detector...")
        self.cam.Temperature.setpoint = core.CAMERATEMP  # start cooling
        self.cam.Temperature.cooler = core.CAMERACOOLING

        self._txtlog = {}
        self.auto_cmap_adjust = True
        self.log = False
        self.camsize = self.cam.Detector.size
        
        self.lastimg = np.zeros(self.camsize).astype(np.int16)
        self._dark = np.zeros(self.camsize).astype(np.int16)

        self.cam.exposure = core.DEFAULTEXPOSURETIME  # ms
        self.cam.Acquire.Video()

        # needed for boxcal show_boxes
        self._boxcal._szratio = self.camsize[0]*1./self.camsize[1]

        # init the sub img
        self._nsub = [int(np.ceil(np.sqrt(len(core.FIRSTSEGS)))), 0]
        self._nsub[1] = int(np.ceil(len(core.FIRSTSEGS)/self._nsub[0]))

        self._do_boxes()
        
        l = self.boxes_list(ret=True)
        if len(l) > 0:
            self.boxes_load(l[-1])
        self._txtlog = {'dark': False, 'log': self._log,
                        'auto': self.auto_cmap_adjust}

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

    @_callit('after', 'init')
    def _build_frames(self, *args, **kwargs):
        if core.SHOWANDORBIGIMAGE:
            self.img = self.add_frame(
                    jk.Image(name="Andor", pos=(50, 100),
                                size=[self.camsize[1], self.camsize[0]],
                                #size=[self.camsize[0], self.camsize[1]],
                                freq_up=7, cmap='gist_earth'))
        self.subimg = self.add_frame(
                    jk.Image(name="Segments", pos=(650, 50),
                                size=[self._subsize[1]*core.ZOONFACTORSUBIMG,
                                      self._subsize[0]*core.ZOONFACTORSUBIMG],
                                freq_up=7, cmap='gist_earth',
                                axrect=[0,0,1,1], centerorig=False))
        self.cts = self.add_frame(
                    jk.Text(name="Counts", size=(350, 230), pos=(10, 10),
                            freq_up=10, rev=True, mark_line=False,
                            scrollbar=False))
        for idx, seg in enumerate(core.FIRSTSEGS):
            sby, sbx = self._subimgboxes[idx]
            self.subimg.ax.text(sbx.start + core.MARGIN, sby.stop,
                                "#"+str(seg))

    @_infinite_loop(wait_time=0.12)
    def _get_data(self):
        try:
            #self.lastimg = self.cam.Acquire.Newest(1).astype(np.int16)
            self.lastimg = self.cam.Acquire.Newest(1).astype(np.int16).reshape((496,658)).T
        except andorsdk.AndorError:
            return
        data = self.lastimg-self.dark
        if self._log:
            data = np.log(np.clip(data, a_min=data[data>0].min(), a_max=1e99))
        if core.SHOWANDORBIGIMAGE:
            self.img.set_data(data)
        for idx, seg in enumerate(core.FIRSTSEGS):
            by, bx = self._boxcal.boxes[idx]
            cut = data[by.start:by.stop,bx.start:bx.stop]
            sby, sbx = self._subimgboxes[idx]
            self._txtlog['sum'+str(seg)] = cut.sum()
            self._txtlog['max'+str(seg)] = cut.max()
            self.lastsubimg[sby.start:sby.stop,sbx.start:sbx.stop] = cut
        self.subimg.set_data(self.lastsubimg)
        self.cts.clear()
        # auto-adjust cmap
        if self._auto_cmap_adjust:
            bds = data.min(), data.max()
            if core.SHOWANDORBIGIMAGE:
                self.img.cm_bounds = bds
            self.subimg.cm_bounds = bds
        self._txtlog['min'], self._txtlog['max'] = self.subimg.cm_bounds
        self.cts.add_text(core.DISPLAYLOG.format(**self._txtlog))

    def save_latest(self, name, override=False):
        """
        Saves the latest image to file

        Args:
          * name (str): the name of the file
          * override (bool): whether to override an existing file
        """
        name = os.path.join(core.PATHIMG,
                            datetime.utcnow().strftime(core.IMGFILENAME)\
                                    .format(name=core.clean_txt(str(name))))
        if os.path.isfile(name) and not bool(override):
            print("File '{}' already exists".format(name))
            return
        hdulist = pf.HDUList()
        hd = pf.Header([
            ('TYPE', 'img-dark', 'See other hdus for img or dark data'),
            ('ITIME', self.cam.exposure, 'in ms'),
            ('TIME', datetime.utcnow().strftime('%H%M%S'), 'Time HHMMSS'),
            ('MSTIME', datetime.utcnow().strftime('%f'), 'Time microseconds'),
            ('DATE', datetime.utcnow().strftime('%Y%m%d'), 'Date YYYYMMDD'),
            ('COOLER', self.cam.Temperature.cooler, 'Cooler on/off'),
            ('TEMP', self.cam.Temperature.read['temperature'],
                    'Current temperature (C)'),
            ('SETTEMP', self.cam.Temperature.setpoint,
                    'Target temperature (C)')
            ])
        hd.add_comment('Written by Guillaume SCHWORER')
        last = self.lastimg
        dark = self.dark
        hdulist.append(pf.ImageHDU(data=last-dark, header=hd))
        hdulist.append(pf.ImageHDU(data=last,
                                   header=pf.Header([('TYPE', 'img')])))
        hdulist.append(pf.ImageHDU(data=dark,
                                   header=pf.Header([('TYPE', 'dark')])))
        hdulist.writeto(name, clobber=override)
        print("Saved in '{}'".format(name))

    def save_dark(self, name, override=False):
        """
        Saves the current dark to file

        Args:
          * name (str): the name of the file
          * override (bool): whether to override an existing file
        """
        name = os.path.join(core.PATHIMG,
                            datetime.utcnow().strftime(core.IMGFILENAME)\
                                    .format(name=core.clean_txt(str(name))))
        if os.path.isfile(name) and not bool(override):
            print("File '{}' already exists".format(name))
            return
        hdulist = pf.HDUList()
        hd = pf.Header([
            ('TYPE', 'dark', ''),
            ('ITIME', self.cam.exposure, 'in ms'),
            ('TIME', datetime.utcnow().strftime('%H%M%S'), 'Time HHMMSS'),
            ('MSTIME', datetime.utcnow().strftime('%f'), 'Time microseconds'),
            ('DATE', datetime.utcnow().strftime('%Y%m%d'), 'Date YYYYMMDD'),
            ('COOLER', self.cam.Temperature.cooler, 'Cooler on/off'),
            ('TEMP', self.cam.Temperature.read['temperature'],
                    'Current temperature (C)'),
            ('SETTEMP', self.cam.Temperature.setpoint,
                    'Target temperature (C)')
            ])
        hd.add_comment('Written by Guillaume SCHWORER')
        hdulist.append(pf.ImageHDU(data=self.dark, header=hd))
        hdulist.writeto(name, clobber=override)
        print("Saved in '{}'".format(name))

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

    @property
    def clims(self):
        """
        The [min, max] of the view
        """
        return self.subimg.cm_bounds
    @clims.setter
    def clims(self, value):
        if core.SHOWANDORBIGIMAGE:
            self.img.cm_bounds = value
        self.subimg.cm_bounds = value

    @_callit('after', 'exit')
    def _exit_warning(self):
        print("Exiting")
        self.cam.shutdown()
        time.sleep(1)

    @property
    def dark(self):
        return self._dark
    @dark.setter
    def dark(self, value):
        print('Use acq_dark or rm_dark instead')

    def acq_dark(self):
        """
        Acquires a dark frame that will be subtracted to the
        current video stream
        """
        self._dark = self.cam.Acquire.Newest(1).astype(np.int16)
        self._txtlog['dark'] = True

    def rm_dark(self):
        """
        Deletes the current dark frame
        """
        self._dark = np.zeros(self.camsize).astype(np.int16)
        self._txtlog['dark'] = False

    @property
    def auto_cmap_adjust(self):
        """
        Set to True to activate automated color-map min-max adjustment,
        or False to deactivate it
        """
        return self._auto_cmap_adjust

    @auto_cmap_adjust.setter
    def auto_cmap_adjust(self, value):
        self._auto_cmap_adjust = bool(value)
        self._txtlog['auto'] = self._auto_cmap_adjust

    @property
    def log(self):
        """
        Set to True to activate log view, or False to deactivate it
        """
        return self._log

    @log.setter
    def log(self, value):
        self._log = bool(value)
        self._txtlog['log'] = self._log
