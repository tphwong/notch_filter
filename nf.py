##############################
# NOTCH FILTER PROJECT 							#
#																#
# Written by Timothy Wong and Tack Lee	#	
# ver1.0	Last revised: 4/4/2018 				#
##############################

import serial
import time
import math
import nf_header

################
#					  			  #
# Serial COM functions #
#					   			  #
################

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
	
	
################
#								#
# Protocol commands #
#								#
################

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
	
#-----------------------------------------------------------#	
# ACR Commands (not used for automated testing)	#
#-----------------------------------------------------------#

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
	
	
##############################
#															    #
# Special functions (for HD data test cases)  #
#											 				    #
##############################

# use loss to determine if there should be a 1-dB attenuation
def loss(speed, wavelength, distance):
	return 20 * math.log((4 * math.pi * distance / wavelength), 10) - 20 * math.log((4 * math.pi * (distance - speed) / wavelength), 10)

# # allows the setting of attenuation for each filter channel
# def setFilterConfig_handover(ser, atten1, atten2, atten3, atten4, atten5, atten6, atten7, atten8):
	# print("Setting attenuation for each filter channel...")
	# packet = nf_header.setFilterConfig_handover(atten1, atten2, atten3, atten4, atten5, atten6, atten7, atten8)
	# ser.write(packet)

	# nf_header.getFilterConfig_resp(ser)

def signalsOff(ser):		# after signals off, radio state goes from monitoring to AF searching to band scan mode in 35 seconds
	print("All channels off...")
	packet = nf_header.setFilterConfig_handover(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
	ser.write(packet)
	nf_header.getFilterConfig_resp(ser)
	time.sleep(35)
	
def signalsOn(ser):		# after signals on, radio state goes from band scan to monitoring mode in 10 seconds
	print("All channels off...")
	packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0)
	ser.write(packet)
	nf_header.getFilterConfig_resp(ser)
	time.sleep(10)
	
def fade_in_AA(ser, maxAtten, step):
	# AA signal fade in at constant rate
	print("91.7MHz fading in... with step size ", step)
	
	print("Setting preconditions...")
	packet = nf_header.setFilterConfig_handover(1, 0, 0, 0, 0, 0, 0, 0, 35, 0, 0, 0, 0, 0, 0, 0)
	ser.write(packet)
	nf_header.getFilterConfig_resp(ser)
	time.sleep(45)
	print("Preconditions are set.")
	
	var = 0
	while (var  < maxAtten):
		print("+++ Input variable = ", var, " +++")
		packet = nf_header.setFilterConfig_handover(1, 0, 0, 0, 0, 0, 0, 0, 35-var, 35, 35, 35, 0, 0, 0, 0)
		ser.write(packet)
		# if (var < 35 or var == 35):
			# packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 0, 0, 0, 0, 35-var, 35, 35, 35, 0, 0, 0, 0)
			# ser.write(packet)
		# elif ((var > 35 and var < 70) or var == 70):
			# packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 0, 0, 0, 0, 0, 35-(var-35), 35, 35, 0, 0, 0, 0)
			# ser.write(packet)
		# elif ((var > 70 and var < 105) or var == 105):
			# packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 35-(var-70), 35, 0, 0, 0, 0)
			# ser.write(packet)
		# else: 
			# packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 35-(var-105), 0, 0, 0, 0)
			# ser.write(packet)
	
		nf_header.getFilterConfig_resp(ser)
		var += step
		time.sleep(3)
		
def fade_in_Det(ser, maxAtten, step):
	# Detroit signal fade in at constant rate
	print("105.1MHz fading in... with step size ", step)
	
	print("Setting preconditions...")
	packet = nf_header.setFilterConfig_handover(0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 35, 35, 35, 35)
	ser.write(packet)
	nf_header.getFilterConfig_resp(ser)
	time.sleep(45)
	print("Preconditions are set.")
	
	var = 0
	while (var  < maxAtten or var == maxAtten):
		print("+++ Input variable = ", var, " +++")
		if (var < 35 or var == 35):
			packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 35-var, 35, 35, 35)
			ser.write(packet)
		elif ((var > 35 and var < 70) or var == 70):
			packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 35-(var-35), 35, 35)
			ser.write(packet)
		elif ((var > 70 and var < 105) or var == 105):
			packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 35-(var-70), 35)
			ser.write(packet)
		else: 
			packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 35-(var-105))
			ser.write(packet)
	
		nf_header.getFilterConfig_resp(ser)
		var += step
		time.sleep(1)
		
