import serial
import time
import math
import nf
import nf_header


# specify which COM port to open
com = nf.comOpen('COM32')

height = 349		# antenna height for 91.7MHz in meters
maxDist = 4120 * math.sqrt(height) 	# distance right when AA signal is completely cut off (considering Eath's curvature)
distance = maxDist + 31.3		# starting distance should be the second before vehicles reaches AA signal region
speed = 31.3		# assume vehicle speed is 70 mi/h, converted to m/s; 70mi/h === 31.3m/s
freq = 105100000	# frequency at which HD data is transmitted
wavelength = 299800000 / freq		# by v = f * lambda
endDist = 28913.2		# at the end of the test case, arriving at MTCA, which is 33829.8 m from AA signal tower

# at the end of the test case, arriving at MTCA, which is 33829.8 m from AA signal tower

duration = 3600

nf.real_fade_in_Det(com, speed, wavelength, distance, height, duration, endDist)