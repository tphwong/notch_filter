#########################################
# NOTCH FILTER PROJECT 					#
#										#
# Written by Timothy Wong and Tack Lee	#	
# ver1.0	Last revised: 3/13/2018 	#
#########################################

import serial
import time
import nf, nf_header

# specify which COM port to open
com = nf.comOpen('COM32')

# issue commands

nf.reset(com)
com.reset_input_buffer()
time.sleep(4)

nf.getVersion(com)
com.reset_input_buffer()
time.sleep(4)

nf.getSystemStats(com)
com.reset_input_buffer()
time.sleep(4)

nf.setDefaultConfig(com)
com.reset_input_buffer()
time.sleep(4)

nf.setSystemConfig(com)
com.reset_input_buffer()
time.sleep(4)

nf.setFilterConfig(com)
com.reset_input_buffer()
time.sleep(4)

nf.getFilterConfig(com)
com.reset_input_buffer()
time.sleep(4)

nf.setACRConfig(com)
com.reset_input_buffer()
time.sleep(4)

nf.getACRConfig(com)
com.reset_input_buffer()
time.sleep(4)

nf.reset(com)
com.reset_input_buffer()
time.sleep(4)

# close the COM port
nf.comClose(com)