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
		packet = nf_header.setFilterConfig_handover(1, 0, 0, 0, 0, 0, 0, 0, 35-var, 0, 0, 0, 0, 0, 0, 0)
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
	packet = nf_header.setFilterConfig_handover(0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 35, 0, 0, 0)
	ser.write(packet)
	nf_header.getFilterConfig_resp(ser)
	time.sleep(45)
	print("Preconditions are set.")
	
	var = 0
	while (var  < maxAtten or var == maxAtten):
		print("+++ Input variable = ", var, " +++")
		packet = nf_header.setFilterConfig_handover(0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 35-var, 0, 0, 0)
		ser.write(packet)
		# if (var < 35 or var == 35):
			# packet = nf_header.setFilterConfig_handover(0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 35-var, 35, 35, 35)
			# ser.write(packet)
		# elif ((var > 35 and var < 70) or var == 70):
			# packet = nf_header.setFilterConfig_handover(0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 35-(var-35), 35, 35)
			# ser.write(packet)
		# elif ((var > 70 and var < 105) or var == 105):
			# packet = nf_header.setFilterConfig_handover(0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 35-(var-70), 35)
			# ser.write(packet)
		# else: 
			# packet = nf_header.setFilterConfig_handover(0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 35-(var-105))
			# ser.write(packet)
	
		nf_header.getFilterConfig_resp(ser)
		var += step
		time.sleep(3)
		
