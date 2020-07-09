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
tkinter = core.tkinter
mat = core.mat
FigureCanvasTkAgg = core.FigureCanvasTkAgg


__all__ = ['ClickImg']

class ClickImg(object):
    def __init__(self, daddy, img, cmap_minmax, cmap):
        self._img = np.asarray(img)
        self._daddy = daddy
        self._cmap = cmap
        self._cmap_minmax = cmap_minmax
        self._success = False
        self.nclicks = int(self._daddy._nfib)
        self._window = tkinter.Tk()
        self._window.title('Click on the {:d} blobs from bottom to top'.format(self.nclicks))
        self._window.protocol("WM_DELETE_WINDOW", self._exit)
        self._window.geometry("{}x{}+{}+{}".format(*(self._img.T.shape+(50,50))))
        self._frame = tkinter.Frame(self._window)
        self._frame.pack()
        self._frame.focus_set()
        self._fig = mat.figure.Figure()
        self._ax = self._fig.add_axes((0,0,1,1))
        self._canvas = FigureCanvasTkAgg(self._fig, master=self._window)
        self._canvas.show()
        self._canvas.get_tk_widget().pack(side=tkinter.TOP,
                                          fill=tkinter.BOTH,
                                          expand=True)
        self._canvas._tkcanvas.pack(side=tkinter.TOP,
                                    fill=tkinter.BOTH,
                                    expand=True)
        self._canvas.callbacks.connect('button_press_event', self._click)
        self._ax.imshow(self._img, cmap=cmap, vmin=cmap_minmax[0],
                        vmax=cmap_minmax[1], origin='lower')
        self._ax.grid(color='k', lw=1)
        self._canvas.draw()
        self.clicks = np.zeros((self.nclicks, 2), dtype=int)
        self._curr_click = 0

    def _click(self, event):
        self.clicks[self._curr_click] = int(event.y), int(event.x)
        self._curr_click += 1
        if self._curr_click >= self.nclicks:
            self._daddy.centers = self.clicks
            self._daddy.show_boxes(self._img, cmap=self._cmap,
                                   cmap_minmax=self._cmap_minmax)
            self._exit()

    def _exit(self):
        self._window.destroy()
