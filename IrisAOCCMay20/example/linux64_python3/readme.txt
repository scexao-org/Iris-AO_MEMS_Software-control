Authors: Clement Chalumeau (SETI Institute) & Franck Marchis (Iris AO & SETI Institute)
Date: June 17, 2016
Last update: May 2, 2020


Code example using the IrisAO_Python API

Version linux 64 bits
Tested on Anaconda2 64 bits (Python 2.7), Anaconda3 64 bits
You can dowload Anaconda from  https://www.continuum.io/downloads


- Install the library IrisAO_PythonAPI following guidelines in 'IrisAO_PythonAPI/description.txt'.
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

