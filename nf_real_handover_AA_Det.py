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
distance = 33829.8		# start distance is the distance from Mobis to 91.7MHz radio tower in meters
height = 513		# antenna height for 91.7MHz in meters
duration = 3600	# duration of test case
maxDist = 4120 * math.sqrt(height)	# end distance is distance right when AA signal is completely cut off (considering Eath's curvature)

nf.real_handover_AA_Det(com, speed, wavelength, distance, duration, maxDist)