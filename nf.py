#########################################
# NOTCH FILTER PROJECT 					#
#										#
# Written by Timothy Wong and Tack Lee	#	
# ver1.0	Last revised: 3/13/2018 	#
#########################################

import serial
import time
import math
import nf_header
import nf_atten

########################
#					   #
# Serial COM functions #
#					   #
########################

def comOpen(port):
	# initiate serial communication
	ser = serial.Serial()
	ser.baudrate = 38400
	ser.port = port	# depends on driver installation
	ser.timeout = 3
	ser.open()
	if (ser.is_open): print("Serial connection established.")
	return ser

def comClose(ser):
	ser.close()
	print("Serial connection closed.")
	
	
#####################
#					#
# Protocol commands #
#					#
#####################

def reset(ser):	# RESET
	# prepare packet as a byte array and send through COM
	packet = nf_header.reset()
	ser.write(packet)
	
	# read and print response from COM
	nf_header.reset_resp(ser)
	
def getVersion(ser):	# GET VERSION INFORMATION
	# prepare packet as a byte array and send through COM
	packet = nf_header.getVersion()
	ser.write(packet)
	print("Sent packet: ", packet)
	
	# read and print response from COM
	# response has 34 bytes
	nf_header.getVersion_resp(ser)
	
def getSystemStats(ser):	# GET SYSTEM STATUS
	# prepare packet as a byte array and send through COM
	packet = nf_header.getSystemStats()
	ser.write(packet)
	print("Sent packet: ", packet)
	
	# read and print response from COM
	# response has 24 bytes
	nf_header.getSystemStatus_resp(ser)
	
def setSystemConfig(ser):	# SET SYSTEM CONFIGURATION
	# prepare packet as a byte array and send through COM
	packet = nf_header.setSystemConfig()
	ser.write(packet)
	print("Sent packet: ", packet)
	
	# read and print response from COM
	# response has 24 bytes
	nf_header.getSystemStatus_resp(ser)

def setDefaultConfig(ser):	# SET DEFAULT CONFIGURATION
	# this cmd will enable ALC_OnOff, which will turn on the Alarm LED
	# send cmd 4 to disable ALC_OnOff for normal operation

	# prepare packet as a byte array and send through COM
	packet = nf_header.setDefaultConfig()
	ser.write(packet)
	print("Sent packet: ", packet)
	
	# read and print response from COM
	# response has 24 bytes
	nf_header.getSystemStatus_resp(ser)	

def setFilterConfig(ser):	# SET DIGITAL FILTER CONFIGURATION
	# prepare packet as a byte array and send through COM
	packet = nf_header.setFilterConfig()
	ser.write(packet)
	print("Sent packet: ", packet)
	
	# read and print response from COM
	# response has 86 bytes
	# (1+4+4+1) bytes per channel * 8 channels + 6 bytes from header, etc. 
	nf_header.getFilterConfig_resp(ser)	
	
def getFilterConfig(ser):	# GET DIGITAL FILTER CONFIGURATION
	# prepare packet as a byte array and send through COM
	packet = nf_header.getFilterConfig()
	ser.write(packet)
	print("Sent packet: ", packet)
	
	# read and print response from COM
	# response has 86 bytes
	# (1+4+4+1) bytes per channel * 8 channels + 6 bytes from header, etc. 
	nf_header.getFilterConfig_resp(ser)	
	
#-----------------------------------------------#	
# ACR Commands (not used for automated testing)	#
#-----------------------------------------------#

def setACRConfig(ser):	# SET ACR CONFIGURATION
	# prepare packet as a byte array and send through COM
	packet = nf_header.setACRConfig()
	ser.write(packet)
	print("Sent packet: ", packet)
	
	# read and print response from COM
	# response has 687 bytes
	# each ACR line has {ACR_OnOff (1), ACR_LeadTime (4), Ch1~8 params ((1+4+4+1)*8)} -> 85 bytes
	# total bytes = 85 bytes per ACR line * 8 ACR lines + (1 byte extra) + 6 bytes from preamble, etc. = 687 bytes
	nf_header.getACRConfig_resp(ser)
	
