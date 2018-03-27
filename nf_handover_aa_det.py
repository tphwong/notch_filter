import serial
import time
import math
import nf
import nf_header


# specify which COM port to open
com = nf.comOpen('COM32')

speed = 31.3		# assume vehicle speed is 70 mi/h, converted to m/s
freq = 91700000	# frequency at which HD data is transmitted
wavelength = 299800000 / freq		# by v = f * lambda
distance = 33829.8		# distance from Mobis to 91.7MHz radio tower in meters
height = 513		# antenna height for 91.7MHz in meters

maxDist = 4120 * math.sqrt(height)

runningLoss = 0		# keep track of the running loss; whenever runningLoss increases by more than 1, attenuate by 1 dB
curAtten = 0		# keep track of current attenuation

for i in range(0, 3600):
	distance += speed
	runningLoss += nf.loss(speed, wavelength, distance)
	# print(runningLoss)
	if (runningLoss >= 1):
		runningLoss -= 1
		curAtten += 1
		nf.setFilterConfig_handover(com, curAtten, curAtten, curAtten, curAtten, 0, 0, 0, 0)
		print (i, "	", curAtten)
	else: 
		nf.setFilterConfig_handover(com, curAtten, curAtten, curAtten, curAtten, 0, 0, 0, 0)
		

		
# close the COM port
nf.comClose(com)