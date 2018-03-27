import time
import math

speed = 31.3		# assume vehicle speed is 70 mi/h, converted to m/s
freq = 91700000	# frequency at which HD data is transmitted
wavelength = 299800000 / freq		# by v = f * lambda
distance = 33829.8		# distance from Mobis to 91.7MHz radio tower in meters
height = 513		# antenna height for 91.7MHz in meters

maxDist = 4120 * math.sqrt(height)



# use loss to determine if there should be a 1-dB attenuation
def loss(speed, wavelength, distance):
	return 20 * math.log((4 * math.pi * distance / wavelength), 10) - 20 * math.log((4 * math.pi * (distance - speed) / wavelength), 10)
	
	


	

	
	
	
runningLoss = 0		# keep track of the running loss; whenever runningLoss increases by more than 1, attenuate by 1 dB
for i in range(0, 3600):
	distance += speed
	runningLoss += loss(speed, wavelength, distance)
	# print(runningLoss)
	if (runningLoss >= 1):
		runningLoss -= 1
		atten = 1
		print (i, "	", atten)
	else: atten = 0
	
	

	
# if (distance >= maxDistance):
	# signal is 0
	