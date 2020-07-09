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

import time
from . import core
os = core.os
np = core.np
glob = core.glob
IrisAO_API = core.IrisAO_API


__all__ = ['Mems']

class Mems(object):
    def __init__(self):
        self._INITIALDIR = os.getcwd()
        self._connected = False
        self._pos = np.zeros((core.NSEGMENTS, 3))
        self._off = np.c_[np.ones((core.NSEGMENTS, 2))*core.TIPTILTMIN,
                          np.zeros((core.NSEGMENTS,1))]
        self._on = np.zeros((core.NSEGMENTS, 3))

    def __enter__(self):
        return self

    def __del__(self):
        self.flat()
        self.disconnect()

    __exit__ = __del__

    def connect(self):
        """
        Connects to the Mems
        """
        # already connected
        if self._connected:
            return
        # hack to CD to the folder with the cal files
        os.chdir(core.PATHCALMEMS)
        disableHardware = False
        self._mirror = IrisAO_API.MirrorConnect(core.MIRRORNUM,
                                                core.DRIVERNUM,
                                                disableHardware)
        # CD to previous folder
        os.chdir(self._INITIALDIR)
        self._connected = True

    def disconnect(self):
        """
        Disconnects the Mems
        """
        if not self._connected:
            print("ERROR: Not connected to Mems")
            return
        self.flat()
        IrisAO_API.MirrorRelease(self._mirror)
        self._connected = False

    def exit(self):
        """
        Disconnects the Mems
        """
        self.disconnect()

    @property
    def connected(self):
        """
        If there is an active link to the Mems
        """
        return self._connected

    @connected.setter
    def connected(self, value):
        print("Read-only")

    @property
    def first_nseg(self):
        return len(core.FIRSTSEGS)

    @first_nseg.setter
    def first_nseg(self, value):
        print('Read-only')

    @property
    def first_seg(self):
        """
        The favorite segments of First
        """
        return core.FIRSTSEGS

    @first_seg.setter
    def first_seg(self, value):
        print('Read-only')
        
    def flat(self):
        """
        Sets all tip, tilt, piston to nil
        """
        if not self._connected:
            print("ERROR: Not connected to Mems")
            return
        IrisAO_API.MirrorCommand(self._mirror,
                                 IrisAO_API.MirrorInitSettings)
        self._pos = np.zeros((core.NSEGMENTS, 3))

    def _moveit(self, arr, elm):
        elm, sz = self._clean_segment(elm)
        if elm is None:
            print("Wrong input, should be int, list of int, 'first', or 'all'")
            return
#       tip, tilt = arr[:,:2][core.mask_elm(elm)].T
	piston, tip, tilt = arr[:,:][core.mask_elm(elm)].T