def simul_fade_in(ser, maxAtten, step):
	# fade in AA and Detroit signals simultaneously
	print("Simultaneous fade in... with step size ", step)
	var = 0
	while (var  < maxAtten or var == maxAtten):
		print("+++ Input variable = ", var, " +++")
		if (var < 35 or var == 35):
			packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 1, 1, 1, 1, 35-var, 35, 35, 35, 35-var, 35, 35, 35)
			ser.write(packet)
		elif ((var > 35 and var < 70) or var == 70):
			packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 1, 1, 1, 1, 0, 35-(var-35), 35, 35, 0, 35-(var-35), 35, 35)
			ser.write(packet)
		elif ((var > 70 and var < 105) or var == 105):
			packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 35-(var-70), 35, 0, 0, 35-(var-70), 35)
			ser.write(packet)
		else: 
			packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 35-(var-105), 0, 0, 0, 35-(var-105))
			ser.write(packet)
	
		nf_header.getFilterConfig_resp(ser)
		var += step
		time.sleep(1)
		
def fade_out_AA(ser, maxAtten, step):
	# AA signal fade out at constant rate
	print("91.7MHz fading out... with step size ", step)
	
	print("Setting preconditions...")
	packet = nf_header.setFilterConfig_handover(1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
	ser.write(packet)
	nf_header.getFilterConfig_resp(ser)
	time.sleep(45)
	print("Preconditions are set.")
	
	var = 0
	while (var  < maxAtten or var == maxAtten):
		print("+++ Input variable = ", var, " +++")
		packet = nf_header.setFilterConfig_handover(1, 0, 0, 0, 0, 0, 0, 0, var, 0, 0, 0, 0, 0, 0, 0)
		ser.write(packet)
		# if (var < 35 or var == 35):
			# packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 0, 0, 0, 0, var, 0, 0, 0, 0, 0, 0, 0)
			# ser.write(packet)
		# elif ((var > 35 and var < 70) or var == 70):
			# packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 0, 0, 0, 0, 35, var-35, 0, 0, 0, 0, 0, 0)
			# ser.write(packet)
		# elif ((var > 70 and var < 105) or var == 105):
			# packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 0, 0, 0, 0, 35, 35, var-70, 0, 0, 0, 0, 0)
			# ser.write(packet)
		# else: 
			# packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 0, 0, 0, 0, 35, 35, 35, var-105, 0, 0, 0, 0)
			# ser.write(packet)
	
		nf_header.getFilterConfig_resp(ser)
		var += step
		time.sleep(3)

def fade_out_Det(ser, maxAtten, step):
	# Det signal fade out at constant rate
	print("105.1MHz fading out... with step size ", step)
	var = 0
	while (var  < maxAtten or var == maxAtten):
		print("+++ Input variable = ", var, " +++")
		if (var < 35 or var == 35):
			packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, var, 0, 0, 0)
			ser.write(packet)
		elif ((var > 35 and var < 70) or var == 70):
			packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 35, var-35, 0, 0)
			ser.write(packet)
		elif ((var > 70 and var < 105) or var == 105):
			packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 35, 35, var-70, 0)
			ser.write(packet)
		else: 
			packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 35, 35, 35, var-105)
			ser.write(packet)
	
		nf_header.getFilterConfig_resp(ser)
		var += step
		time.sleep(1)
		
def simul_fade_out(ser, maxAtten, step):
	# fade out AA and Detroit signals simultaneously
	print("Simultaneous fade out... with step size ", step)
	var = 0
	while (var  < maxAtten or var == maxAtten):
		print("+++ Input variable = ", var, " +++")
		if (var < 35 or var == 35):
			packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 1, 1, 1, 1, var, 0, 0, 0, var, 0, 0, 0)
			ser.write(packet)
		elif ((var > 35 and var < 70) or var == 70):
			packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 1, 1, 1, 1, 35, var-35, 0, 0, 35, var-35, 0, 0)
			ser.write(packet)
		elif ((var > 70 and var < 105) or var == 105):
			packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 1, 1, 1, 1, 35, 35, var-70, 0, 35, 35, var-70, 0)
			ser.write(packet)
		else: 
			packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 1, 1, 1, 1, 35, 35, 35, var-105, 35, 35, 35, var-105)
			ser.write(packet)
	
		nf_header.getFilterConfig_resp(ser)
		var += step
		time.sleep(1)
	
