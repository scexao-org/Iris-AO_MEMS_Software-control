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


import joystick as jk
from . import core
np = core.np
from .mems import Mems


__all__ = ['MemsCtrl']


class MemsCtrl(jk.Joystick):
    # initialize the infinite loop decorator
    _infinite_loop = jk.deco_infinite_loop()
    _callit = jk.deco_callit()

    @_callit('before', 'init')
    def _init_data(self, **kwargs):
        # some variable init
        pass

    @_callit('after', 'init')
    def _build_frames(self, *args, **kwargs):
        self.tiptilt = self.add_frame(
                   jk.GraphMulti(name="tip-tilt", size=(500, 500), pos=(50, 50),
                            fmt="ko", xnpts=len(core.FIRSTSEGS),
                            nlines=len(core.FIRSTSEGS), freq_up=5, bgcol="w",
                            numbering=True, lbls=core.FIRSTSEGS, legend=False,
                            xylim=(core.TIPTILTMIN, core.TIPTILTMAX,
                                   core.TIPTILTMIN, core.TIPTILTMAX),
                            xlabel='tip', ylabel='tilt'))
        self.piston = self.add_frame(
                   jk.Graph(name="Piston", size=(500, 500), pos=(650, 50),
                            fmt="rs", xnpts=len(core.FIRSTSEGS),
                            freq_up=5, bgcol="w",
                            xylim=(-1, np.max(core.FIRSTSEGS)+1,
                                   core.PISTONMIN, core.PISTONMAX),
                            xlabel='segment', ylabel='piston'))
        self.mems = Mems()

    @_callit('before', 'exit')
    def _exit_warning(self):
        print('Exiting')
        self.mems.disconnect()

    @_infinite_loop(wait_time=0.2)
    def _get_pos(self):
        """
        Loop starting with simulation start, getting data and
        pushing it to the graph every 0.2 seconds
        """
        # If the connection to the mems got killed
        if self.mems.connected:
            # get pos of mems
            piston, tip, tilt = self.mems.get_pos('first')
            # push new data to the graph
            self.piston.set_xydata(core.FIRSTSEGS, piston)
            self.tiptilt.set_xydata(x=tip.reshape((tip.size, 1)),
                                    y=tilt.reshape((tilt.size, 1)))
        else:
            self.running = False
