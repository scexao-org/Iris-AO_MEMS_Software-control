################################################################################
##################            Main control script           ####################
################################################################################
"""
This program calls the control functions for the Andor camera
written in the file "andorCtrl_science.py".

It allows the user to type commands with their names in order to execute
them and send a corresponding command to the script "andorCtrl_science.py"
in which it will be executed.

"""

import time
import os
import zmq
from threading import Thread


#import FIRST_Ixion as FI 
# from FIRST_Ixion.andorCtrl_science import AndorCtrl
#import FIRST_mems as Fm
#from FIRST_mems.memsCtrl import MemsCtrl
from FIRST_mems.memsCtrl import MemsCtrl



################################################################################
##################             Global variables             ####################
################################################################################


# Communication
port_PUB_comps = "tcp://*:5550"
port_PUB_print = "tcp://*:5551"

client_address_print = b"P"
client_address_andor = b"A"
client_address_mems = b"M"

component_address = {'print': client_address_print,
                     'andor': client_address_andor,
                     'mems': client_address_mems,
                     'cmd': 'cmd'}


# Mems
# ACTIVE_MEMS_SEGS = [22, 11, 27, 20, 2, 5, 36, 17, 31]
ACTIVE_MEMS_SEGS = [37, 9, 24, 35, 7, 4, 33, 15, 28]  # new mapp, 15_11_2019


################################################################################
##################           Decorator definitions          ####################
################################################################################


def add_command(comp_method):
    def decorator(original_method):
        def modified_func(*args, **kwargs):
            kwargs['command'] = comp_method
            return original_method(*args, **kwargs)
        # Set the doctring to the component method one
        if comp_method.__doc__ is not None:
            modified_func.__doc__ = original_method.__doc__
            modified_func.__doc__ = comp_method.__doc__
        return modified_func
    return decorator


def cmd_compatibility():
    def decorator(cmd_method):
        """The decorator."""

        def modified_func(self, *args, **kwargs):
            """Check if the given arguments (args and kwargs) correspond
            to those needed to comp_method."""

            # Retrieve the component method
            comp_method = kwargs['command']

            # Retrieve the args and the kwargs of the component method
            comp_arguments = comp_method.__code__.co_varnames
            len_arguments = comp_method.__code__.co_argcount
            comp_kwargs_value = comp_method.__defaults__

            # Check if the given kwargs (kwargs) are the same as the expected ones (comp_arguments)
            if comp_kwargs_value is not None:
                len_diff = len_arguments - len(comp_kwargs_value)  # Nbre of unamed arguments

                for key in kwargs:
                    if (key != 'command') and (key not in comp_arguments[len_diff:]):
                        raise TypeError("{0}() got an unexpected keyword argument '{1}'"
                                        .format(comp_method.__name__, key))
            else:
                len_diff = len_arguments
            
            if len_diff > 1:
                # Check if there is the right number of expected arguments given
                if len_diff - 1 != len(args):
                    raise TypeError("{0}() takes {1} positional argument but {2} were given"
                                    .format(comp_method.__name__, len_diff - 1, len(args)))

                # Put the unamed arguments in kwargs
                for i in range(1, len_diff):
                    kwargs[comp_arguments[i]] = args[i-1]
            return cmd_method(self, *args, **kwargs)
        return modified_func
    return decorator


################################################################################
##################              Command class               ####################
################################################################################


class FirstCommand:
    def __init__(self, comp_class, publisher, address):
        self.comp_class = comp_class
        self.pub = publisher
        self.client_address = address

        # Retrieve the methods of the component class
        comp_class_dict = self.comp_class.__dict__

        # Set all the methods according to the component class
        for key, value in comp_class_dict.items():
            if not key.startswith('__'):
                self.__dict__[key] = add_command(value)(self.send_pyobj_cmd)

    @cmd_compatibility()
    def send_pyobj_cmd(self, *args, **kwargs):
        """ """
        # Customised send_pyobj() function, embedding the address and parameters sending.
        kwargs['command'] = kwargs['command'].__name__
        kwargs["address"] = self.client_address
        #for key, value in kwargs.items():
        #    print(key, value)
        self.pub.send_pyobj(kwargs)


################################################################################
##################              Andor functions             ####################
################################################################################


################################################################################
##################              Mems functions              ####################
################################################################################


def mems_seg_on(segment):
    """Set a specific segment to the FLAT position (0,0,0)."""
    m.set_pos(segment, 0, 0, 0)


def mems_all_on():
    """Set all the segments to the FLAT position (0,0,0)."""
    for seg in ACTIVE_MEMS_SEGS:
        mems_seg_on(seg)
        time.sleep(0.1)


def mems_seg_off(segment):
    """Set a specific segment to the OFF position (0,3,3)."""
    m.set_pos(segment, 0, 3, 3)


def mems_all_off():
    """Set all the segments to the OFF position (0,3,3)."""
    for seg in ACTIVE_MEMS_SEGS:
        mems_seg_off(seg)
        time.sleep(0.1)


################################################################################
##################               ODL functions              ####################
################################################################################


################################################################################
##################             Global functions             ####################
################################################################################


def close(component, force_quit=False):
    """
    Close 'component' process.
    Execute close('cmd') to close this process (the command terminal).
    Execute close('print', force_quit=True) to close the print terminal.
    """
    command = "done()"
    if component == 'print':
        if force_quit:
            command = "forcequit"
        pub_print.send_multipart([component_address[component], command.encode('UTF-8')])
    elif component == 'cmd':
        publisher_comps.close()
        pub_print.close()
        context.term()
        os._exit(1)
    elif component == 'odl':
        for odl_i in range(9):
            kwargs = {"address": component_address['odl' + str(odl_i+1)],
                      "command": command}
            publisher_comps.send_pyobj(kwargs)
    else:
        kwargs = {"address": component_address[component],
                  "command": command}
        publisher_comps.send_pyobj(kwargs)


def done():
    """Close all processes."""
    for key in component_address:
        if key != 'cmd':
            close(key)
    else:
        close('cmd')


################################################################################
##################               Main process               ####################
################################################################################


"""

   Pubsub envelope publisher

   Author: Guillaume Aubert (gaubert) <guillaume(dot)aubert(at)gmail(dot)com>

"""


if __name__ == "__main__":
    ### Initialize com ###
    context = zmq.Context()
    publisher_comps = context.socket(zmq.PUB)
    publisher_comps.bind(port_PUB_comps)


    ### Initialise the andor command class ###
   # a = FirstCommand(AndorCtrl, publisher_comps, client_address_andor)


    ### Initialize the Mems command class ###
    m = FirstCommand(MemsCtrl, publisher_comps, client_address_mems)


    ### Print top messages in the terminal ###
    print("\n#####  Info  #####")
    print("a. controls the camera.")
    print("m. controls the mems.")
    print("odlX. controls the odl number X.")
    print("Type done() to close everything.")
    print("Type close('component') to just close 'component'.")
    print("Start entering commands to a component only when the 'print' terminal indicates the component is initialized.")
    print("#####  Info  #####")



    ### Initialise com with the print terminal ###
    pub_print = context.socket(zmq.PUB)
    pub_print.bind(port_PUB_print)