#       self.set_pos(elm=elm, piston=[0]*sz, tip=tip, tilt=tilt)
        self.set_pos(elm=elm, piston=piston, tip=tip, tilt=tilt)

    def off(self, elm='all'):
        """
        Sets all piston to nil; sets tip & tilt to min range
        """
        self._moveit(self._off, elm)

    def on(self, elm='first'):
        """
        Sets all piston to nil; sets tip & tilt to min range
        """
        self._moveit(self._on, elm)

    def _clean_segment(self, elm):
        if isinstance(elm, int):
            return [elm], 1
        elif hasattr(elm, '__iter__'):
            elm = [item for item in core.clean_list(elm)\
                            if item > 0 and item <= core.NSEGMENTS]
        elif elm.lower() == 'first':
            elm = core.FIRSTSEGS
        elif elm.lower() == 'all':
            elm = range(1, core.NSEGMENTS+1)
        else:
            return None, None
        return elm, len(elm)

    def get_pos(self, elm):
        """
        Gets the positions of the mems segments

        ex: tip, tilt, piston = m.get_pos('first')

        Input argument elm can be:
          * int -> 1 segment
          * list of int -> n segment
          * 'first' -> the first segments
          * 'all' -> all segments
        """
        if not self._connected:
            print("ERROR: Not connected to Mems")
            return
        elm, sz = self._clean_segment(elm)
        if elm is None:
            print("Wrong input, should be int, list of int, 'first', or 'all'")
            return
        # (tip, tilt, piston), locked, reachable
        return np.asarray(IrisAO_API.\
                  GetMirrorPosition(self._mirror, elm)[0]).T

    def set_pos(self, elm, piston=None, tip=None, tilt=None):
        """
        Sets the positions of the mems segments

        Input argument elm can be:
          * int -> 1 segment
          * list of int -> n segment
          * 'first' -> the first segments
          * 'all' -> all segments

        tip, tilt, piston can be left to None to remain unchanged
        if not None, tip, tilt and piston should be a list of floats
        with same size as elm
        """
        if not self._connected:
            print("ERROR: Not connected to Mems")
            return
        elm, sz = self._clean_segment(elm)
        # check input

	if piston is None:
            piston = self._pos[:,0][core.mask_elm(elm)]
        elif np.size(piston) != sz:
            print('Wrong size, should be same as elm: {}'.format(sz))
            return
        piston = core.clean_pos(piston, ax='piston')
        
	if tip is None:
            tip = self._pos[:,1][core.mask_elm(elm)]
        elif np.size(tip) != sz:
            print('Wrong size, should be same as elm: {}'.format(sz))
            return
        tip = core.clean_pos(tip, ax='tiptilt')
        
	if tilt is None:
            tilt = self._pos[:,2][core.mask_elm(elm)]
        elif np.size(tilt) != sz:
            print('Wrong size, should be same as elm: {}'.format(sz))
            return
        tilt = core.clean_pos(tilt, ax='tiptilt')
        
	new_val = np.vstack((piston, tip, tilt)).T
        self._pos[core.mask_elm(elm),:] = new_val
        new_val = [tuple(item) for item in new_val]
        # replace in local values
        IrisAO_API.SetMirrorPosition(self._mirror, elm, new_val)
        IrisAO_API.MirrorCommand(self._mirror, IrisAO_API.MirrorSendSettings)

    def _shape_save(self, name, arr, override):
        if not self._connected:
            print("ERROR: Not connected to Mems")
            return
        if os.path.isfile(name) and not bool(override):
            print("File '{}' already exists".format(name))
            return
        np.savetxt(name, arr, header="PISTON, TIP, TILT")
        print("Saved in '{}'".format(name))

    def shape_save(self, name, override=False):
        """
        Saves the current shape into a file

        Args:
          * name (str): the name of the file
          * override (bool): whether to override a file if already
            existing
        """
        name = core.make_filepath(name, core.SHAPEFILENAME)
        self._pos = self.get_pos('all').T
        self._shape_save(name, self._pos, override)

    def shape_on_save(self, name, override=False):
        """
        Saves the current shape ON into a file

        Args:
          * name (str): the name of the file
          * override (bool): whether to override a file if already
            existing
        """
        name = core.make_filepath(name, core.SHAPEONFILENAME)
        self._shape_save(name, self._pos, override)
        self._on = self._pos.copy()

    def shape_off_save(self, name, override=False):
        """
        Saves the current shape OFF into a file

        Args:
          * name (str): the name of the file
          * override (bool): whether to override a file if already
            existing
        """
        name = core.make_filepath(name, core.SHAPEOFFFILENAME)
        self._shape_save(name, self._pos, override)
        self._off = self._pos.copy()

    def shape_list(self):
        """
        Shows all available shape files saved
        """
        print("\n".join(core.list_filepath(core.SHAPEFILENAME)))

    def shape_on_list(self):
        """
        Shows all available shape ON files saved
        """
        print("\n".join(core.list_filepath(core.SHAPEONFILENAME)))

    def shape_off_list(self):
        """
        Shows all available shape OFF files saved
        """
        print("\n".join(core.list_filepath(core.SHAPEOFFFILENAME)))

    def _shape_delete(self, name):
        if os.path.isfile(name):
            os.remove(name)
            print("Removed: '{}'".format(name))
        else:
            print("File '{}' not found".format(name))

    def shape_delete(self, name):
        """
        Deletes a shape file saved

        Args:
          * name (str): the name of the file
        """
        self._shape_delete(
            core.make_filepath_nostamp(name, core.SHAPEFILENAME))

    def shape_on_delete(self, name):
        """
        Deletes a shape ON file saved

        Args:
          * name (str): the name of the file
        """
        self._shape_delete(
            core.make_filepath_nostamp(name, core.SHAPEONFILENAME))

    def shape_off_delete(self, name):
        """
        Deletes a shape OFF file saved

        Args:
          * name (str): the name of the file
        """
        self._shape_delete(
            core.make_filepath_nostamp(name, core.SHAPEOFFFILENAME))

    def _shape_load(self, name):
        if not self._connected:
            print("ERROR: Not connected to Mems")
            return None
        if os.path.isfile(name):
            l = np.loadtxt(name)
            print("Loaded '{}'".format(name))
            return l
        else:
            print("File '{}' not found".format(name))
            return None

    def shape_load(self, name):
        """
        Loads a shape file previously saved

        Args:
          * name (str): the name of the file
        """
        name = core.make_filepath_nostamp(name, core.SHAPEFILENAME)
        res = self._shape_load(name)
        if res is not None:
            self._moveit(np.loadtxt(name), 'all')

    def shape_on_load(self, name):
        """
        Loads a shape ON file previously saved

        Args:
          * name (str): the name of the file
        """
        name = core.make_filepath_nostamp(name, core.SHAPEONFILENAME)
        res = self._shape_load(name)
        if res is not None:
            self._on = np.loadtxt(name)

    def shape_off_load(self, name):
        """
        Loads a shape OFF file previously saved

        Args:
          * name (str): the name of the file
        """
        name = core.make_filepath_nostamp(name, core.SHAPEOFFFILENAME)
        res = self._shape_load(name)
        if res is not None:
            self._off = np.loadtxt(name)


    ##### Seb & Nick's additions - Might be broke #########
    def piston_scan(self,elm, piston_begin, piston_end, step, wait_time):

        """
        Piston Scan function. Format is piston_scan(Seg#, Where to begin, Where to end, stepsize,wait time).
        It will then scan through once. 
        """
        nb_steps=int((abs(piston_end)+abs(piston_begin))/step)
        #print nb_steps
        #print 'Initiating ramp from '+str(piston_begin)+' to '+str(piston_end)+' with '+str(nb_steps)+' steps'
        print "MEMS Scanning...."
        for i in range(0,nb_steps+1):
            self.set_pos(elm, piston_begin+i*step,0,0)
            #print piston_begin+i*step
            #print 'Piston step nb '+str(i+1)
            time.sleep(wait_time)