def fade_in_inst_AA(ser):
	# AA signal instantaneous fade in (from max atten to no atten instantaneously)
	print("91.7MHz instantaneous fade in...")
	
	print("Setting preconditions...")
	packet = nf_header.setFilterConfig_handover(1, 0, 0, 0, 0, 0, 0, 0, 35, 0, 0, 0, 0, 0, 0, 0)
	ser.write(packet)
	nf_header.getFilterConfig_resp(ser)
	time.sleep(45)
	print("Preconditions are set.")
	
	print("Instantaneously fade in now!")
	packet = nf_header.setFilterConfig_handover(1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
	ser.write(packet)
	
	nf_header.getFilterConfig_resp(ser)
	time.sleep(3)
	
def fade_in_inst_Det(ser):
	# Detroit signal instantaneous fade in (from max atten to no atten instantaneously)
	print("105.1MHz instantaneous fade in...")
	
	print("Setting preconditions...")
	packet = nf_header.setFilterConfig_handover(0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 35, 0, 0, 0)
	ser.write(packet)
	nf_header.getFilterConfig_resp(ser)
	time.sleep(45)
	print("Preconditions are set.")
	
	print("Instantaneously fade in now!")
	packet = nf_header.setFilterConfig_handover(0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
	ser.write(packet)
	
	nf_header.getFilterConfig_resp(ser)
	time.sleep(3)
	
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
	
	print("Setting preconditions...")
	packet = nf_header.setFilterConfig_handover(0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
	ser.write(packet)
	nf_header.getFilterConfig_resp(ser)
	time.sleep(45)
	print("Preconditions are set.")
	
	var = 0
	while (var  < maxAtten or var == maxAtten):
		print("+++ Input variable = ", var, " +++")
		packet = nf_header.setFilterConfig_handover(0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, var, 0, 0, 0)
		ser.write(packet)
		# if (var < 35 or var == 35):
			# packet = nf_header.setFilterConfig_handover(0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, var, 0, 0, 0)
			# ser.write(packet)
		# elif ((var > 35 and var < 70) or var == 70):
			# packet = nf_header.setFilterConfig_handover(0, 0, 0, 0, 1, 1, 1, 1 0, 0, 0, 0, 35, var-35, 0, 0)
			# ser.write(packet)
		# elif ((var > 70 and var < 105) or var == 105):
			# packet = nf_header.setFilterConfig_handover(0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 35, 35, var-70, 0)
			# ser.write(packet)
		# else: 
			# packet = nf_header.setFilterConfig_handover(0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 35, 35, 35, var-105)
			# ser.write(packet)
	
		nf_header.getFilterConfig_resp(ser)
		var += step
		time.sleep(1)
	
def fade_out_inst_AA(ser):
	# AA signal instantaneous fade out (from max atten to no atten instantaneously)
	print("91.7MHz instantaneous fade out...")
	
	print("Setting preconditions...")
	packet = nf_header.setFilterConfig_handover(1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
	ser.write(packet)
	nf_header.getFilterConfig_resp(ser)
	time.sleep(45)
	print("Preconditions are set.")
	
	print("Instantaneously fade out now!")
	packet = nf_header.setFilterConfig_handover(1, 0, 0, 0, 0, 0, 0, 0, 35, 0, 0, 0, 0, 0, 0, 0)
	ser.write(packet)
	
	nf_header.getFilterConfig_resp(ser)
	time.sleep(35)
	
def fade_out_inst_Det(ser):
	# Detroit signal instantaneous fade out (from max atten to no atten instantaneously)
	print("105.1MHz instantaneous fade out...")
	
	print("Setting preconditions...")
	packet = nf_header.setFilterConfig_handover(0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
	ser.write(packet)
	nf_header.getFilterConfig_resp(ser)
	time.sleep(45)
	print("Preconditions are set.")
	
	print("Instantaneously fade out now!")
	packet = nf_header.setFilterConfig_handover(0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 35, 0, 0, 0)
	ser.write(packet)
	
	nf_header.getFilterConfig_resp(ser)
	time.sleep(35)
	
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
	
	print("Setting preconditions...")
	packet = nf_header.setFilterConfig_handover(1, 0, 0, 0, 1, 0, 0, 0, 35, 0, 0, 0, 0, 0, 0, 0)
	ser.write(packet)
	nf_header.getFilterConfig_resp(ser)
	time.sleep(45)
	print("Preconditions are set.")
	
	var = 0
	while (var  < maxAtten or var == maxAtten):
		print("+++ Input variable = ", var, " +++")
		packet = nf_header.setFilterConfig_handover(1, 0, 0, 0, 1, 0, 0, 0, 35-var, 0, 0, 0, var, 0, 0, 0)
		ser.write(packet)
		# if (var < 35 or var == 35):
			# packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 1, 1, 1, 1, 35-var, 35, 35, 35, var, 0, 0, 0)
			# ser.write(packet)
		# elif ((var > 35 and var < 70) or var == 70):
			# packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 1, 1, 1, 1, 0, 35-(var-35), 35, 35, 35, var-35, 0, 0)
			# ser.write(packet)
		# elif ((var > 70 and var < 105) or var == 105):
			# packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 35-(var-70), 35, 35, 35, var-70, 0)
			# ser.write(packet)
		# else: 
			# packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 35-(var-105), 35, 35, 35, var-105)
			# ser.write(packet)
	
		nf_header.getFilterConfig_resp(ser)
		var += step
		time.sleep(3)

def handover_inst_AA_Det(ser):
	# Det signal handover to AA signal instantaneously
	print("91.7MHz fades out instantaneously; 105.1MHz fades in instantaneously...")
	
	print("Setting preconditions...")
	packet = nf_header.setFilterConfig_handover(1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 35, 0, 0, 0)
	ser.write(packet)
	nf_header.getFilterConfig_resp(ser)
	time.sleep(45)
	print("Preconditions are set.")
	
	print("Instantaneous fading now!")
	packet = nf_header.setFilterConfig_handover(1, 0, 0, 0, 1, 0, 0, 0, 35, 0, 0, 0, 0, 0, 0, 0)
	ser.write(packet)
	
	nf_header.getFilterConfig_resp(ser)
	time.sleep(45)
		
def handover_inst_Det_AA(ser):
	# Det signal handover to AA signal instantaneously
	print("105.1MHz fades out instantaneously; 91.7MHz fades in instantaneously...")
	
	print("Setting preconditions...")
	packet = nf_header.setFilterConfig_handover(1, 0, 0, 0, 1, 0, 0, 0, 35, 0, 0, 0, 0, 0, 0, 0)
	ser.write(packet)
	nf_header.getFilterConfig_resp(ser)
	time.sleep(45)
	print("Preconditions are set.")
	
	print("Instantaneous fading now!")
	packet = nf_header.setFilterConfig_handover(1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 35, 0, 0, 0)
	ser.write(packet)
	
	nf_header.getFilterConfig_resp(ser)
	time.sleep(45)

################
#				                 #
# Realistic Test Cases  #
#					             #
################
	
def real_fade_out_AA(ser, speed, wavelength, distance, duration, maxDist):
	# simulate a realistic fade-out of 91.7MHz
	# parameters (in SI units): vehicle speed, signal wavelength, distance from MTCA to radio tower, antenna height, test duration,
	#										max distance for signal cut-off (from Earth curvature)
	print("Setting preconditions...")
	packet = nf_header.setFilterConfig_handover(1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
	ser.write(packet)
	nf_header.getFilterConfig_resp(ser)
	time.sleep(45)
	print("Preconditions are set.")
	
	runningLoss = 0
	curAtten = 0
	
	for i in range(0, duration):
		distance += speed
		# if maxDist is reached, turn off signal
		if (distance > maxDist or distance == maxDist):
			print ("Time: ", i)
			print("Reached max distance.")
			packet = nf_header.setFilterConfig_handover(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
			ser.write(packet)
			nf_header.getFilterConfig_resp(ser)
			return
		
		else: 
			runningLoss += nf_header.loss(speed, wavelength, distance)
			if (runningLoss >= 1):
				runningLoss -= 1
				curAtten += 1
				print("Time: ", i, ",	Current Attenuation: ", curAtten)
				packet = nf_header.setFilterConfig_handover(1, 0, 0, 0, 0, 0, 0, 0, curAtten, 0, 0, 0, 0, 0, 0, 0)
				ser.write(packet)
				nf_header.getFilterConfig_resp(ser)
				time.sleep(1)
				
			else:
				time.sleep(1)
				
def real_fade_out_Det(ser, speed, wavelength, distance, duration, maxDist):
	# simulate a realistic fade-out of 105.1MHz
	# parameters (in SI units): vehicle speed, signal wavelength, distance from MTCA to radio tower, antenna height, test duration,
	#										max distance for signal cut-off (from Earth curvature)
	print("Setting preconditions...")
	packet = nf_header.setFilterConfig_handover(0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
	ser.write(packet)
	nf_header.getFilterConfig_resp(ser)
	time.sleep(45)
	print("Preconditions are set.")
	
	runningLoss = 0
	curAtten = 0
	
	for i in range(0, duration):
		distance += speed
		# if maxDist is reached, turn off signal
		if (distance > maxDist or distance == maxDist):
			print ("Time: ", i)
			print("Reached max distance.")
			packet = nf_header.setFilterConfig_handover(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
			ser.write(packet)
			nf_header.getFilterConfig_resp(ser)
			return
		
		else: 
			runningLoss += nf_header.loss(speed, wavelength, distance)
			if (runningLoss >= 1):
				runningLoss -= 1
				curAtten += 1
				print("Time: ", i, ",	Current Attenuation: ", curAtten)
				packet = nf_header.setFilterConfig_handover(0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, curAtten, 0, 0, 0)
				ser.write(packet)
				nf_header.getFilterConfig_resp(ser)
				time.sleep(1)
				
			else:
				time.sleep(1)
				
def real_fade_in_AA(ser, speed, wavelength, distance, duration, endDist):
	# simulate a realistic fade-out of 91.7MHz
	# parameters (in SI units): vehicle speed, signal wavelength, distance from MTCA to radio tower, antenna height, test duration,
	#										max distance for signal cut-off (from Earth curvature)
	print("Setting preconditions...")
	packet = nf_header.setFilterConfig_handover(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
	ser.write(packet)
	nf_header.getFilterConfig_resp(ser)
	time.sleep(45)
	print("Preconditions are set.")
	
	runningGain = 0
	curGain = 0
	
	for i in range(0, duration):
		distance -= speed
		# if endDist is reached, set to min attenuation
		if (distance < endDist or distance == endDist):
			print ("Time: ", i)
			print("Reached end distance.")
			packet = nf_header.setFilterConfig_handover(1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
			ser.write(packet)
			nf_header.getFilterConfig_resp(ser)
			return
		
		else: 
			runningGain += nf_header.loss(speed, wavelength, distance)
			if (runningGain >= 1):
				runningGain -= 1
				curGain += 1
				print("Time: ", i, ",	Current Gain: ", curGain)
				packet = nf_header.setFilterConfig_handover(1, 0, 0, 0, 0, 0, 0, 0, 8-curGain, 0, 0, 0, 0, 0, 0, 0)
				ser.write(packet)
				nf_header.getFilterConfig_resp(ser)
				time.sleep(1)
				
			else:
				time.sleep(1)
				
def real_fade_in_Det(ser, speed, wavelength, distance, duration, endDist):
	# simulate a realistic fade-out of 91.7MHz
	# parameters (in SI units): vehicle speed, signal wavelength, distance from MTCA to radio tower, antenna height, test duration,
	#										max distance for signal cut-off (from Earth curvature)
	print("Setting preconditions...")
	packet = nf_header.setFilterConfig_handover(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
	ser.write(packet)
	nf_header.getFilterConfig_resp(ser)
	time.sleep(45)
	print("Preconditions are set.")
	
	runningGain = 0
	curGain = 0
	
	for i in range(0, duration):
		distance -= speed
		# if endDist is reached, set to min attenuation
		if (distance < endDist or distance == endDist):
			print ("Time: ", i)
			print("Reached end distance.")
			packet = nf_header.setFilterConfig_handover(0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
			ser.write(packet)
			nf_header.getFilterConfig_resp(ser)
			return
		
		else: 
			runningGain += nf_header.loss(speed, wavelength, distance)
			if (runningGain >= 1):
				runningGain -= 1
				curGain += 1
				print("Time: ", i, ",	Current Gain: ", curGain)
				packet = nf_header.setFilterConfig_handover(0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 8-curGain, 0, 0, 0)
				ser.write(packet)
				nf_header.getFilterConfig_resp(ser)
				time.sleep(1)
				
			else:
				time.sleep(1)
		
def real_handover_AA_Det(ser, speed, wavelengthAA, distanceAA, duration, maxDistAA):
	# simulate a realistic handover from AA to Det
	# start from MTCA and move at constant speed towards Detroit
	print("Setting preconditions...")
	# at MTCA, both AA and Det signals are at atten=0
	# allow H/U to lock on to AA signal
	packet = nf_header.setFilterConfig_handover(1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
	ser.write(packet)
	nf_header.getFilterConfig_resp(ser)
	time.sleep(45)
	#introduce Det signal 
	packet = nf_header.setFilterConfig_handover(1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
	ser.write(packet)
	nf_header.getFilterConfig_resp(ser)
	print("Preconditions are set.")
	
	# keep track of signal loss of AA 
	runningLoss = 0
	curAtten = 0
	
	for i in range(0, duration):
		distanceAA += speed
		
		# handle AA signal attenuation
		# if maxDist is reached, turn off signal
		if (distanceAA > maxDistAA or distanceAA == maxDistAA):
			print ("Time: ", i)
			print("Reached max distance.")
			packet = nf_header.setFilterConfig_handover(0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
			ser.write(packet)
			nf_header.getFilterConfig_resp(ser)
			time.sleep(45)
			return
		
		else: 
			runningLoss += nf_header.loss(speed, wavelengthAA, distanceAA)
			if (runningLoss >= 1):
				runningLoss -= 1
				curAtten += 1
				print("Time: ", i, ",	Current Attenuation: ", curAtten)
				packet = nf_header.setFilterConfig_handover(1, 0, 0, 0, 1, 0, 0, 0, curAtten, 0, 0, 0, 0, 0, 0, 0)
				ser.write(packet)
				nf_header.getFilterConfig_resp(ser)
				time.sleep(1)
				
			else:
				time.sleep(1)
				
def real_handover_Det_AA(ser, speed, wavelengthDet, distanceDet, duration, maxDistDet):
	# simulate a realistic handover from AA to Det
	# start from MTCA and move at constant speed towards Detroit
	print("Setting preconditions...")
	# at MTCA, both AA and Det signals are at atten=0
	# allow H/U to lock on to Det signal
	packet = nf_header.setFilterConfig_handover(0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
	ser.write(packet)
	nf_header.getFilterConfig_resp(ser)
	time.sleep(45)
	#introduce AA signal 
	packet = nf_header.setFilterConfig_handover(1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
	ser.write(packet)
	nf_header.getFilterConfig_resp(ser)
	print("Preconditions are set.")
	
	# keep track of signal loss of Det 
	runningLoss = 0
	curAtten = 0
	
	for i in range(0, duration):
		distanceDet += speed
		
		# handle AA signal attenuation
		# if maxDist is reached, turn off signal
		if (distanceDet > maxDistDet or distanceDet == maxDistDet):
			print ("Time: ", i)
			print("Reached max distance.")
			packet = nf_header.setFilterConfig_handover(1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
			ser.write(packet)
			nf_header.getFilterConfig_resp(ser)
			time.sleep(45)
			return
		
		else: 
			runningLoss += nf_header.loss(speed, wavelengthDet, distanceDet)
			if (runningLoss >= 1):
				runningLoss -= 1
				curAtten += 1
				print("Time: ", i, ",	Current Attenuation: ", curAtten)
				packet = nf_header.setFilterConfig_handover(1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, curAtten, 0, 0, 0)
				ser.write(packet)
				nf_header.getFilterConfig_resp(ser)
				time.sleep(1)
				
			else:
				time.sleep(1)				
		