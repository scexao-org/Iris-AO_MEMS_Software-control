#-----------------------------------------------------------------
# File Example_IrisAO_PythonAPI.py
# 
# Clement Chalumeau (SETI Institute) & Franck Marchis (Iris AO & SETI Institute)
# Date:   Apr. 20 2016
# Modified: Jun. 6, 2016
#
# This file demonstrates the use of the Python functions available 
# in the IrisAO_PythonAPI module.
# Change the parameters to the ones corresponding to your mirror
# and driver configuration
#------------------------------------------------------------------


# CHANGE PARAMETERS HERE
mirror_num = 'PWA163-04-02-0702'
driver_num = '03160009'
nbSegments = 169  # 37 for PTT111, 169 for PTT489
disableHW = True


# Import control functions from the package
import IrisAO_PythonAPI  as IrisAO_API

import time
import sys

# Prompt configuration
print "\n****************************************************************"
print "*                IrisAO Mirror control example"
print "****************************************************************\n"
print "Current configuration:"
print "  Mirror number: ",mirror_num
print "  Driver box number: ",driver_num
print "  Number of segments: ",nbSegments

resp = raw_input("\nIs this the right combination of mirror and driver numbers? [y/n]\n")
if resp not in ['y','Y']:
	print "\nPlease change the settings in the file Example_IrisAO_PythonAPI.py"
	print "The example program is terminating\n\n"
	sys.exit()




# Initialisation file numbers
print "\n\n*** Mirror connect (",nbSegments,"segments)"


# Connect to a mirror: get a mirror handle
try:
	mirror = IrisAO_API.MirrorConnect(mirror_num,driver_num,disableHW)
except Exception as e:
	print e
	sys.exit("There was a problem connecting to the mirror, exiting")
print "Connection to the mirror: " , mirror

print "\n*** Reset all mirrors (set all segments to (0,0,0))"
try:
	IrisAO_API.MirrorCommand(mirror, IrisAO_API.MirrorInitSettings)
	print "...done"
except Exception as e:
	print e
	print "There was an error sending parameters to the mirror"

raw_input("\n Press 'enter' to continue\n\n")




# Set modal position, for one (coefficient,value) couple
print "\n*** Set modal position: one coefficient"
print "Coefficient 4 (focus) set to 0.30 um rms"
try:
	IrisAO_API.SetModalPosition(mirror, (4,0.30))
	# Send the settings to the mirror
	IrisAO_API.MirrorCommand(mirror, IrisAO_API.MirrorSendSettings)
	print "...done"
except Exception as e:
	print e
	print "There was an error sending parameters to the mirror"

try:
	print "Position of segment 1: ", IrisAO_API.GetMirrorPosition(mirror, 1)[0]
except Exception as e:
	print e
	print "There was an error reading from the mirror"


raw_input("\n Press 'enter' to continue\n\n")




print "\n*** Reset all mirrors (set all segments to (0,0,0))"
try:
	IrisAO_API.MirrorCommand(mirror, IrisAO_API.MirrorInitSettings)
	print "...done"
except Exception as e:
	print e
	print "There was an error sending parameters to the mirror"


# Set modal position, for a list of (coefficient,value) couples
print "\n*** Set modal position: two coefficients"
print "Coefficient 3 (astigmatism) set to -0.10 um rms"
print "Coefficient 4 (focus) set to +0.20 um rms"
try:
	IrisAO_API.SetModalPosition(mirror, [(3,-0.10),(4,0.20)])
	# Send the settings to the mirror
	IrisAO_API.MirrorCommand(mirror, IrisAO_API.MirrorSendSettings)
	print "...done"	
except Exception as e:
	print e
	print "There was an error sending parameters to the mirror"


# Get the position of one segment
print "\n*** Get position: one segment"
try:
	pos, locked, reachable = IrisAO_API.GetMirrorPosition(mirror, 1)
	print "Segment 1 position:  ",pos
	print "Segment 1 locked:    ",locked
	print "Segment 1 reachable: ",reachable
except Exception as e:
	print e
	print "There was an error reading from the mirror"

#Get the position of a list of segments
print "\n*** Get position: list of segments [1,2,3]"
try:
	positions,locked,reachable = IrisAO_API.GetMirrorPosition(mirror,[1,2,3])
	print "Position segment 1: ",positions[0]
	print "Position segment 2: ",positions[1]
	print "Position segment 3: ",positions[2]
	print "Segment 1 locked: ",locked[0]
	print "Segment 2 locked: ",locked[1]
	print "Segment 3 locked: ",locked[2]
	print "Segment 1 reachable: ",reachable[0]
	print "Segment 2 reachable: ",reachable[1]
	print "Segment 3 reachable: ",reachable[2]
except Exception as e:
	print e
	print "There was an error reading from the mirror"
	
	
raw_input("\n Press 'enter' to continue\n\n")


# Flatten the mirror
print "Flatten the mirror"
try:
	IrisAO_API.MirrorCommand(mirror, IrisAO_API.MirrorInitSettings)
except Exception as e:
	print e
	print "There was an error sending parameters to the mirror"
	
	
# Set the position of one segment
print "\n*** Set mirror position: one segment"
try:
	print "Segment 1 set to (0.10 um,0.11 mrad,0.12 mrad)"
	IrisAO_API.SetMirrorPosition(mirror, 1, (0.10,0.11,0.12))
	# Send the settings to the mirror
	IrisAO_API.MirrorCommand(mirror, IrisAO_API.MirrorSendSettings)
	print "...done"
	print "New position: ",IrisAO_API.GetMirrorPosition(mirror, 1)[0]
except Exception as e:
	print e
	print "There was a problem of communication with the mirror"



raw_input("\n Press 'enter' to continue\n\n")


# Set the position of a list of segments
print "\n*** Set mirror position: list of segments"
try:
	print "Segment 2 set to (0.20 um,0.21 mrad,0.22 mrad)"
	print "Segment 3 set to (0.30 um,0.31 mrad,0.32 mrad)"
	print "Segment 4 set to (0.40 um,0.41 mrad,0.42 mrad)"
	IrisAO_API.SetMirrorPosition(mirror,[2,3,4],[(0.20,0.21,0.22),(0.30,0.31,0.32),(0.40,0.41,0.42)])
	IrisAO_API.MirrorCommand(mirror, IrisAO_API.MirrorSendSettings)
	positions = IrisAO_API.GetMirrorPosition(mirror, [2,3,4])[0]
	print "...done"
	print "New position segment 2: ",positions[0]
	print "New position segment 3: ",positions[1]
	print "New position segment 4: ",positions[2]
except Exception as e:
	print e
	print "There was a problem of communication with the mirror"


raw_input("\n Press 'enter' to continue\n\n")


# Release the mirror handle
print "\n*** Mirror release"
print "successful if result==0"
try:
	print "result: ", IrisAO_API.MirrorRelease(mirror)
except Exception as e:
	print e
	print "There was a problem releasing the connection with the mirror"
