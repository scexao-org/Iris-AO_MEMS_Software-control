#-----------------------------------------------------------------
# File Example_IrisAO_PythonAPI.py
# 
# Clement Chalumeau (SETI Institute) & Franck Marchis (Iris AO & SETI Institute)
# Date:   Apr. 20 2016
# Modified : Jun. 6 2016
#
# This file demonstrates the use of the Python functions available 
# in the IrisAO_PythonAPI module.
# Change the parameters to the ones corresponding to your mirror
# and driver configuration
#------------------------------------------------------------------


# CHANGE PARAMETERS HERE
mirror_num = 'PWA163-05-04-0405'
driver_num = '12140002'
nbSegments = 169  # 37 for PTT111, 169 for PTT489
disableHW = True


# Import control functions from the package
import IrisAO_PythonAPI  as IrisAO_API

import time
import sys

# Prompt configuration
print "\n****************************************************************"
print "*                IrisAO Mirror control example"
print "*                     Flatten the mirror"
print "****************************************************************\n"
print "Current configuration:"
print "  Mirror number: ",mirror_num
print "  Driver box number: ",driver_num

resp = raw_input("\nIs this the right combination of mirror and driver numbers? [y/n]\n")
if resp not in ['y','Y']:
	print "\nPlease change the settings in the file Flatten_mirror.py"
	print "The example program is terminating\n\n"
	sys.exit()




# Initialisation file numbers
print "\n*** Mirror connect (",nbSegments,"segments)"


# Connect to a mirror: get a mirror handle
try:
	mirror = IrisAO_API.MirrorConnect(mirror_num,driver_num,disableHW)
except Exception as e:
	print e
	sys.exit("There was a problem connecting to the mirror")
		
print "Connection to the mirror: " , mirror

# Flatten the mirror
print "\n*** Reset all mirrors"

try:
	# Send the settings to the mirror
	IrisAO_API.MirrorCommand(mirror, IrisAO_API.MirrorInitSettings)
except Exception as e:
	print e,type(e)
	sys.exit('There was a problem sending settings to the mirror')
print "...done"

raw_input("\n Press 'enter' to terminate\n\n")



# Release the mirror handle
print "\n*** Mirror release"
try:
	print "result: ", IrisAO_API.MirrorRelease(mirror)
except Exception as e:
	print e
	sys.exit("There was a problem releasing the connection")
	