def handover_const_atten_AA_Det(ser, maxAtten, step):
	# AA signal fade out at constant rate; Det signal fade in at constant rate
	print("91.7MHz fading out and 105.1 fading in... with step size ", step)
	
	print("Setting preconditions...")
	packet = nf_header.setFilterConfig_handover(1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 35, 0, 0, 0)
	ser.write(packet)
	nf_header.getFilterConfig_resp(ser)
	time.sleep(45)
	print("Preconditions are set.")
	
	var = 0
	while (var  < maxAtten or var == maxAtten):
		print("+++ Input variable = ", var, " +++")
		packet = nf_header.setFilterConfig_handover(1, 0, 0, 0, 1, 0, 0, 0, var, 0, 0, 0, 35-var, 0, 0, 0)
		ser.write(packet)
		# if (var < 35 or var == 35):
			# packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 1, 1, 1, 1, var, 0, 0, 0, 35-var, 35, 35, 35)
			# ser.write(packet)
		# elif ((var > 35 and var < 70) or var == 70):
			# packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 1, 1, 1, 1, 35, var-35, 0, 0, 0, 35-(var-35), 35, 35)
			# ser.write(packet)
		# elif ((var > 70 and var < 105) or var == 105):
			# packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 1, 1, 1, 1, 35, 35, var-70, 0, 0, 0, 35-(var-70), 35)
			# ser.write(packet)
		# else: 
			# packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 1, 1, 1, 1, 35, 35, 35, var-105, 0, 0, 0, 35-(var-105))
			# ser.write(packet)
	
		nf_header.getFilterConfig_resp(ser)
		var += step
		time.sleep(3)

def handover_const_atten_Det_AA(ser, maxAtten, step):
	# AA signal fade in at constant rate; Det signal fade out at constant rate
	print("91.7MHz fading in and 105.1 fading out... with step size ", step)
	var = 0
	while (var  < maxAtten or var == maxAtten):
		print("+++ Input variable = ", var, " +++")
		if (var < 35 or var == 35):
			packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 1, 1, 1, 1, 35-var, 35, 35, 35, var, 0, 0, 0)
			ser.write(packet)
		elif ((var > 35 and var < 70) or var == 70):
			packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 1, 1, 1, 1, 0, 35-(var-35), 35, 35, 35, var-35, 0, 0)
			ser.write(packet)
		elif ((var > 70 and var < 105) or var == 105):
			packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 35-(var-70), 35, 35, 35, var-70, 0)
			ser.write(packet)
		else: 
			packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 35-(var-105), 35, 35, 35, var-105)
			ser.write(packet)
	
		nf_header.getFilterConfig_resp(ser)
		var += step
		time.sleep(1)