def getACRConfig(ser):	# GET ACR CONFIGURATION
	# prepare packet as a byte array and send through COM
	packet = nf_header.getACRConfig()
	ser.write(packet)
	print("Sent packet: ", packet)
	
	# read and print response from COM
	# response has 687 bytes
	# each ACR line has {ACR_OnOff (1), ACR_LeadTime (4), Ch1~8 params ((1+4+4+1)*8)} -> 85 bytes
	# total bytes = 85 bytes per ACR line * 8 ACR lines + (1 byte extra) + 6 bytes from preamble, etc. = 687 bytes
	nf_header.getACRConfig_resp(ser)
	
	
##############################################
#											 #
# Special functions (for HD data test cases) #
#											 #
##############################################

# use loss to determine if there should be a 1-dB attenuation
def loss(speed, wavelength, distance):
	return 20 * math.log((4 * math.pi * distance / wavelength), 10) - 20 * math.log((4 * math.pi * (distance - speed) / wavelength), 10)

# allows the setting of attenuation for each filter channel
def setFilterConfig_handover(ser, atten1, atten2, atten3, atten4, atten5, atten6, atten7, atten8):
	print("Setting attenuation for each filter channel...")
	packet = nf_header.setFilterConfig_handover(atten1, atten2, atten3, atten4, atten5, atten6, atten7, atten8)
	ser.write(packet)

	nf_header.getFilterConfig_resp(ser)
	







# for TC 1 - Handover: FM1 -> FM2

def handover_AA_Det(ser, step):	# handover from Ann Arbor to Detroit
	# step is the step size of each attenuation
	print("Sending command: Set digital filter configuration for HD handover test case...")
	print("Ann Arbor -> Detroit")
	while var in range(0, 31):
		print("+++ Input variable = ", var, " +++")
		packet = nf_header.setFilterConfig_handover(var, var, var, var, 30-var, 30-var, 30-var, 30-var)
		ser.write(packet)
	
		nf_header.getFilterConfig_resp(ser)
		time.sleep(3)
		var += step
		
def handover_Det_AA(ser):	# handover from Detroit to Ann Arbor
	print("Sending command: Set digital filter configuration for HD handover test case...")
	print("Detroit -> Ann Arbor")
	for var in range(0, 31):
		print("+++ Input variable = ", var, " +++")
		packet = nf_header.setFilterConfig_handover(30-var, 30-var, 30-var, 30-var, var, var, var, var)
		ser.write(packet)
	
		nf_header.getFilterConfig_resp(ser)
		time.sleep(3)

def fade_in(ser):	# fade out Ann Arbor and Detroit HD freqs -> weak signal
	print("Sending command: Set digital filter configuration for HD fading test case...")
	print("Fading out...")
	for var in range(0, 31):
		print("+++ Input variable = ", var, " +++")
		packet = nf_header.setFilterConfig_handover(30-var, 30-var, 30-var, 30-var, 30-var, 30-var, 30-var, 30-var)
		ser.write(packet)
		
		nf_header.getFilterConfig_resp(ser)
		time.sleep(3)
		
def fade_out(ser):	# fade in Ann Arbor and Detroit HD freqs -> normal signal
	print("Sending command: Set digital filter configuration for HD fading test case...")
	print("Fading in...")
	for var in range(0, 31):
		print("+++ Input variable = ", var, " +++")
		packet = nf_header.setFilterConfig_handover(var, var, var, var, var, var, var, var)
		ser.write(packet)
		
		nf_header.getFilterConfig_resp(ser)
		time.sleep(3)
		
def signal_off(ser):  # signal cut off, e.g. under a bridge
	print("Sending command: Set digital filter configuration for HD cut-off test case...")
	print("Signal cut off...")
	packet = nf_header.setFilterConfig_handover(30, 30, 30, 30, 30, 30, 30, 30)
	ser.write(packet)
	
	nf_header.getFilterConfig_resp(ser)
	time.sleep(3)
	
def signal_on(ser):  # signal resumes after cut off, e.g. coming out from under a bridge
	print("Signal resumes...")
	packet = nf_header.setFilterConfig_handover(0, 0, 0, 0, 0, 0, 0, 0)
	ser.write(packet)
	
	nf_header.getFilterConfig_resp(ser)
	time.sleep(3)