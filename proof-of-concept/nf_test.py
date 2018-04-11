#########################################
# NOTCH FILTER PROJECT 					#
#										#
# Written by Timothy Wong and Tack Lee	#	
# ver1.0	Last revised: 3/13/2018 	#
#########################################

# this is a script for the driver developer to test all the basic API functions

import serial
import time
import nf_header

# initiate serial communication
nf = serial.Serial()
nf.baudrate = 38400
nf.port = 'COM32'	# depends on driver installation
nf.timeout = 3
nf.open()
if (nf.is_open): print("Serial connection established.")

running = True	# a flag to notify whether program is running

acrOp = False	# a flag to notify whether ACR operation is playing
Pause_OnOff = 0x00		# a flag to notify whether ACR is paused


while(running):
	print("")
	print("Command list: ")
	print("1:	RESET")
	print("2:	GET VERSION INFORMATION")
	print("3:	GET SYSTEM STATUS")
	print("4:	SET SYSTEM CONFIGURATION")
	print("5:	SET DEFAULT CONFIGURATION")
	print("6:	SET DIGITAL FILTER CONFIGURATION")
	print("7:	GET DIGITAL FILTER CONFIGURATION")
	print("8:	SET ACR CONFIGURATION")
	print("9:	GET ACR CONFIGURATION")
	
	# commands 10-13 are redundant for H/U testing purposes
	# print("10:	PLAY ACR OPERATION")
	# print("11:	LOOP ACR OPERATION")
	# print("12:	STOP ACR OPERATION")
	# print("13:	PAUSE ACR OPERATION")
	
	print("99:	EXIT")
	
	# prompt user to input command
	cmd = input("Input command: ")
	cmd = int(cmd)
	
	nf.reset_input_buffer()		# clear buffer before further reading

	if (cmd == 1):	# RESET
		# prepare packet as a byte array and send through COM
		packet = nf_header.reset()
		nf.write(packet)
		
		# read and print response from COM
		nf_header.reset_resp(nf)
		
	elif (cmd == 2):	# GET VERSION INFORMATION
		# prepare packet as a byte array and send through COM
		packet = nf_header.getVersion()
		nf.write(packet)
		print("Sent packet: ", packet)
		
		# read and print response from COM
		# response has 34 bytes
		nf_header.getVersion_resp(nf)
		
	elif (cmd == 3):	# GET SYSTEM STATUS
		# prepare packet as a byte array and send through COM
		packet = nf_header.getSystemStats()
		nf.write(packet)
		print("Sent packet: ", packet)
		
		# read and print response from COM
		# response has 24 bytes
		nf_header.getSystemStatus_resp(nf)
		
	elif (cmd == 4):	# SET SYSTEM CONFIGURATION
		# prepare packet as a byte array and send through COM
		packet = nf_header.setSystemConfig()
		nf.write(packet)
		print("Sent packet: ", packet)
		
		# read and print response from COM
		# response has 24 bytes
		nf_header.getSystemStatus_resp(nf)

	elif (cmd == 5):	# SET DEFAULT CONFIGURATION
		# this cmd will enable ALC_OnOff, which will turn on the Alarm LED
		# send cmd 4 to disable ALC_OnOff for normal operation
	
		# prepare packet as a byte array and send through COM
		packet = nf_header.setDefaultConfig()
		nf.write(packet)
		print("Sent packet: ", packet)
		
		# read and print response from COM
		# response has 24 bytes
		nf_header.getSystemStatus_resp(nf)	

	elif (cmd == 6):	# SET DIGITAL FILTER CONFIGURATION
		# prepare packet as a byte array and send through COM
		packet = nf_header.setFilterConfig()
		nf.write(packet)
		print("Sent packet: ", packet)
		
		# read and print response from COM
		# response has 86 bytes
		# (1+4+4+1) bytes per channel * 8 channels + 6 bytes from header, etc. 
		nf_header.getFilterConfig_resp(nf)	
		
	elif (cmd == 7):	# GET DIGITAL FILTER CONFIGURATION
		# prepare packet as a byte array and send through COM
		packet = nf_header.getFilterConfig()
		nf.write(packet)
		print("Sent packet: ", packet)
		
		# read and print response from COM
		# response has 86 bytes
		# (1+4+4+1) bytes per channel * 8 channels + 6 bytes from header, etc. 
		nf_header.getFilterConfig_resp(nf)	

	elif (cmd == 8):	# SET ACR CONFIGURATION
		# prepare packet as a byte array and send through COM
		packet = nf_header.setACRConfig()
		nf.write(packet)
		print("Sent packet: ", packet)
		
		# read and print response from COM
		# response has 687 bytes
		# each ACR line has {ACR_OnOff (1), ACR_LeadTime (4), Ch1~8 params ((1+4+4+1)*8)} -> 85 bytes
		# total bytes = 85 bytes per ACR line * 8 ACR lines + (1 byte extra) + 6 bytes from preamble, etc. = 687 bytes
		nf_header.getACRConfig_resp(nf)
		
	elif (cmd == 9):	# GET ACR CONFIGURATION
		# prepare packet as a byte array and send through COM
		packet = nf_header.getACRConfig()
		nf.write(packet)
		print("Sent packet: ", packet)
		
		# read and print response from COM
		# response has 687 bytes
		# each ACR line has {ACR_OnOff (1), ACR_LeadTime (4), Ch1~8 params ((1+4+4+1)*8)} -> 85 bytes
		# total bytes = 85 bytes per ACR line * 8 ACR lines + (1 byte extra) + 6 bytes from preamble, etc. = 687 bytes
		nf_header.getACRConfig_resp(nf)
		
	elif (cmd == 10):	# PLAY ACR OPERATION
		# prepare packet as a byte array and send through COM
		packet = nf_header.playACROp()
		nf.write(packet)
		print("Sent packet: ", packet)
		
		acrOp = True	# set the flag for periodic ACR report
		
		# read and print response from COM
		# if ACR operation is on (play, loop, pause), report is sent every second
		# response has 78 bytes 
		# ACR_LED, ACR_Loop, Pause_On, ACR_State (1 byte each), Total_ElapsedTime (4 bytes at the end) -> 8 bytes
		# ACR_LeadTime, ACR_ElapsedTime (4 bytes each) * 8 ACR lines -> (4+4)*8 = 64
		# header, etc. contributes 6 bytes
		
	elif (cmd == 11):	# LOOP ACR OPERATION
		# prepare packet as a byte array and send through COM
		packet = nf_header.loopACROp()
		nf.write(packet)
		print("Sent packet: ", packet)
		
		acrOp = True	# set the flag for periodic ACR report
		
		# read and print response from COM
		# if ACR operation is on (play, loop, pause), report is sent every second
		# response has 78 bytes 
		# ACR_LED, ACR_Loop, Pause_On, ACR_State (1 byte each), Total_ElapsedTime (4 bytes at the end) -> 8 bytes
		# ACR_LeadTime, ACR_ElapsedTime (4 bytes each) * 8 ACR lines -> (4+4)*8 = 64
		# header, etc. contributes 6 bytes
		
	elif (cmd == 12):	# STOP ACR OPERATION
		# prepare packet as a byte array and send through COM
		packet = nf_header.stopACROp()
		nf.write(packet)
		print("Sent packet: ", packet)
		
		acrOp = False	# stop the periodic ACR report
		
		# read and print response from COM
		# if ACR operation is on (play, loop, pause), report is sent every second
		# response has 78 bytes 
		# ACR_LED, ACR_Loop, Pause_On, ACR_State (1 byte each), Total_ElapsedTime (4 bytes at the end) -> 8 bytes
		# ACR_LeadTime, ACR_ElapsedTime (4 bytes each) * 8 ACR lines -> (4+4)*8 = 64
		# header, etc. contributes 6 bytes
		# does not call nf_header.ACR_report(nf)
		
	elif (cmd == 13):	# PAUSE ACR OPERATION
		# prepare packet as a byte array and send through COM
		# Pause_OnOff tells the program whether ACR Op is paused (pause + pause = play)
		# when paused, Total_ElapsedTime should stop
		packet = nf_header.playACROp(Pause_OnOff)
		nf.write(packet)
		print("Sent packet: ", packet)
		
		acrOp = True	# set the flag for periodic ACR report
		
		# read and print response from COM
		# if ACR operation is on (play, loop, pause), report is sent every second
		# response has 78 bytes 
		# ACR_LED, ACR_Loop, Pause_On, ACR_State (1 byte each), Total_ElapsedTime (4 bytes at the end) -> 8 bytes
		# ACR_LeadTime, ACR_ElapsedTime (4 bytes each) * 8 ACR lines -> (4+4)*8 = 64
		# header, etc. contributes 6 bytes
		
	elif (cmd == 99):
		running = False
		
	else: print("Invalid command.")
	
	# handle ACR operating conditions
	# when acrOp is set, give user the options to act (play, pause, loop, stop) or receive report
	# (ACR report is sent from notch filter every second whenever acrOp is set)
	while (acrOp):
		print("ACR operation in progress. ACR commands:")
		print("a: PLAY ACR OPERATION")
		print("b: PAUSE ACR OPERATION")
		print("c: LOOP ACR OPERATION")
		print("d: GET ACR STATE REPORT")
		print("e: STOP ACR OPERATION")
		acrCmd = input("Input ACR command: ")
		
		if (acrCmd == 'a'):		# play ACR operation
			packet = nf_header.playACROp()
			nf.write(packet)
			print("Sent packet: ", packet)
			
		elif (acrCmd == 'b'):	# pause ACR operation
			packet = nf_header.pauseACROp(Pause_OnOff)
			nf.write(packet)
			print("Sent packet: ", packet)
		
		elif (acrCmd == 'c'):	# loop ACR operation
			packet = nf_header.loopACROp()
			nf.write(packet)
			print("Sent packet: ", packet)
		
		elif (acrCmd == 'd'):	# get ACR state report
			# clear previously saved states, then read the most recent state
			nf.reset_input_buffer()		
			nf_header.reportACRState(nf)
		
		elif (acrCmd == 'e'):	# stop ACR operation
			packet = nf_header.stopACROp()
			nf.write(packet)
			print("Sent packet: ", packet)
			acrOp = False
		
		else: print("Invalid command. Other commands will be available after ACR operation is stopped.")
		
nf.close()
