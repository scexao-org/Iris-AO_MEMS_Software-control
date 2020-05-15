Authors: Clement Chalumeau (SETI Institute) & Franck Marchis (Iris AO & SETI Institute)
Apr. 20, 2016


Code example using the IrisAO_Python API
Version windows 64 bits
Tested on Anaconda2 64 bits (Python 2.7)

BEFORE RUNNING THE EXAMPLE
- Copy the mirror configuration file (.mcf) and driver configuration file
  (.dcf) corresponding to your mirror into the working directory
- Change the corresponding parameters in the file Example_IrisAO_PythonAPI.py
- You can disable hardware by setting the variable disableHW to True in the
  file Example_IrisAO_PythonAPI.py

To run the example: from this folder in the cmd:
python Example_IrisAO_PythonAPI.py


A light version of the example is provided, that only flattens the mirror
You must have the right mirror and driver configuration set before running it
To run it:
python Flatten_mirror.py