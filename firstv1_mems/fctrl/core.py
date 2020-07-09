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


import matplotlib as mat
mat.use('TkAgg')
import matplotlib.backends.backend_tkagg
FigureCanvasTkAgg = mat.backends.backend_tkagg.FigureCanvasTkAgg
import matplotlib.pyplot as plt
plt.ion()
from matplotlib.patches import Rectangle

try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

try:
    input = raw_input
except:
    input = input

import time
import sys
import os
import glob
import numpy as np
from datetime import datetime

from patiencebar import Patiencebar
from scipy.ndimage import gaussian_filter
import IrisAO_PythonAPI  as IrisAO_API


from .param import *


def concat_dir(*args):
    """
    Concatenates the path in ``args`` into a string-path
    """
    return os.path.join(*args)

def home_dir(*args):
    """
    Concatenates the path in ``args`` into a string-path
    """
    return os.path.join(HOME, *args)

def rel_dir(*args):
    """
    Concatenates the path in ``args`` into a relative
    string-path from the package directory
    """
    return concat_dir(ROOT, *args)


AUTHCHARS = range(ord('A'), ord('Z')+1) \
                + range(ord('a'), ord('z')+1) \
                + range(ord('0'), ord('9')+1) \
                + [ord('-'), ord('_')]

ROOT = os.path.dirname(os.path.abspath(__file__))

HOME = os.path.expanduser("~")

PATHCONFIGFILE = home_dir(*PATHCONFIGFILE)
PATHCALMEMS = home_dir(*PATHCALMEMS)
PATHIMG = home_dir(*PATHIMG)


def clean_txt(txt):
    """
    Removes weird characters from txt
    """    
    return "".join([ch for ch in txt if ord(ch) in AUTHCHARS])

def clean_list(ll):
    """
    Returns a list of non-doublon integers
    """
    return sorted(set(list(map(int, ll))))

def clean_pos(arr, ax):
    if ax.lower() == 'tiptilt':
        minmax = [TIPTILTMIN, TIPTILTMAX]
    else:
        minmax = [PISTONMIN, PISTONMAX]
    arr = np.clip(np.asarray(arr, dtype=float), minmax[0], minmax[1])
    if arr.ndim == 0:
        return tuple([arr])
    else:
        return tuple(arr.tolist())

def mask_elm(elm):
    """
    Always give cleaned elm as input
    """
    return np.asarray(elm)-1

def gauss2D(x, y, a=1., x0=0., y0=0., sigma=1., foot=0.):
    Y, X = np.meshgrid(x, y)
    return gaussPt(x=X, y=Y, a=a, x0=x0, y0=y0, sigma=sigma, foot=foot)
			
def gaussPt(x, y, a=1., x0=0., y0=0., sigma=1., foot=0.):
    return a*np.exp(-((x-x0)**2+(y-y0)**2)/(np.sqrt(2)*sigma)**2)+foot


def make_filepath(name, fmt, basepath=None):
    """
    Adds the fmt extension and timestamp to name and join
    it to configuration dir
    """
    if basepath is None:
        basepath = PATHCONFIGFILE
    return os.path.join(basepath,
                        datetime.utcnow().strftime(fmt).format(
                                            name=clean_txt(str(name))))

def make_filepath_nostamp(name, fmt, basepath=None):
    """
    Adds the fmt extension to name and join it to configuration dir
    """
    if basepath is None:
        basepath = PATHCONFIGFILE
    name = clean_txt(str(name)) + os.path.splitext(fmt)[1]
    return os.path.join(basepath, name)

def list_filepath(fmt, basepath=None):
    """
    Returns a list of all files with same fmt extension, sorted
    with the timestamp
    """
    if basepath is None:
        basepath = PATHCONFIGFILE
    pattern = "*" + os.path.splitext(fmt)[1]
    names = glob.glob(os.path.join(basepath, pattern))
    names = [os.path.split(os.path.splitext(item)[0])[1] for item in names]
    return sorted(names, key=lambda x: x.rsplit('_', 1)[-1])
