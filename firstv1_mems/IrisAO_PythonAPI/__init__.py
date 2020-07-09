#--------------------------------------------------------------
# Module IrisAO_PythonAPI
#
# Clement Chalumeau (SETI Institute) & Franck Marchis (Iris AO & SETI Institute)
# Date:    Apr. 20, 2016
# Modified: Jun. 6, 2016
#
# This module provides Python functions to control IrisAO 
# segmented mirrors, as well as command definitions
#--------------------------------------------------------------

# Make all functions from IrisAO_MirrorControl available here
from .IrisAO_Python_MirrorControl import *

# Make commands available
from .IrisAO_Python import _mirrorSendSettings as MirrorSendSettings
from .IrisAO_Python import _mirrorInitSettings as MirrorInitSettings
