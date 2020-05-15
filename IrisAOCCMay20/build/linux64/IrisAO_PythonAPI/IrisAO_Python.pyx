# distutils: language = c++
# distutils: sources = "raisePythonException.cpp"
#--------------------------------------------------------------
# File IrisAO_Python.pyx
#
# Author :  Clement Chalumeau (SETI Institute) & Franck Marchis (Iris AO & SETI Institute)
# Date:     Apr. 20, 2016
# Modified: Jun. 6,  2016
# 
# Cython interface, to use the IrisAO.Devices library in Python
#--------------------------------------------------------------

    
# Import C++ boolean type
from libcpp cimport bool
from cpython.ref cimport PyObject

# Create a mirror handle integer type (cython does not manage 
# c++ pointer type  void*, an integer will be used instead when
# necessary).

ctypedef unsigned long MirrorHandleInt
ctypedef unsigned long MirrorCommandsInt


cdef extern from "raisePythonException.h":
    cdef void raise_python_error()


# Import useful features from IrisAO.Devices library
cdef extern from "irisao.mirrors.h":
    # import types
    ctypedef void* MirrorHandle
    ctypedef const char* SerialNumber
    ctypedef bool HardwareDisabled
    ctypedef void* MirrorCommands
    ctypedef unsigned int CoefficientNumber
    ctypedef unsigned int SegmentNumber  
    


    cdef cppclass MirrorPosition:
        float z
        float xgrad
        float ygrad
        bool  locked
        bool  reachable
        MirrorPosition() except +raise_python_error
        
        
    # Import variables
    cdef MirrorCommands MirrorSendSettings
    cdef MirrorCommands MirrorInitSettings
    
    # Import functions
    cdef MirrorHandle MirrorConnect (SerialNumber, SerialNumber, HardwareDisabled) except +raise_python_error
    cdef MirrorHandle MirrorRelease(MirrorHandle) except +raise_python_error
    cdef void SetMirrorPosition(MirrorHandle, SegmentNumber, float, float, float) except +raise_python_error
    cdef void GetMirrorPosition(MirrorHandle, SegmentNumber, MirrorPosition*) except +raise_python_error
    cdef void SetModalPosition (MirrorHandle, CoefficientNumber, float) except +raise_python_error
    cdef void MirrorCommand (MirrorHandle, MirrorCommands) except +raise_python_error

# Define constants useful for the programm
_mirrorSendSettings = <MirrorCommandsInt>MirrorSendSettings
_mirrorInitSettings = <MirrorCommandsInt>MirrorInitSettings


# Define cython functions wrapping the library functions, to make them
# available from Python  
def _connect(SerialNumber mirror, SerialNumber driver, HardwareDisabled disabled):
    try:
        return <MirrorHandleInt>MirrorConnect ( mirror,  driver,  disabled)
    except:
        raise   

def _release(MirrorHandleInt mirror):
    try:
        return <MirrorHandleInt>MirrorRelease(<MirrorHandle>mirror)
    except:
        raise

def _setPosition(MirrorHandleInt mirror,list SegmentList, int nbSegments, list PTTPositions):
    try:
        for i in range(nbSegments):
            SetMirrorPosition(<MirrorHandle>mirror,SegmentList[i],
                               PTTPositions[i][0],PTTPositions[i][1],PTTPositions[i][2])
    except:
        raise
        
def _getMirrorPosition(MirrorHandleInt mirror, list SegmentList, int nbSegments):
    cdef MirrorPosition *ptrPosition
    try:
        ptrPosition = new MirrorPosition()
        PTTPositions=[]
        LockedFlag=[]
        ReachableFlag=[]
        for i in range(nbSegments):
            GetMirrorPosition(<MirrorHandle>mirror,SegmentList[i],ptrPosition)
            PTTPositions.append((ptrPosition.z,ptrPosition.xgrad,ptrPosition.ygrad))
            LockedFlag.append(ptrPosition.locked)
            ReachableFlag.append(ptrPosition.reachable)
        return (PTTPositions,LockedFlag,ReachableFlag)
    except:
        raise
    finally:
        del ptrPosition
        

def _setModalPosition(MirrorHandleInt mirror, list CoefficientValueCouples , int nbCoefficients):
    try:  
        for i in range(nbCoefficients):
            SetModalPosition(<MirrorHandle>mirror,CoefficientValueCouples[i][0],CoefficientValueCouples[i][1])
    except:
        raise   
def _mirrorCommand(MirrorHandleInt mirror,MirrorCommandsInt cde):
    try:
        if cde == _mirrorInitSettings:
            MirrorCommand(<MirrorHandle>mirror,MirrorInitSettings)
        elif cde == _mirrorSendSettings:
            MirrorCommand(<MirrorHandle>mirror,MirrorSendSettings)
        else:
            # This will raise an exception (invalid argument exception)
            MirrorCommand(<MirrorHandle>mirror,<MirrorCommands>cde)
    except:
        raise
    


   
