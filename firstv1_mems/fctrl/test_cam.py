
from ctypes import *
import time
from PIL import Image


cdll.LoadLibrary("/usr/local/lib/libandor.so")
dll = CDLL("/usr/local/lib/libandor.so")

## Get available cameras
c_total_cameras = c_long()
error = dll.GetAvailableCameras(byref(c_total_cameras))
total_cameras = c_total_cameras.value

print('Total cameras :'+str(total_cameras))

## Get the camera handle
c_camera_handle = c_long()
error = dll.GetCameraHandle(0, byref(c_camera_handle))
camera_handle1 = c_camera_handle.value

print('Camera handle 1 :'+str(camera_handle1))


c_camera_handle = c_long()
error = dll.GetCameraHandle(1, byref(c_camera_handle))
camera_handle2 = c_camera_handle.value

print('Camera handle 2 :'+str(camera_handle2))

## Set camera 1
error = dll.SetCurrentCamera(camera_handle1)
## Get camera 1
c_current_handle = c_long()
error = dll.GetCurrentCamera(byref(c_current_handle))
current_handle1 = c_current_handle.value
print('Current handle 1 :'+str(current_handle1))

## Initialize camera
dll.Initialize("/usr/local/etc/andor")
## Get serial number
c_number = c_int()
error = dll.GetCameraSerialNumber(byref(c_number))
camera_serialnumber1 = c_number.value
print('Current Serial Number : '+str(camera_serialnumber1))

width = c_long()
height = c_long()
dll.GetDetector(byref(width), byref(height))
print('Width :'+str(width))
print('Height :'+str(height))

## Shut down camera
dll.ShutDown()