def handover_unstable_simple_AA(ser, duration, period):
	# AA signal is periodically toggled on/off
	print("91.7MHz signal is unstable... toggled on/off every ", period, " seconds")
	
	print("Setting preconditions...")
	# first lock on to 91.7
	packet = nf_header.setFilterConfig_handover(1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
	ser.write(packet)
	nf_header.getFilterConfig_resp(ser)
	time.sleep(45)
	# allow 105.1 while still locked on to 91.7
	packet = nf_header.setFilterConfig_handover(1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
	ser.write(packet)
	nf_header.getFilterConfig_resp(ser)
	time.sleep(3)
	print("Preconditions are set.")
	
	timer = 0	# keeping track of time -> toggle signal every period
	signalOn = 1	# flag for toggling signal on/off
	periodCnt = 0	# keep count of the number of periods passed
	
	while (timer < duration):
		# toggle the signalOn flag every period
		if ((timer != 0) and (timer % period == 0)):	
			periodCnt += 1
			print("Period count: ", periodCnt)
			signalOn = 1 - signalOn
			packet = nf_header.setFilterConfig_handover(signalOn, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
			ser.write(packet)
			nf_header.getFilterConfig_resp(ser)
		
		timer += 1
		time.sleep(3)
		
def handover_unstable_simple_Det(ser, duration, period):
	# Detroit signal is periodically toggled on/off
	print("105.1MHz signal is unstable... toggled on/off every ", period, " seconds")
	timer = 0	# keeping track of time -> toggle signal every period
	signalOn = 1	# flag for toggling signal on/off
	periodCnt = 0	# keep count of the number of periods passed
	
	# precondition: 91.7MHz and 105.1MHz without attenuation
	packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0)
	ser.write(packet)
	nf_header.getFilterConfig_resp(ser)
	time.sleep()
	
	while (timer < duration):
		# toggle the signalOn flag every period
		if ((timer != 0) and (timer % period == 0)):	
			periodCnt += 1
			print("Period count: ", periodCnt)
			signalOn = 1 - signalOn
			packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, signalOn, signalOn, signalOn, signalOn, 0, 0, 0, 0, 0, 0, 0, 0)
			ser.write(packet)
			nf_header.getFilterConfig_resp(ser)
		
		timer += 1
		time.sleep(1)
	

	
# def handover_simple_AA_Det(ser):	# handover from Ann Arbor to Detroit
	# # step is the step size of each attenuation
	# print("Sending command: Set digital filter configuration for HD handover test case...")
	# print("Ann Arbor -> Detroit")
	# for var in range(0, 35):
		# print("+++ Input variable = ", var, " +++")
		# packet = nf_header.setFilterConfig_handover(1, 0, 0, 0, 1, 0, 0, 0, var, var, var, var, 35-var, 35-var, 35-var, 35-var)
		# ser.write(packet)
	
		# nf_header.getFilterConfig_resp(ser)
		# time.sleep(3)
		# time.sleep(2)
	
	# packet = nf_header.setFilterConfig_handover(0, 0, 0, 0, 1, 0, 0, 0, var, var, var, var, 35-var, 35-var, 35-var, 35-var)
	# ser.write(packet)
	
	# nf_header.getFilterConfig_resp(ser)
		
# def handover_simple_Det_AA(ser):	# handover from Detroit to Ann Arbor
	# print("Sending command: Set digital filter configuration for HD handover test case...")
	# print("Detroit -> Ann Arbor")
	# for var in range(0, 35):
		# print("+++ Input variable = ", var, " +++")
		# packet = nf_header.setFilterConfig_handover(1, 0, 0, 0, 1, 0, 0, 0, 35-var, 35-var, 35-var, 35-var, var, var, var, var)
		# ser.write(packet)
	
		# nf_header.getFilterConfig_resp(ser)
		# time.sleep(3)
		# time.sleep(2)
	
	# packet = nf_header.setFilterConfig_handover(1, 0, 0, 0, 0, 0, 0, 0, 35-var, 35-var, 35-var, 35-var, var, var, var, var)
	# ser.write(packet)
	
	# nf_header.getFilterConfig_resp(ser)
	
# def handover_unstable_AA_Det(ser, maxAtten, step, period):
	# # AA signal fade out at constant rate; Det signal fade in at constant rate
	# # AA signal is unstable (periodically toggle on/off)
	# print("91.7MHz fading out and 105.1 fading in... with step size ", step)
	# var = 0
	# timer = 0	# keeping track of time -> toggle signal every period
	# signalOn = 1	# flag for toggling signal on/off
	
	# while (var  < maxAtten or var == maxAtten):
		# print("+++ Input variable = ", var, " +++")
		
		# # toggle the signalOn flag every period
		# if ((timer != 0) and (timer % period == 0)):	signalOn = 1- signalOn
		
		# if (var < 35 or var == 35):
			# packet = nf_header.setFilterConfig_handover(signalOn, signalOn, signalOn, signalOn, 1, 1, 1, 1, var, 0, 0, 0, 35-var, 35, 35, 35)
			# ser.write(packet)
		# elif ((var > 35 and var < 70) or var == 70):
			# packet = nf_header.setFilterConfig_handover(signalOn, signalOn, signalOn, signalOn, 1, 1, 1, 1, 35, var-35, 0, 0, 0, 35-(var-35), 35, 35)
			# ser.write(packet)
		# elif ((var > 70 and var < 105) or var == 105):
			# packet = nf_header.setFilterConfig_handover(signalOn, signalOn, signalOn, signalOn, 1, 1, 1, 1, 35, 35, var-70, 0, 0, 0, 35-(var-70), 35)
			# ser.write(packet)
		# else: 
			# packet = nf_header.setFilterConfig_handover(signalOn, signalOn, signalOn, signalOn, 1, 1, 1, 1, 35, 35, 35, var-105, 0, 0, 0, 35-(var-105))
			# ser.write(packet)
	
		# nf_header.getFilterConfig_resp(ser)
		# var += step
		# timer += 1
		# time.sleep(1)	
	
# def handover_unstable_Det_AA(ser, maxAtten, step, period):
	# # AA signal fade in at constant rate; Det signal fade in at constant rate
	# # AA signal is unstable (periodically toggle on/off)
	# print("91.7MHz fading in and 105.1 fading out... with step size ", step)
	# var = 0
	# timer = 0	# keeping track of time -> toggle signal every period
	# signalOn = 1	# flag for toggling signal on/off
	# while (var  < maxAtten or var == maxAtten):
		# print("+++ Input variable = ", var, " +++")
		
		# # toggle the signalOn flag every period
		# if ((timer != 0) and (timer % period == 0)):	signalOn = 1 - signalOn
		
		# if (var < 35 or var == 35):
			# packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, signalOn, signalOn, signalOn, signalOn, 35-var, 35, 35, 35, var, 0, 0, 0)
			# ser.write(packet)
		# elif ((var > 35 and var < 70) or var == 70):
			# packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, signalOn, signalOn, signalOn, signalOn, 0, 35-(var-35), 35, 35, 35, var-35, 0, 0)
			# ser.write(packet)
		# elif ((var > 70 and var < 105) or var == 105):
			# packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, signalOn, signalOn, signalOn, signalOn, 0, 0, 35-(var-70), 35, 35, 35, var-70, 0)
			# ser.write(packet)
		# else: 
			# packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, signalOn, signalOn, signalOn, signalOn, 0, 0, 0, 35-(var-105), 35, 35, 35, var-105)
			# ser.write(packet)
	
		# nf_header.getFilterConfig_resp(ser)
		# var += step
		# timer += 1
		# time.sleep(1)	
	
	
# def fade_in(ser):	# fade out Ann Arbor and Detroit HD freqs -> weak signal
	# print("Sending command: Set digital filter configuration for HD fading test case...")
	# print("Fading out...")
	# for var in range(0, 31):
		# print("+++ Input variable = ", var, " +++")
		# packet = nf_header.setFilterConfig_handover(30-var, 30-var, 30-var, 30-var, 30-var, 30-var, 30-var, 30-var)
		# ser.write(packet)
		
		# nf_header.getFilterConfig_resp(ser)
		# time.sleep(3)
		
# def fade_out(ser):	# fade in Ann Arbor and Detroit HD freqs -> normal signal
	# print("Sending command: Set digital filter configuration for HD fading test case...")
	# print("Fading in...")
	# for var in range(0, 31):
		# print("+++ Input variable = ", var, " +++")
		# packet = nf_header.setFilterConfig_handover(var, var, var, var, var, var, var, var)
		# ser.write(packet)
		
		# nf_header.getFilterConfig_resp(ser)
		# time.sleep(3)
		
# def signal_off(ser):  # signal cut off, e.g. under a bridge
	# print("Sending command: Set digital filter configuration for HD cut-off test case...")
	# print("Signal cut off...")
	# packet = nf_header.setFilterConfig_handover(30, 30, 30, 30, 30, 30, 30, 30)
	# ser.write(packet)
	
	# nf_header.getFilterConfig_resp(ser)
	# time.sleep(3)
	
# def signal_on(ser):  # signal resumes after cut off, e.g. coming out from under a bridge
	# print("Signal resumes...")
	# packet = nf_header.setFilterConfig_handover(0, 0, 0, 0, 0, 0, 0, 0)
	# ser.write(packet)
	
	# nf_header.getFilterConfig_resp(ser)
	# time.sleep(3)
	