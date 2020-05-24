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


import os
import time
import zmq
import sys
import numpy as np
from threading import Thread

import memsCtrl as mCl
from com_zmq import PColors
from errorManaging import MyException


################################################################################
##################             Subscriber class             ####################
################################################################################


port_SUB = "tcp://localhost:5550"
server_address = b"M"

port_PUB = "tcp://*:5558"#################a remettre sur 5552, apres restart de l'ordi
client_address = b"P"


"""

   Pubsub envelope subscriber

   Author: Guillaume Aubert (gaubert) <guillaume(dot)aubert(at)gmail(dot)com>

"""


class ComPortSUB(Thread):
    def __init__(self, publisher, port_SUB, address):
        super().__init__()
        self.running = True

        self.pub = publisher
        self.port = port_SUB
        self.address = address

        global m

        self.start()

    def _creation_socket(self):
        self.context = zmq.Context()
        self.sub = self.context.socket(zmq.SUB)
        self.sub.connect(self.port)
        self.sub.setsockopt(zmq.SUBSCRIBE, b'')
        self.pub.pprint("Com receiver is initialized (address: %s)" % (self.port))

    def run(self):
        self._creation_socket()
        while self.running:
            cmd_dict = self.sub.recv_pyobj()
            if cmd_dict["address"] == self.address:
                cmd_dict.pop("address")
                try:
                    if cmd_dict["command"] == "done()":
                        self.running = False
                        done()
                    else:
                        command = getattr(m, cmd_dict["command"])
                        cmd_dict.pop("command")
                        command(**cmd_dict)
                except Exception as cur_exception:
                    self.pub.pprint(MyException(cur_exception))
            else:
                pass
        #dself.stop()

    def stop(self):
        self.pub.pprint("Com receiver is closed (address: %s)" % (self.port))
        self.sub.close()
        self.context.term()

    def start(self):
        super().start()


################################################################################
##################              Publisher class             ####################
################################################################################


class ComPortPUB(object):
    def __init__(self, port_PUB, client_address):
        self.port = port_PUB
        self.address = client_address

        self.context = zmq.Context()
        self.pub = self.context.socket(zmq.PUB)
        self.pub.bind(self.port)
        self.pprint("\n\nCom transmitter is initialized (address: %s)" % (self.port))

    def pprint(self, message):
        time.sleep(1)# need time to sleep before sending a message
        self.pub.send_multipart([self.address, str(message).encode('UTF-8')])

    def stop(self):
        self.pprint("Com transmitter is closed (address: %s)" % (self.port))
        self.pprint("done()")
        self.pub.close()
        self.context.term()


################################################################################
##################           Function definition            ####################
################################################################################


def done(mems_connected=True):
    if mems_connected:
        m.disconnect()
    mems_sub.stop()
    time.sleep(1)
    mems_pub.pprint(PColors.MEMS + "    Mems shut down COMPLETE\n" + PColors.ENDC)
    mems_pub.stop()
    os._exit(1)


################################################################################
##################              Main process                ####################
################################################################################


if __name__ == "__main__":
    ### Initialize the communication transmitter ###
    mems_pub = ComPortPUB(port_PUB, client_address)


    ### Initialize the communication receiver ###
    mems_sub = ComPortSUB(mems_pub, port_SUB, server_address)


    ###	Initialise Mems Live Viewer ###
    milk_solution = False
    if milk_solution:
        m = mCl.Mems(mems_pub)
    else:
        import memsDisplay as mDy
        Mems_Qt_app = mDy.QtWidgets.QApplication(sys.argv)
        app = mDy.MemsWindow(mems_pub)
        m = app.mems
        app.show()
        Mems_Qt_app.exec_()

    mems_pub.pprint(PColors.MEMS + "    MEMS initialised\n" + PColors.ENDC)