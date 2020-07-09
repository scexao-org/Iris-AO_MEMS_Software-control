#--------------------------------------------------------------
# File IrisAO_Python_MirrorControl.py
#
# Clement Chalumeau (SETI Institute) & Franck Marchis (Iris AO & SETI Institute)
# Date:    Apr. 20, 2016
# Modified: Jun. 6,2016
# 
# Python functions for IrisAO mirror control.
# Provided interfaces:
# - MirrorConnect
# - MirrorRelease
# - SetMirrorPosition
# - GetMirrorPosition
# - SetModalPosition
# - MirrorCommand (supported commands: MirrorInitSettings and MirrorSendSettings)
#--------------------------------------------------------------

from . import IrisAO_Python as IAOW





def MirrorConnect(mirror, driver, HWdisabled):
    """Function MirrorConnect
    Arguments: 
    - mirror: string that specifies the name of the mirror
        configuration file (without extension)
    - driver: string that specifies the name of the driver
        box configuration file (without extension)
    - disabled: Boolean flag to disable hardware
    Return:
       Handle to a mirror (type 'int')
    """
    try:
        return IAOW._connect(mirror.encode(),driver.encode(),HWdisabled)
    except: 
        print("ecveption here")
        raise

def MirrorRelease(mirror):
    """Function MirrorRelease
    Arguments: 
    - mirror: mirror handle (int)
    Return:
    0 when the release is successful
    """
    try:
        return IAOW._release(mirror)
    except:
        raise

def SetMirrorPosition(mirror, Segments, PTT):
    """Function SetMirrorPosition
    Arguments:
    - mirror: mirror handle (int)
    - Segments : Two possibilities: 
           1. Segment number
           2. List of segment numbers
    - PTT: Two possibilities, according to 'Segments'
           1. tuple (z, xgrad, ygrad) describing the position for the 
              segment given in 'Segments'
           2. List of tuples (z, xgrad, ygrad) (one triplet for each 
              segment in 'Segments')"""
    if isinstance(Segments, int): # Only one segment given
        try:
            IAOW._setPosition(mirror,[Segments],1,[PTT])
        except:
            raise
    else: #list of segments given
        try:
            IAOW._setPosition(mirror,Segments,len(Segments),PTT)
        except:
            raise
        
def GetMirrorPosition(mirror,Segments):
    """Function GetMirrorPosition
    Arguments:
    - mirror: mirror handle (int)
    - Segments : Two possibilities: 
           1. Segment number
           2. List of segment numbers
    Return: tuple (PTT, locked, reachable)
    - PTT: Two possibilities, according to 'Segments'
       1. If one segment given: tuple (z, xgrad, ygrad) representing
          the position of the given segment
       2. If list of segments given: list of tuples (z, xgrad,ygrad),
          one for each segment given
    - locked:
       1. If one segment given: Boolean 
       2. If list of segments given: list of Booleans, one for each segment given
    - reachable:
       1. If one segment given: Boolean
       2. If list of segments given: list of Booleans, one for each segment given
    """
    try:
        if isinstance(Segments, int): # Only one segment given
            PTT, locked, reachable = IAOW._getMirrorPosition(mirror,[Segments],1)
            return (PTT[0],locked[0],reachable[0])
        else: #list of segments given
            PTT, locked, reachable = IAOW._getMirrorPosition(mirror,Segments,len(Segments))   
            return (PTT, locked, reachable) 
    except:
        raise
  
def SetModalPosition(mirror,CoefficientValueCouples):
    """Function SetModalPosition
    Arguments:
    - mirror: mirror handle (int)
    - CoefficientValueCouples : Two possibilities: 
           1. tuple (coefficient number,value)
           2. List of tuples (coefficient number,value)
    """
    try:
        if isinstance(CoefficientValueCouples, tuple): # Only one couple given
            IAOW._setModalPosition(mirror,[CoefficientValueCouples],1)        
        else: #list of couples given
            IAOW._setModalPosition(mirror,CoefficientValueCouples,len(CoefficientValueCouples))
    except:
        raise        
   

def MirrorCommand(mirror,mirrorCommand):
    """ Function MirrorCommand
    The function provides support for dispatching 
    commands to the user supplied mirror connection.
    
    Arguments:  mirror handle (int)
                command: one of MirrorInitSettings or MirrorSendSettings
    
    
    returns void
    """
    try:
        IAOW._mirrorCommand(mirror,mirrorCommand)
    except:
        raise      
