import serial
import time
import math
import nf
import nf_header


# specify which COM port to open
com = nf.comOpen('COM32')

speed = 31.3	# assume vehicle speed is 70 mi/h, converted to m/s; 70mi/h === 31.3m/s
freq = 91700000	# frequency at which HD data is transmitted
wavelength = 299800000 / freq		# by v = f * lambda
distance = 33829.8		# distance from Mobis to 91.7MHz radio tower in meters
height = 513		# antenna height for 91.7MHz in meters
duration = 3600
maxDist = 4120 * math.sqrt(height)

nf.real_fade_out_AA(com, speed, wavelength, distance, height, duration, maxDist)