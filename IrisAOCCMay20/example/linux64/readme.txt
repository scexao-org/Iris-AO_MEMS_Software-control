Authors: Clement Chalumeau (SETI Institute) & Franck Marchis (Iris AO & SETI Institute)
Date: June 17, 2016


Code example using the IrisAO_Python API

Version linux 64 bits
Tested on Anaconda2 64 bits (Python 2.7) and Linux Ubuntu 15.04
You can dowload Anaconda from  https://www.continuum.io/downloads


- Create a symbolib link named libirisao.devices.so to libirisao.devices.1.0.2.5.so 
  (found in IrisAO_PythonAPI/Library) in ${ANACONDA_SETUP_DIR}/lib  where ANACONDA_SETUP_DIR 
  is the location of anaconda, e.g   /home/username/anaconda2/
  (e.g. ln -s IrisAO_PythonAPI/Library/libirisao.devices.1.0.2.5.so ${ANACONDA_SETUP_DIR}/lib/libirisao.devices.so)
- Copy the mirror configuration file (.mcf) and driver configuration file
  (.dcf) corresponding to your mirror into the working directory
- Change the corresponding parameters in the file Example_IrisAO_PythonAPI.py
- You can enable/disable hardware by setting the variable disableHW to False/True in the
  file Example_IrisAO_PythonAPI.py

To run the example: from this folder in the cmd:
sudo python Example_IrisAO_PythonAPI.py
(root priviledges are required for the driver to work properly)

A light version of the example is provided, that only flattens the mirror
You must have the right mirror and driver configuration set before running it
To run it:
sudo python Flatten_mirror.py

