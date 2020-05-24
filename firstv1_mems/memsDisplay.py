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


################################################################################
##################             Mems Live Viewer             ####################
################################################################################

# from __future__ import unicode_literals

import core
np = core.np
os = core.os

import time
from astropy.io import fits

from memsCtrl import Mems
from com_zmq import PColors

from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5

if is_pyqt5():
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure


__all__ = ['MemsWindow']


FCTRL_PATH = os.getcwd() + "/firstv1_mems/"
MEMS_INDEX_NAME = "mems_index.fits"
MEMS_OPD_NAME = "mems_opd.fits"
MEMS_CENTERS_NAME = "mems_centers.txt"

# ACTIVE_MEMS_SEGS = [22, 11, 27, 20, 2, 5, 36, 17, 31]
ACTIVE_MEMS_SEGS = np.array([37, 9, 24, 35, 7, 4, 33, 15, 28])  # new mapp, 15_11_2019


################################################################################
##################             Plot application             ####################
################################################################################


class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.fig.set_tight_layout(True)

        self.compute_initial_figure()

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass


class MemsDynamicMplCanvas(MyMplCanvas):
    """A canvas that updates itself every second with a new plot."""

    def __init__(self, publisher, *args, **kwargs):
        self.pub = publisher

        # Initialise the different maps for the display of the mems surface
        self.map_index, self.map_index_h = fits.getdata(FCTRL_PATH + MEMS_INDEX_NAME, header=True)
        self.map_height, self.map_width = np.shape(self.map_index)
        self.map_opd = np.ones((self.map_height, self.map_width))
        self.map_opd[self.map_index == 0] = 0
        self.map_centers = np.loadtxt(FCTRL_PATH + MEMS_CENTERS_NAME, dtype=np.int)
        self.map_radius_x = np.ones((self.map_height, self.map_width))
        self.map_radius_y = np.ones((self.map_height, self.map_width))
        self.compute_radii()

        # Initialise the figure (canvas)
        MyMplCanvas.__init__(self, *args, **kwargs)
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(100)

        self.mems = Mems(self.pub)
        self.mems.connect()
        self.mems.flat()

    def compute_initial_figure(self):
        self.axes.imshow(self.map_opd, interpolation='nearest', aspect='auto', origin='lower', cmap='jet')

    def update_figure(self):
        if self.mems.connected:
            # Get pos of mems
            piston, tip, tilt = self.mems.get_pos('all')

            # Push new data to the graph
            self.imshow_pist_tiptilt(piston, tip, tilt)
        else:
            self.compute_initial_figure()

    def imshow_pist_tiptilt(self, piston_arr, tip_arr, tilt_ar):
        # Compute piston, tip and tilt in the opd map
        for seg_ind in range(37):
            tip_value = self.map_radius_x[self.map_index == seg_ind + 1] * np.sin(tip_arr[seg_ind] * 10 ** (-3))
            tilt_value = self.map_radius_y[self.map_index == seg_ind + 1] * np.sin(tilt_ar[seg_ind] * 10 ** (-3))
            self.map_opd[self.map_index == seg_ind + 1] = piston_arr[seg_ind] + tip_value + tilt_value

        self.axes.clear()
        self.axes.imshow(self.map_opd, interpolation='nearest', aspect='auto', origin='lower', cmap='jet')
        self.draw()

    def compute_radii(self):
        for pix_x in range(self.map_height):
            for pix_y in range(self.map_width):
                seg_ind = self.map_index[pix_x, pix_y]
                if seg_ind != 0:
                    radius_x = pix_x - self.map_centers[0, seg_ind - 1]
                    self.map_radius_x[pix_x, pix_y] = radius_x
                    radius_y = pix_y - self.map_centers[1, seg_ind - 1]
                    self.map_radius_y[pix_x, pix_y] = radius_y


class MemsWindow(QtWidgets.QMainWindow):
    def __init__(self, publisher):
        QtWidgets.QMainWindow.__init__(self)

        self.pub = publisher

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.main_widget = QtWidgets.QWidget(self)

        layout = QtWidgets.QVBoxLayout(self.main_widget)
        dc = MemsDynamicMplCanvas(self.pub, self.main_widget, width=5, height=4, dpi=100)
        layout.addWidget(dc)
        self.mems = dc.mems

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

    def file_quit(self):
        self.close()

    def close_event(self, ce):
        self.fileQuit()

    def about(self):
        QtWidgets.QMessageBox.about(self, "About", "Coucou")


"""
###############################################################################
# Gui for python 2
###############################################################################


import joystick as jk
import core
np = core.np
from memsCtrl import Mems
from com_zmq import PColors


__all__ = ['MemsWindow']


class MemsWindow(jk.Joystick):
    # initialize the infinite loop decorator
    _infinite_loop = jk.deco_infinite_loop()
    _callit = jk.deco_callit()

    @_callit('before', 'init')
    def _init_data(self, **kwargs):
        pass

    def __init__(self, publisher):
        super(MemsWindow, self).__init__()
        self.pub = publisher
        self._pprint("    Initialising Mems...\n")

    @_callit('after', 'init')
    def _build_frames(self, *args, **kwargs):
        self.tiptilt = self.add_frame(
                   jk.GraphMulti(name="MEMS : Tip-Tilt", size=(340, 200), pos=(760, 25),
                                 fmt="ko", xnpts=len(core.FIRSTSEGS),
                                 nlines=len(core.FIRSTSEGS), freq_up=5, bgcol="w",
                                 numbering=True, lbls=core.FIRSTSEGS, legend=False,
                                 #xylim=(core.TIPTILTMIN, core.TIPTILTMAX,
                                 #       core.TIPTILTMIN, core.TIPTILTMAX),
                                 xylim=(-1, 1,
                                   -1, 1),
                                 xlabel='tip', ylabel='tilt'))
        self.piston = self.add_frame(
                   jk.Graph(name="MEMS : Piston", size=(340, 200), pos=(760, 254),
                            fmt="rs", xnpts=len(core.FIRSTSEGS),
                            freq_up=5, bgcol="w",
                            xylim=(-3, np.max(core.FIRSTSEGS) + 3,
                                   core.PISTONMIN, core.PISTONMAX),
                            xlabel='segment', ylabel='piston'))
        self.mems = Mems()

    def _pprint(self, message):
        '''
        Print message with a color define in the class PColors.
        '''
        self.pub.pprint(PColors.MEMS + str(message) + PColors.ENDC)

    @_callit('before', 'exit')
    def _exit_warning(self):
        print('Exiting')
        self.mems.disconnect()

    @_infinite_loop(wait_time=0.2)
    def _get_pos(self):
        '''
        Loop starting with simulation start, getting data and
        pushing it to the graph every 0.2 seconds
        '''
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
"""