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

import numpy as np
import fctrl as fc
import time
import matplotlib.pyplot as plt


print("\n\n\n")


# init control object
c = fc.MemsCtrl()
# get connection
c.mems.connect()
# reset flat
c.mems.flat()
# start real time
c.start()

m = c.mems

done = c.exit

print("Type m.<tab> to list mems commands\n"\
      "Type m.something? to view documentation about 'something'"\
      "Type done() to disconnect mems and close viewing")
