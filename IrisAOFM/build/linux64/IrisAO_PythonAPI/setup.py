#--------------------------------------------------------------
# File setup.py
#
# Clement Chalumeau (SETI Institute) & Franck Marchis (Iris AO & SETI Institute)
# Date:    Apr. 20, 2016
# Modified Jun. 13, 2016
#
# used by distutils to compile the python wrapper
#--------------------------------------------------------------

from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize


setup(
    name = "IrisAO_Python",
    ext_modules = cythonize([Extension("IrisAO_Python", ["IrisAO_Python.pyx"],libraries=["irisao.devices"])]),
)