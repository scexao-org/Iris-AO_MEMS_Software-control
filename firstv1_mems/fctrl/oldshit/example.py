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

# sudo /home/slacour/anaconda2/bin/ipython

import numpy as np
import sys
sys.path.append('/home/slacour/Documents/lib/firstctrl')
import fctrl as fc
import time
c = fc.ctrl.Ctrl()
# a graph frame should pop up

c.mems.connect()  # get connection
c.mems.flat()

c.boxcal.centers=np.array([[ 24, 254],[ 50, 254],[ 89, 256],[141, 257],[209, 255],[285, 257],[374, 258],[474, 255]])



maxes = 5
segs = 'first'
tips = np.linspace(-maxes, maxes, 100)
res = []
c.mems.flat()
for tip in tips:
    c.mems.set_pos(segs, tip=[tip]*c.mems.first_nseg)
    time.sleep(0.05)
    res.append(c.mems.get_pos(segs)[0]) # 0=tip, 1=tilt, 2=piston


plt.figure()
plt.plot(tips, tips, 'g-', lw=2)
for r in np.asarray(res).T:
    plt.plot(tips, r)

plt.xlabel('Tip Sent (mrad)')
plt.ylabel('Mems Tip Response (mrad)')




c.start()

c.mems.set_pos([1], tip=[0.2], tilt=[-0.2])


# finally, disconnect:
c.mems.disconnect()
