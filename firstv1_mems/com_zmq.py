################################################################################
##################         ZMQ communication class          ####################
################################################################################


# This is class that works together
# They have to be used together in a script that needs to receive and also 
# send messages and command


import time
import zmq
from threading import Thread


################################################################################
##################            Error managing class          ####################
################################################################################


class MyException(BaseException):
    # Class made to catch errors coming from the subscriber com
    # See in class ComPortSUB
    def __init__(self, current_exception):
        self.current_exception = current_exception

    def __str__(self):
        return str(self.current_exception)


################################################################################
##################              Text color class            ####################
################################################################################


class PColors:
    Red = '\033[91m'
    Green = '\033[92m'
    Blue = '\033[94m'
    Cyan = '\033[96m'
    White = '\033[97m'
    Yellow = '\033[93m'
    Magenta = '\033[95m'
    Grey = '\033[90m'
    Black = '\033[90m'
    Default = '\033[99m'
    ANDOR = Green

    MEMS = Red
    ODL = Blue
    ENDC = '\033[0m'


################################################################################
##################             Subscriber class             ####################
################################################################################


"""

   Pubsub envelope subscriber

   Author: Guillaume Aubert (gaubert) <guillaume(dot)aubert(at)gmail(dot)com>

"""


class ComPortSUB(Thread):
    def __init__(self, publisher, port_SUB, address):
        Thread.__init__(self)
        self.running = False

        self.pub = publisher
        self.port = port_SUB
        self.address = address

        self.start()

    def _creation_socket(self):
        self.context = zmq.Context()
        self.sub = self.context.socket(zmq.SUB)
        self.sub.connect(self.port)
        self.sub.setsockopt(zmq.SUBSCRIBE, self.address)
        self.pub.pprint("Com receiver is initialized (address: %s)" % (self.port))

    def run(self):
        self._creation_socket()
        self.running = True
        while self.running:
            [address_cmd, command] = self.sub.recv_multipart()
            try:
                self.pub.pprint("try com sub")
                exec(command)
            except Exception as cur_exception:
                self.pub.pprint(MyException(cur_exception))

    def stop(self):
        self.pub.pprint("Com receiver is closed (address: %s)" % (self.port))
        self.running = False
        self.sub.close()
        self.context.term()

    def start(self):
        super().start()


################################################################################
##################              Publisher class             ####################
################################################################################


class ComPortPUB(object):
    def __init__(self, port_PUB, client_adress):
        self.port = port_PUB
        self.adress = client_adress

        self.context = zmq.Context()
        self.pub = self.context.socket(zmq.PUB)
        self.pub.bind(self.port)
        self.pprint("\n\nCom transmitter is initialized (address: %s)" % (self.port))

    def pprint(self, message):
        time.sleep(1)  # need time to sleep before sending a message
        self.pub.send_multipart([self.adress, str(message).encode('UTF-8')])

    def stop(self):
        self.pprint("Com transmitter is closed (address: %s)" % (self.port))
        self.pprint("done()")
        self.pub.close()
        self.context.term()
