#########################################
# NOTCH FILTER PROJECT 					#
#										#
# Written by Timothy Wong and Tack Lee	#	
# ver1.0	Last revised: 3/13/2018 	#
#########################################

import serial
import time
import math

# global variables for preparing packets
PREAMBLE = 0xC0
TRAILER = 0xC0

# debug mode to toggle between sets of print statements
DEBUG_ON = False

####################
# HELPER FUNCTIONS #
####################

def fourByteMSB(num):
	# returns the most significant byte from a 4-byte input number
	num = num >> 24		# shifts 6 places to the right (24 bits)
	return num
	
def fourByte2SB(num):
	# returns the 2nd most significant byte from a 4-byte input number
	num = num & 0x00FF0000		# use a mask to filter out unwanted bytes
	num = num >> 16		# shifts 4 places to the right (16 bits)
	return num
	
def fourByte3SB(num):
	# returns the 3rd most significant byte from a 4-byte input number
	num = num & 0x0000FF00		# use a mask to filter out unwanted bytes
	num = num >> 8		# shifts 2 places to the right (8 bits)
	return num
	
def fourByteLSB(num):
	# returns the least significant byte from a 4-byte input number
	num = num & 0x000000FF		# use a mask to filter out unwanted bytes
	return num

def prepChannel(OnOff, StartFreq, StopFreq, DspAtten):
	# called in setFilterConfig(), setACRConfig()
	# set the parameters for each channel
	# OnOff: 1 byte, StartFreq: 4 bytes, StopFreq: 4 bytes, DspAtten: 1 byte
	Ch_OnOff 		= OnOff
	Ch_StartFreq 	= StartFreq
	Ch_StartFreq_a 	= fourByteMSB(StartFreq)
	Ch_StartFreq_b 	= fourByte2SB(StartFreq)
	Ch_StartFreq_c 	= fourByte3SB(StartFreq)
	Ch_StartFreq_d 	= fourByteLSB(StartFreq)
	Ch_StopFreq 	= StopFreq
	Ch_StopFreq_a 	= fourByteMSB(StopFreq)
	Ch_StopFreq_b 	= fourByte2SB(StopFreq)
	Ch_StopFreq_c 	= fourByte3SB(StopFreq)
	Ch_StopFreq_d 	= fourByteLSB(StopFreq)
	Ch_DspAtten 	= DspAtten
	
	return bytearray([Ch_OnOff, 
						Ch_StartFreq_a, Ch_StartFreq_b, Ch_StartFreq_c, Ch_StartFreq_d,
						Ch_StopFreq_a, Ch_StopFreq_b, Ch_StopFreq_c, Ch_StopFreq_d,
						Ch_DspAtten])

def filterPayload(chArray):
	# called in setFilterConfig()
	# calculates the payload by adding up all the bytes from all channels
	payload = 0
	for i in range(0, 80):
		payload += chArray[i]
	
	return payload
			
def filterPrepPacket(PREAMBLE, cmd, length_MSB, length_LSB, chArray, checksum, TRAILER):
	# called in setFilterConfig()
	# prepares the message packet to be sent by assigning all the bytes correspondingly
	packet = []
	packet.append(PREAMBLE)
	packet.append(cmd)
	packet.append(length_MSB)
	packet.append(length_LSB)
	
	for i in range(0, 80):
		packet.append(chArray[i])
	
	packet.append(checksum)
	packet.append(TRAILER)
	
	# convert packet to bytearray
	packet = bytearray(packet)
	return packet
	
def ACRPrepLine(ACR_OnOff, ACR_LeadTime, chArray):
	# each ACR line has 85 bytes 
	# ACR_OnOff: 1, ACR_LeadTime: 1, chArray: 10*8
	# create an array for a line
	line = [0] * 85
	
	line[0] = ACR_OnOff
	line[1] = fourByteMSB(ACR_LeadTime)
	line[2] = fourByte2SB(ACR_LeadTime)
	line[3] = fourByte3SB(ACR_LeadTime)
	line[4] = fourByteLSB(ACR_LeadTime)
	# assign the elements from chArray to line
	for i in range(0, 8):
		for j in range(0, 10):
			# iterate a new subarray in chArray every 10 elements -> 10*i
			# the first two elements of line are already assigned -> j+2
			line[10*i+j+5] = chArray[i][j]
			
	return bytearray(line)
	
def ACRPayload(acrArray):
	# calculate the payload by adding up all the bytes in acrArray
	payload = 0

	for i in range(0, 8):	# iterating through 8 ACR lines
		for j in range(0, 85):	# iterating through 85 bytes in each line
			payload += acrArray[i][j]
	
	return payload
			
def ACRPrepPacket(PREAMBLE, cmd, length_MSB, length_LSB, acrArray, checksum, TRAILER):
	# prepares the message packet to be sent by assigning all the bytes correspondingly
	packet = []
	packet.append(PREAMBLE)
	packet.append(cmd)
	packet.append(length_MSB)
	packet.append(length_LSB)
	
	for i in range(0, 8):	# iterating through 8 ACR lines
		for j in range(0, 85):	# iterating through 85 bytes in each line
			packet.append(acrArray[i][j])
	
	packet.append(checksum)
	packet.append(TRAILER)
	
	# convert packet to bytearray
	packet = bytearray(packet)
	return packet

def byteStuffing(packet):
	# takes a bytearray packet as input, checks for 0xC0 and 0xDB
	size = len(packet)
	i = 1	# index for loop starts at 1 to skip over preamble byte
	while (i < size-1):	# skip over trailer byte
		if (packet[i] == 0xC0):		# 0xC0 -> 0xDBDC
			packet[i] = 0xDB
			packet.insert(i+1, 0xDC)	# insert the extra byte
			size += 1	# adjust the size of the packet after inserting extra byte
			
		elif (packet[i] == 0xDB):	# 0xDB -> 0xDBDD
			packet.insert(i+1, 0xDD)	# insert the extra byte
			size += 1	# adjust the size of the packet after inserting extra byte
		
		i += 1
		
	return packet
		
def reverseByteStuffing(packet):
	# the reverse operation of byteStuffing
	# takes a bytearray packet as input, checks for 0xDBDC or 0xDBDD
	size = len(packet)		# store the size of the input packet
	i = 1	# index for loop starts at 1 to skip over preamble byte
	while (i < size-1):
		if (packet[i] == 0xDB):
			if (packet[i+1] == 0xDC):	# 0xDBDC -> 0xC0
				packet[i] = 0xC0
				packet.pop(i+1)		# remove the extra byte
				size -= 1	# adjust the size of the packet after removing extra byte
			
			elif (packet[i+1] == 0xDD):	# 0xDBDD -> 0xDB
				packet[i] = 0xDB
				packet.pop(i+1)		# remove the extra byte
				size -= 1	# adjust the size of the packet after removing extra byte
			
		i += 1
			
	return packet
			
			
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!
# add code for read error (when receiving packet and clearing buffer happen simultaneously in ACR reporting)
def readPacket(ser):
	# read packet received from serial
	packet = bytearray()
	
	packet.extend(ser.read())	# preamble
	packet.extend(ser.read())	# cmd
	# use a while loop to read the payload (length unknown), checksum
	i = 1
	
	# check if there is no response from nf
	if (len(packet) == 0):
		return False
	
	while (packet[i] != 0xC0):
		packet.extend(ser.read())
		i += 1
	
	packet = reverseByteStuffing(packet)	# remove any byte stuffing to return packet to original
	
	return packet
	
	
#####################
# PROTOCOL COMMANDS #
#####################
	
def reset():
	cmd = 0x86
	
	length = 0x0001
	length_MSB = 0x00
	length_LSB = 0x01
	# payload does not exist
	checksum = 0x100 - (cmd + length_MSB + length_LSB)
	checksum = checksum & 0x000000FF

	print("Sending command: Reset...")
	# packet = 0xC08600007AC0
	return bytearray([PREAMBLE, cmd, length_MSB, length_LSB, checksum, TRAILER])

def reset_resp(ser):
	# read and print response from serial COM
	print("=================")
	print("Response from COM")
	print("=================")
	# response = ser.readline()
	# print(response)
	# response = ser.readline()	# garbage line after reset
	# response = ser.readline()	# version number 
	# print(response)
	
	packet = bytearray()
	for i in range(0, 64):
		packet.extend(ser.read())
	print(packet)
	# response = ser.readline()
	# #print(response.decode("ascii"))
	# print(':'.join('{:02x}'.format(x) for x in response),len(response))
	# response = ser.readline()
	# print(':'.join('{:02x}'.format(x) for x in response),len(response))
	# response = ser.readline()
	# #print(response.decode("ascii"))
	# print(':'.join('{:02x}'.format(x) for x in response),len(response))
	# response = ser.readline()
	# #print(response)
	
def getVersion():
	# response packet from serial COM is 34 bytes long
	# preamble (1), header (1+2), HW version (4), FW version (4), SN (20), checksum (1), trailer (1)
	
	cmd = 0x01
	
	length = 0x0001
	length_MSB = 0x00
	length_LSB = 0x01
	# payload does not exist
	checksum = 0x100 - (cmd + length_MSB + length_LSB)
	checksum = checksum & 0x000000FF
	
	print("Sending command: Get version information...")
	# packet = 0xC0010000FFC0	
	return bytearray([PREAMBLE, cmd, length_MSB, length_LSB, checksum, TRAILER])
	
def getVersion_resp(ser):
	# read and print response from serial COM
	# response has 34 bytes
	packet = readPacket(ser)
	if (packet == False):
		print("No response from COM")
	
	else:
		preamble = packet[0]
		header = packet[1:4]
		hw_ver = packet[4:8]
		fw_ver = packet[8:12]
		sn = packet[12:32]
		checksum = packet[32]
		trailer = packet[33]
		
		print("=================")
		print("Response from COM")
		print("=================")
		
		if (DEBUG_ON):
			# preamble = ser.read()
			# print("Preamble: 	", preamble)
			# header = ser.read(3)
			# print("Header:		", header)
			# hw_ver = ser.read(4)
			# print("HW Version: 	", hw_ver)
			# fw_ver = ser.read(4)
			# print("FW Version: 	", fw_ver)
			# sn = ser.read(20)
			# print("SN: 		", sn)
			# checksum = ser.read()
			# print("Checksum: 	", checksum)
			# trailer = ser.read()
			# print("Trailer: 	", trailer)
				
			print("Preamble:	",''.join('{:02x}'.format(preamble)))
			print("Header:		",':'.join('{:02x}'.format(x) for x in header))
			print("HW Ver.:	",':'.join('{:02x}'.format(x) for x in hw_ver))
			print("FW Ver.:	",':'.join('{:02x}'.format(x) for x in fw_ver))
			print("SN:		",':'.join('{:02x}'.format(x) for x in sn))
			print("Checksum:	",''.join('{:02x}'.format(checksum)))
			print("Trailer:	",''.join('{:02x}'.format(trailer)))
			
		else:
			# print("HW Version: 	", hw_ver)
			# print("FW Version: 	", fw_ver)
			# print("SN: 		", sn)
			print("HW Ver:	","%.1f"%(int(hw_ver[2])+0.1*int(hw_ver[3])))
			print("FW Ver:	","%.1f"%(int(fw_ver[2])+0.1*int(fw_ver[3])))
			print("SN:	",sn.decode())
	
def getSystemStats():
	# response packet from COM is 24 bytes long
	
	cmd = 0x51
	
	length = 0x0001
	length_MSB = 0x00
	length_LSB = 0x01
	# payload does not exist
	checksum = 0x100 - (cmd + length_MSB + length_LSB)
	checksum = checksum & 0x000000FF
	
	print("Sending command: Get system status...")
	# packet = 0xC0510000AFC0
	return bytearray([PREAMBLE, cmd, length_MSB, length_LSB, checksum, TRAILER])
	
def getSystemStatus_resp(ser):
	# read and print response from serial COM
	# response has 24 bytes
	
	packet = readPacket(ser)
	if (packet == False):
		print("No response from COM")
		
	else: 
		preamble = packet[0]
		header = packet[1:4]
		AMP_OnOff = packet[4]
		BT_OnOff = packet[5]
		ALC_OnOff = packet[6]
		AGC_OnOff = packet[7]
		MGC_OnOff = packet[8]
		ASD_OnOff = packet[9]
		ALC_Level = packet[10]
		AGC_Level = packet[11]
		Input_Pwr = packet[12]
		Output_Pwr = packet[13]
		System_Gain = packet[14]
		ALC_Atten = packet[15]
		AGC_Atten = packet[16]
		MGC_Atten = packet[17]
		Alarm_Led = packet[18]
		ACR_Led = packet[19]
		Temperature = packet[20:22]
		checksum = packet[22]
		trailer = packet[23]
		
		print("=================")
		print("Response from COM")
		print("=================")
		
		if (DEBUG_ON):
			
			# print("Preamble: 	", packet[0])
			# print("Header:		", packet[1], packet[2], packet[3])
			# print("AMP_OnOff: 	", packet[4])
			# print("BT_OnOff: 	", packet[5])
			# print("ALC_OnOff: 	", packet[6])
			# print("AGC_OnOff: 	", packet[7])
			# print("MGC_OnOff: 	", packet[8])
			# print("ASD_OnOff: 	", packet[9])
			# print("ALC_Level:	", packet[10])
			# print("AGC_Level:	", packet[11])
			# print("Input_Pwr:	", packet[12])
			# print("Output_Pwr:	", packet[13])
			# print("System_Gain:	", packet[14])
			# print("ALC_Atten: 	", packet[15])
			# print("AGC_Atten: 	", packet[16])
			# print("MGC_Atten: 	", packet[17])
			# print("Alarm_Led:	", packet[18])
			# print("Temperature:	", packet[20], packet[21])
			# print("Checksum: 	", packet[22])
			# print("Trailer: 	", packet[23])
			
			preamble = packet[0]
			header = packet[1:4]
			AMP_OnOff = packet[4]
			BT_OnOff = packet[5]
			ALC_OnOff = packet[6]
			AGC_OnOff = packet[7]
			MGC_OnOff = packet[8]
			ASD_OnOff = packet[9]
			ALC_Level = packet[10]
			AGC_Level = packet[11]
			Input_Pwr = packet[12]
			Output_Pwr = packet[13]
			System_Gain = packet[14]
			ALC_Atten = packet[15]
			AGC_Atten = packet[16]
			MGC_Atten = packet[17]
			Alarm_Led = packet[18]
			ACR_Led = packet[19]
			Temperature = packet[20:22]
			checksum = packet[22]
			trailer = packet[23]
			
			print("Preamble: 	",''.join('{:02x}'.format(preamble)))
			print("Header:	 	",':'.join('{:02x}'.format(x) for x in header))
			print("AMP_OnOff:	",''.join('{:02x}'.format(AMP_OnOff)))
			print("BT_OnOff:	",''.join('{:02x}'.format(BT_OnOff)))
			print("ALC_OnOff:	",''.join('{:02x}'.format(ALC_OnOff)))
			print("AGC_OnOff:	",''.join('{:02x}'.format(AGC_OnOff)))
			print("MGC_OnOff:	",''.join('{:02x}'.format(MGC_OnOff)))
			print("ASD_OnOff:	",''.join('{:02x}'.format(ASD_OnOff)))
			print("ALC_Level:	",''.join('{:02x}'.format(ALC_Level)))
			print("AGC_Level:	",''.join('{:02x}'.format(AGC_Level)))
			print("Input_Pwr:	",''.join('{:02x}'.format(Input_Pwr)))
			print("Output_Pwr:	",''.join('{:02x}'.format(Output_Pwr)))
			print("System_Gain:	",''.join('{:02x}'.format(System_Gain)))
			print("ALC_Atten:	",''.join('{:02x}'.format(ALC_Atten)))
			print("AGC_Atten:	",''.join('{:02x}'.format(AGC_Atten)))
			print("MGC_Atten:	",''.join('{:02x}'.format(MGC_Atten)))
			print("Alarm_Led:	",''.join('{:02x}'.format(Alarm_Led)))
			print("ACR_Led:	",''.join('{:02x}'.format(ACR_Led)))
			print("Temperature:	",':'.join('{:02x}'.format(x) for x in Temperature))
			print("Checksum:	",''.join('{:02x}'.format(checksum)))
			print("Trailer:	",''.join('{:02x}'.format(trailer)))
			
		else:
			if (AMP_OnOff == 0x00):
				print("AMP_OnOff:	OFF")
			elif (AMP_OnOff == 0x01):
				print("AMP_OnOff:	 ON")
			if (BT_OnOff == 0x00):
				print("BT_OnOff:	OFF")
			elif (BT_OnOff == 0x01):
				print("BT_OnOff:	 ON")
			if (ALC_OnOff == 0x00):
				print("ALC_OnOff:	OFF")
			elif (ALC_OnOff == 0x01):
				print("ALC_OnOff:	 ON")
			if (AGC_OnOff == 0x00):
				print("AGC_OnOff:	OFF")
			elif (AGC_OnOff == 0x01):
				print("AGC_OnOff:	 ON")
			if (MGC_OnOff == 0x00):
				print("MGC_OnOff:	OFF")
			elif (MGC_OnOff == 0x01):
				print("MGC_OnOff:	 ON")
			if (ASD_OnOff == 0x00):
				print("ASD_OnOff:	OFF")
			elif (ASD_OnOff == 0x01):
				print("ASD_OnOff:	 ON")
			ALC_Level = -(ALC_Level&0x80)|(ALC_Level&0x7F)
			print("ALC_Level:	%5.d"%ALC_Level,"dBm")
			AGC_Level = -(AGC_Level&0x80)|(AGC_Level&0x7F)
			print("AGC_Level:	%5.d"%AGC_Level,"dBm")
			Input_Pwr = -(Input_Pwr&0x80)|(Input_Pwr&0x7F)
			print("Input_Pwr:	%5.d"%Input_Pwr,"dBm")
			print("Output_Pwr:	%5.d"%Output_Pwr,"dBm")
			print("System_Gain:	%5.d"%System_Gain,"dB")		
			ALC_Atten = ALC_Atten/2
			print("ALC_Atten:	%5.1f"%ALC_Atten,"dB")
			AGC_Atten = AGC_Atten/2
			print("AGC_Atten:	%5.1f"%AGC_Atten,"dB")
			MGC_Atten = MGC_Atten/2
			print("MGC_Atten:	%5.1f"%MGC_Atten,"dB")
			Alarm = (Alarm_Led&0b00010000)>>4
			Overpower_Led = (Alarm_Led&0b00001000)>>3
			Temp_Led = (Alarm_Led&0b00000100)>>2
			PLL_Led = (Alarm_Led&0b00000010)>>1
			PowerAmp_Led = Alarm_Led&0b00000001
			if (Alarm == 0x00):
				print("Alarm_Led:	OFF")
			elif (Alarm == 0x01):
				print("Alarm_Led:	 ON")
			if(Overpower_Led==0x00):
				print("Overpower_Led:	OFF")
			elif(Overpower_Led==0x01):
				print("Overpower_Led:	 ON")
			if(Temp_Led==0x00):
				print("Temp_Led:	OFF")
			elif(Temp_Led==0x01):
				print("Temp_Led:	 ON")
			if(PLL_Led==0x00):
				print("PLL_Led:	OFF")
			elif(PLL_Led==0x01):
				print("PLL_Led:	 ON")
			if(PowerAmp_Led==0x00):
				print("PowerAmp_Led:	OFF")
			elif(PowerAmp_Led==0x01):
				print("PowerAmp_Led:	 ON")
			ACR_Leds=ACR_Led&0b00000001
			if(ACR_Leds==0x00):
				print("ACR_Led:	OFF",ACR_Led)
			elif(ACR_Leds==0x01):
				print("ACR_Led:	 ON",ACR_Led)
			print("Temperature:	",int.from_bytes(Temperature,byteorder='big')/100,"\xb0C")
	
def setSystemConfig():
	# response packet from COM is 24 bytes long
	
	cmd = 0x52
	
	AMP_OnOff 	= 0x01
	BT_OnOff 	= 0x00
	ALC_OnOff	= 0x00
	AGC_OnOff	= 0x00
	MGC_OnOff	= 0x00
	ASD_OnOff	= 0x00
	ALC_Level	= 0xC0
	AGC_Level	= 0xDB
	ALC_Atten	= 0x00
	AGC_Atten	= 0x00
	MGC_Atten	= 0x00
	
	payload = (AMP_OnOff + BT_OnOff + ALC_OnOff + AGC_OnOff + MGC_OnOff + ASD_OnOff + 
				ALC_Level + AGC_Level + ALC_Atten + AGC_Atten + MGC_Atten)
	length = 0x000B
	length_MSB = 0x00
	length_LSB = 0x0B
	checksum = 0x100 - (cmd + length_MSB + length_LSB + payload)
	checksum = checksum & 0x000000FF
	
	print("Sending command: Set system configuration...")
	packet = bytearray([PREAMBLE, cmd, length_MSB, length_LSB, 
						AMP_OnOff, BT_OnOff, ALC_OnOff, AGC_OnOff, MGC_OnOff, ASD_OnOff, 
						ALC_Level, AGC_Level, ALC_Atten, AGC_Atten, MGC_Atten, 
						checksum, TRAILER])
	
	packet = byteStuffing(packet)	
	return packet
					
def setDefaultConfig():		
	# response packet from COM is 24 bytes long
	
	cmd = 0x53
	
	#payload does not exist
	length = 0x0001
	length_MSB = 0x00
	length_LSB = 0x01
	checksum = 0x100 - (cmd + length_MSB + length_LSB)	
	checksum = checksum & 0x000000FF
	
	print("Sending command: Set default configuration...")
	packet = bytearray([PREAMBLE, cmd, length_MSB, length_LSB, checksum, TRAILER])

	packet = byteStuffing(packet)
	return packet
	
def setFilterConfig():
	# response packet from COM is 86 bytes long
	
	cmd = 0x61
	# create a channel array to store parameters from 8 channels
	chArray = []
	# store Ch_OnOff, Ch_StartFreq, Ch_StopFreq, Ch_DspAtten for each channel as an array
	# and put the arrays into the channel array
	ch1 = prepChannel(0x01, 0x00000000, 0x00000000, 0x01)
	chArray.extend(ch1)
	ch2 = prepChannel(0x01, 0x00000000, 0x00000000, 0x02)
	chArray.extend(ch2)
	ch3 = prepChannel(0x01, 0x00000000, 0x00000000, 0x03)
	chArray.extend(ch3)
	ch4 = prepChannel(0x01, 0x00000000, 0x00000000, 0x04)
	chArray.extend(ch4)
	ch5 = prepChannel(0x01, 0x00000000, 0x00000000, 0x05)
	chArray.extend(ch5)
	ch6 = prepChannel(0x01, 0x00000000, 0x00000000, 0x06)
	chArray.extend(ch6)
	ch7 = prepChannel(0x01, 0x00000000, 0x00000000, 0x07)
	chArray.extend(ch7)
	ch8 = prepChannel(0x01, 0x00000000, 0x00000000, 0x08)
	chArray.extend(ch8)
	
	payload = filterPayload(chArray)

	length = 0x0051		# 80 bytes from channels and 1 byte from checksum
	length_MSB = 0x00
	length_LSB = 0x51
	checksum = 0x100 - (cmd + length_MSB + length_LSB + payload)
	checksum = checksum & 0x000000FF
	
	print("Sending command: Set digital filter configuration...")
	# prepares message packet
	packet = filterPrepPacket(PREAMBLE, cmd, length_MSB, length_LSB, chArray, checksum, TRAILER)	
	packet = byteStuffing(packet)
	return packet

def getFilterConfig():
	# response packet from COM is 86 bytes long
	
	cmd = 0x62
	
	length = 0x0001
	length_MSB = 0x00
	length_LSB = 0x01
	# payload does not exist
	checksum = 0x100 - (cmd + length_MSB + length_LSB)
	
	print("Sending command: Get digital filter configuration...")
	return bytearray([PREAMBLE, cmd, length_MSB, length_LSB, checksum, TRAILER])
	
def getFilterConfig_resp(ser):
	# read and print response from serial COM
	# response has 86 bytes
	
	packet = readPacket(ser)
	if (packet == False):
		print("No response from COM")
	
	else:
		print("=================")
		print("Response from COM")
		print("=================")
		
		if (DEBUG_ON):
			# print("Preamble: 	", packet[0])
			# print("Header:		", packet[1], packet[2], packet[3])
			# # display parameters from each channel
			# for i in range (0, 8):
				# print("Ch", i+1, "OnOff:	", packet[12*i+4])
				# print("Ch", i+1, "StartFreq:	", packet[12*i+5], packet[12*i+6], packet[12*i+7], packet[12*i+8])
				# print("Ch", i+1, "StopFreq:	", packet[12*i+9], packet[12*i+10], packet[12*i+11], packet[12*i+12])
				# print("Ch", i+1, "DspAtten:	", packet[12*i+13])
				# print("Ch", i+1, "Output_Pwr: ", packet[12*i+14])
				# print("Ch", i+1, "Gain:	", packet[12*i+15])
			# print("Checksum: 	", packet[100])
			# print("Trailer: 	", packet[101])
			
			preamable=packet[0]	#preamble
			header=packet[1:4]	#header
			print("Preamble:	",''.join('{:02x}'.format(preamable)))
			print("Header:		",':'.join('{:02x}'.format(x) for x in header))
				
			for i in range(0, 8):
				onoff=packet[i*12+4]
				print("ch",i+1,"on/off:	",''.join('{:02x}'.format(onoff)))
				startfreq=packet[i*12+5:i*12+9]
				print("ch",i+1,"startf:	",':'.join('{:02x}'.format(x) for x in startfreq))
				stopfreq=packet[i*12+9:i*12+13]
				print("ch",i+1,"stopf:	",':'.join('{:02x}'.format(x) for x in stopfreq))
				atten=packet[i*12+13]
				print("ch",i+1,"stten:	",''.join('{:02x}'.format(atten)))
				outpwr=packet[i*12+14]
				print("ch",i+1,"outpwr:	",''.join('{:02x}'.format(outpwr)))
				gain=packet[i*12+15]
				print("ch",i+1,"gain:	",''.join('{:02x}'.format(gain)))
				
			checksum=packet[100]
			trailer=packet[101]
			print("Checksum:	",''.join('{:02x}'.format(checksum)))
			print("Trailer:	",''.join('{:02x}'.format(trailer)))
			
			
			
		else:
			for i in range(0, 8):
				onoff=packet[i*12+4]
				if(onoff==0x00):
					print("ch",i+1,"on/off:	OFF")
				elif(onoff==0x01):
					print("ch",i+1,"on/off:	ON")
				startfreq=packet[i*12+5:i*12+9]
				startfreq=int.from_bytes(startfreq,byteorder='big')/1000000
				print("ch",i+1,"startf:	%7.2f"%startfreq,"MHz")
				stopfreq=packet[i*12+9:i*12+13]
				stopfreq=int.from_bytes(stopfreq,byteorder='big')/1000000
				print("ch",i+1,"stopf:	%7.2f"%stopfreq,"MHz")
				atten=packet[i*12+13]
				print("ch",i+1,"stten:	%7.d"%atten,"dB")
				outpwr=packet[i*12+14]
				outpwr=-(outpwr&0x80)|(outpwr&0x7F)
				print("ch",i+1,"outpwr:	%7.d"%outpwr,"dBm")
				gain=packet[i*12+15]
				gain=-(gain&0x80)|(gain&0x7F)
				print("ch",i+1,"gain:	%7.d"%gain,"dB")
	
def setACRConfig():
	# response has 662 bytes
	
	cmd = 0x71
	# create an ACR array to store parameters from 8 ACR lines (each ACR line with 8 channels)
	acrArray = []
	
	# store ACR_OnOff, ACR_LeadTime, Ch_OnOff, Ch_StartFreq, Ch_StopFreq, Ch_DspAtten 
	# for each ACR line as an array and put the arrays into the ACR array
	# prepChannel() x 8 for each ACRPrepLine() 
	ACR1_OnOff = 0x01
	ACR1_LeadTime = 0x000000FF
	# create a channel array to store parameters from 8 channels
	chArray = []
	# store Ch_OnOff, Ch_StartFreq, Ch_StopFreq, Ch_DspAtten for each channel as an array
	# and put the arrays into the channel array
	ch1 = prepChannel(0x01, 0x00000000, 0x00000000, 0x01)
	chArray.append(ch1)
	ch2 = prepChannel(0x00, 0x00000000, 0x00000000, 0x02)
	chArray.append(ch2)
	ch3 = prepChannel(0x00, 0x00000000, 0x00000000, 0x03)
	chArray.append(ch3)
	ch4 = prepChannel(0x00, 0x00000000, 0x00000000, 0x04)
	chArray.append(ch4)
	ch5 = prepChannel(0x00, 0x00000000, 0x00000000, 0x05)
	chArray.append(ch5)
	ch6 = prepChannel(0x00, 0x00000000, 0x00000000, 0x06)
	chArray.append(ch6)
	ch7 = prepChannel(0x00, 0x00000000, 0x00000000, 0x07)
	chArray.append(ch7)
	ch8 = prepChannel(0x00, 0xFFFFFFFF, 0x00000000, 0x08)
	chArray.append(ch8)
	line1 = ACRPrepLine(ACR1_OnOff, ACR1_LeadTime, chArray)
	acrArray.append(line1)
	
	ACR2_OnOff = 0x00
	ACR2_LeadTime = 0x00000000
	chArray = []
	ch1 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch1)
	ch2 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch2)
	ch3 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch3)
	ch4 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch4)
	ch5 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch5)
	ch6 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch6)
	ch7 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch7)
	ch8 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch8)
	line2 = ACRPrepLine(ACR2_OnOff, ACR2_LeadTime, chArray)
	acrArray.append(line2)
	
	ACR3_OnOff = 0x00
	ACR3_LeadTime = 0x00000000
	chArray = []
	ch1 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch1)
	ch2 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch2)
	ch3 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch3)
	ch4 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch4)
	ch5 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch5)
	ch6 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch6)
	ch7 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch7)
	ch8 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch8)
	line3 = ACRPrepLine(ACR3_OnOff, ACR3_LeadTime, chArray)
	acrArray.append(line3)
	
	ACR4_OnOff = 0x00
	ACR4_LeadTime = 0x00000000
	chArray = []
	ch1 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch1)
	ch2 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch2)
	ch3 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch3)
	ch4 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch4)
	ch5 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch5)
	ch6 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch6)
	ch7 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch7)
	ch8 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch8)
	line4 = ACRPrepLine(ACR4_OnOff, ACR4_LeadTime, chArray)
	acrArray.append(line4)
	
	ACR5_OnOff = 0x00
	ACR5_LeadTime = 0x00000000
	chArray = []
	ch1 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch1)
	ch2 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch2)
	ch3 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch3)
	ch4 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch4)
	ch5 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch5)
	ch6 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch6)
	ch7 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch7)
	ch8 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch8)
	line5 = ACRPrepLine(ACR5_OnOff, ACR5_LeadTime, chArray)
	acrArray.append(line5)
	
	ACR6_OnOff = 0x00
	ACR6_LeadTime = 0x00000000
	chArray = []
	ch1 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch1)
	ch2 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch2)
	ch3 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch3)
	ch4 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch4)
	ch5 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch5)
	ch6 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch6)
	ch7 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch7)
	ch8 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch8)
	line6 = ACRPrepLine(ACR6_OnOff, ACR6_LeadTime, chArray)
	acrArray.append(line6)
	
	ACR7_OnOff = 0x00
	ACR7_LeadTime = 0x00000000
	chArray = []
	ch1 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch1)
	ch2 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch2)
	ch3 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch3)
	ch4 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch4)
	ch5 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch5)
	ch6 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch6)
	ch7 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch7)
	ch8 = prepChannel(0x00, 0x00000000, 0x00000000, 0x00)
	chArray.append(ch8)
	line7 = ACRPrepLine(ACR7_OnOff, ACR7_LeadTime, chArray)
	acrArray.append(line7)
	
	ACR8_OnOff = 0x01
	ACR8_LeadTime = 0x00000001
	chArray = []
	ch1 = prepChannel(0x01, 0x00000000, 0x00000000, 0x01)
	chArray.append(ch1)
	ch2 = prepChannel(0x00, 0x00000000, 0x00000000, 0x02)
	chArray.append(ch2)
	ch3 = prepChannel(0x00, 0x00000000, 0x00000000, 0x03)
	chArray.append(ch3)
	ch4 = prepChannel(0x00, 0x00000000, 0x00000000, 0x04)
	chArray.append(ch4)
	ch5 = prepChannel(0x00, 0x00000000, 0x00000000, 0x05)
	chArray.append(ch5)
	ch6 = prepChannel(0x00, 0x00000000, 0x00000000, 0x06)
	chArray.append(ch6)
	ch7 = prepChannel(0x00, 0x00000000, 0x00000000, 0x07)
	chArray.append(ch7)
	ch8 = prepChannel(0x01, 0xFFFFFFFF, 0x00000000, 0x08)
	chArray.append(ch8)
	line8 = ACRPrepLine(ACR8_OnOff, ACR8_LeadTime, chArray)
	acrArray.append(line8)
	
	payload = ACRPayload(acrArray)
	
	length = 0x02A9	# 681 bytes (680 bytes from ACR lines and 1 byte from checksum)
	length_MSB = 0x02
	length_LSB = 0xA9
	checksum = 0x100 - (cmd + length_MSB + length_LSB + payload)	
	checksum = checksum & 0x000000FF
	
	print("Sending command: Set ACR configuration...")
	packet = ACRPrepPacket(PREAMBLE, cmd, length_MSB, length_LSB, acrArray, checksum, TRAILER)
	packet = byteStuffing(packet)
	return packet
	
def getACRConfig():
	# response packet from COM is 687 bytes long
	
	cmd = 0x72

	length = 0x0001
	length_MSB = 0x00
	length_LSB = 0x01
	# payload does not exist
	checksum = 0x100 - (cmd + length_MSB + length_LSB)
	
	print("Sending command: Get ACR configuration...")
	return bytearray([PREAMBLE, cmd, length_MSB, length_LSB, checksum, TRAILER])

def getACRConfig_resp(ser):
	# read and print response from serial COM
	# response has 687 bytes
	
	packet = readPacket(ser)
	if (packet == False):
		print("No response from COM")
	
	else:
		print("=================")
		print("Response from COM")
		print("=================")
		
		if (DEBUG_ON):
			# print("Preamble: 	", packet[0])
			# print("Header:		", packet[1], packet[2], packet[3])
			# # display parameters from each ACR line and channel
			# for i in range(0, 8):	
				# print("ACR", i+1, "OnOff:	", packet[85*i+4])
				# print("ACR", i+1, "LeadTime:	", packet[85*i+5], packet[85*i+6], packet[85*i+7], packet[85*i+8])
				# for j in range(0, 8):	
					# print("Ch", j+1, "OnOff:	", packet[85*i+10*j+9])
					# print("Ch", j+1, "StartFreq:	", packet[85*i+10*j+10], packet[85*i+10*j+11], packet[85*i+10*j+12], packet[85*i++10*j+13])
					# print("Ch", j+1, "StopFreq:	", packet[85*i+10*j+14], packet[85*i+10*j+15], packet[85*i+10*j+16], packet[85*i+10*j+17])
					# print("Ch", j+1, "DspAtten:	", packet[85*i+10*j+18])		
			# print("(ACRState:	",packet[684], ")")		
			# print("Checksum: 	", packet[685])
			# print("Trailer: 	", packet[686])
			
			preamable=packet[0]	#preamble
			header=packet[1:4]	#header
			print("preamble:		",''.join('{:02x}'.format(preamable)))
			print("header:			",':'.join('{:02x}'.format(x) for x in header))
			
			for i in range(0,8):
				acronoff=packet[i*85+4]
				arcleadtime=packet[i*85+5:i*85+9]
				print("ACR",i+1,"on/off:		",''.join('{:02x}'.format(acronoff)))
				print("ACR",i+1,"leadtime:		",':'.join('{:02x}'.format(x) for x in arcleadtime))
				for j in range(0,8):
					onoff=packet[i*85+j*10+9]
					print("ACR",i+1,"Ch",j+1,"on/off:	",''.join('{:02x}'.format(onoff)))
					startfreq=packet[i*85+j*10+10:i*85+j*10+14]
					print("ACR",i+1,"Ch",j+1,"startf:	",':'.join('{:02x}'.format(x) for x in startfreq))
					stopfreq=packet[i*85+j*10+14:i*85+j*10+18]
					print("ACR",i+1,"Ch",j+1,"stopf:	",':'.join('{:02x}'.format(x) for x in stopfreq))
					atten=packet[i*85+j*10+18]
					print("ACR",i+1,"Ch",j+1,"stten:	",''.join('{:02x}'.format(atten)))
			
			extra=packet[684]
			checksum=packet[685]
			trailer=packet[686]	
			print("ACRState:			",''.join('{:02x}'.format(extra)))
			print("checksum:		",''.join('{:02x}'.format(checksum)))
			print("trailer:		",''.join('{:02x}'.format(trailer)))
			
		else:
			for i in range(0,8):
				acronoff=packet[i*85+4]
				arcleadtime=packet[i*85+5:i*85+9]			
				arcleadtime=int.from_bytes(arcleadtime,byteorder='big')
				if(acronoff==0x00):
					print("ACR",i+1,": OFF","/ %d"%arcleadtime,"sec")
				elif(acronoff==0x01):
					print("ACR",i+1,":  ON"," / %d"%arcleadtime,"sec")
				print("		on/off	start freq	stop freq	attenuation")
				for j in range(0,8):
					onoff=packet[i*85+j*10+9]				
					startfreq=packet[i*85+j*10+10:i*85+j*10+14]
					startfreq=int.from_bytes(startfreq,byteorder='big')/1000000
					stopfreq=packet[i*85+j*10+14:i*85+j*10+18]
					stopfreq=int.from_bytes(stopfreq,byteorder='big')/1000000
					atten=packet[i*85+j*10+18]
					if(onoff==0x00):
						print("	Ch",j+1,":	 OFF	%7.2fMHz	%6.2fMHz	%5.ddB"%(startfreq, stopfreq, atten))
					elif(onoff==0x01):
						print("	Ch",j+1,":	  ON	%7.2fMHz	%6.2fMHz	%5.ddB"%(startfreq, stopfreq, atten))
					
			acrstate=packet[684]
			print("ACR state: ",''.join('{:02x}'.format(acrstate)))
	
def playACROp():
	cmd = 0x74
	
	length = 0x0001
	length_MSB = 0x00
	length_LSB = 0x01
	# payload does not exist
	checksum = 0x100 - (cmd + length_MSB + length_LSB)
	
	print("Sending command: Play ACR operation...")
	return bytearray([PREAMBLE, cmd, length_MSB, length_LSB, checksum, TRAILER])

def loopACROp():
	cmd = 0x75
	
	length = 0x0001
	length_MSB = 0x00
	length_LSB = 0x01
	# payload does not exist
	checksum = 0x100 - (cmd + length_MSB + length_LSB)
	
	print("Sending command: Loop ACR operation...")
	return bytearray([PREAMBLE, cmd, length_MSB, length_LSB, checksum, TRAILER])
	
def stopACROp():
	cmd = 0x76
	
	length = 0x0001
	length_MSB = 0x00
	length_LSB = 0x01
	# payload does not exist
	checksum = 0x100 - (cmd + length_MSB + length_LSB)
	
	print("Sending command: Stop ACR operation...")
	return bytearray([PREAMBLE, cmd, length_MSB, length_LSB, checksum, TRAILER])
	
def pauseACROp(Pause_OnOff):
	cmd = 0x77
	
	length = 0x0002		# 1 byte from payload and 1 byte from checksum
	length_MSB = 0x00
	length_LSB = 0x02
	payload = Pause_OnOff
	
	checksum = 0x100 - (cmd + length_MSB + length_LSB + payload)
	
	if (Pause_OnOff == 0x00): 
		print("Sending command: Pause ACR operation...")
		Pause_OnOff = 0x01
	elif (Pause_OnOff == 0x01):
		print("Sending command: Play ACR operation...")
		Pause_OnOff = 0x00
	return bytearray([PREAMBLE, cmd, length_MSB, length_LSB, payload, checksum, TRAILER])	
	
def reportACRState(ser):
	# if ACR operation is on (play, loop, pause), report is sent every second
	# response has 78 bytes
	
	packet = readPacket(ser)
	if (packet == False):
		print("No response from COM")
		
	else:
		print("=================")
		print("Response from COM")
		print("=================")
		
		if (DEBUG_ON):
			print("Preamble: 	", packet[0])
			print("Header:		", packet[1], packet[2], packet[3])
			print("ACR_LED:		", packet[4])
			print("ACR_Loop:		", packet[5])
			print("Pause_OnOff:		", packet[6])
			print("ACR_State:	", packet[7])
			# read and print ACR_LeadTime and ACR_ElapsedTime for each ACR line
			for i in range(0, 8):
				print("ACR", i+1, "LeadTime:	", packet[8*i+8], packet[8*i+9], packet[8*i+10], packet[8*i+11])
				print("ACR_ElapsedTime", i+1, "ElapsedTime:	", packet[8*i+12], packet[8*i+13], packet[8*i+14], packet[8*i+15])
			print("Total_ElapsedTime:	", packet[72], packet[73], packet[74], packet[75])
			print("Checksum: 	", packet[76])
			print("Trailer: 	", packet[77])
			
		else:
			preamble=packet[0]
			header=packet[1:4]
			acrled=packet[4]
			acrloop=packet[5]
			pauseon=packet[6]
			acrstate=packet[7]
			acr1lt=packet[8:12]
			acr1et=packet[12:16]		
			acr2lt=packet[16:20]
			acr2et=packet[20:24]
			acr3lt=packet[24:28]
			acr3et=packet[28:32]
			acr4lt=packet[32:36]
			acr4et=packet[36:40]
			acr5lt=packet[40:44]
			acr5et=packet[44:48]
			acr6lt=packet[48:52]
			acr6et=packet[52:56]
			acr7lt=packet[56:60]
			acr7et=packet[60:64]
			acr8lt=packet[64:68]
			acr8et=packet[68:72]
			totalet=packet[72:76]
			checksum=packet[76]
			trailer=packet[77]
				
			print("Preamble:	",''.join('{:02x}'.format(preamble)))
			print("Header:		",':'.join('{:02x}'.format(x) for x in header))
			
			print("ACR_LED:	",''.join('{:02x}'.format(acrled)))
			print("ACR_LOOP:	",''.join('{:02x}'.format(acrloop)))
			print("Pause_ON:	",''.join('{:02x}'.format(pauseon)))
			print("ACR_State:	",''.join('{:02x}'.format(acrstate)))
			print("ACR1LT:		",':'.join('{:02x}'.format(x) for x in acr1lt))
			print("ACR1ET:		",':'.join('{:02x}'.format(x) for x in acr1et))
			print("ACR2LT:		",':'.join('{:02x}'.format(x) for x in acr2lt))
			print("ACR2ET:		",':'.join('{:02x}'.format(x) for x in acr2et))
			print("ACR3LT:		",':'.join('{:02x}'.format(x) for x in acr3lt))
			print("ACR3ET:		",':'.join('{:02x}'.format(x) for x in acr3et))
			print("ACR4LT:		",':'.join('{:02x}'.format(x) for x in acr4lt))
			print("ACR4ET:		",':'.join('{:02x}'.format(x) for x in acr4et))
			print("ACR5LT:		",':'.join('{:02x}'.format(x) for x in acr5lt))
			print("ACR5ET:		",':'.join('{:02x}'.format(x) for x in acr5et))
			print("ACR6LT:		",':'.join('{:02x}'.format(x) for x in acr6lt))
			print("ACR6ET:		",':'.join('{:02x}'.format(x) for x in acr6et))
			print("ACR7LT:		",':'.join('{:02x}'.format(x) for x in acr7lt))
			print("ACR7ET:		",':'.join('{:02x}'.format(x) for x in acr7et))
			print("ACR8LT:		",':'.join('{:02x}'.format(x) for x in acr8lt))
			print("ACR8ET:		",':'.join('{:02x}'.format(x) for x in acr8et))
			print("TotalET:	",':'.join('{:02x}'.format(x) for x in totalet))
			
			print("Checksum:	",''.join('{:02x}'.format(checksum)))
			print("Trailer:	",''.join('{:02x}'.format(trailer)))	
			
			
##############################################
#											 #
# Special functions (for HD data test cases) #
#											 #
##############################################

def setFilterConfig_handover(atten1, atten2, atten3, atten4, atten5, atten6, atten7, atten8):
	# takes in attenuation for each channel
	# response packet from COM is 86 bytes long
	
	cmd = 0x61
	# create a channel array to store parameters from 8 channels
	chArray = []
	# store [Ch_OnOff, Ch_StartFreq, Ch_StopFreq, Ch_DspAtten] for each channel as an array
	# and put the arrays into the channel array
	# for handover test case between Ann Arbor and Detroit, 
	# only use 91.7 MHz (90.7 ~ 92.7) and 105.1 MHz (104.1 ~ 106.1)
	# all channels are used because that makes the attenuation effects on amplitude more significant
	# ch 1~4 are for 90.7 ~ 92.7 (0x0567F8E0 ~ 0x05867D60)
	# ch 5~8 are for 104.1 ~ 106.1 (0x063470A0 ~ 0x0652F520)
	ch1 = prepChannel(0x01, 0x0567F8E0, 0x05867D60, atten1)
	chArray.extend(ch1)
	ch2 = prepChannel(0x01, 0x0567F8E0, 0x05867D60, atten2)
	chArray.extend(ch2)
	ch3 = prepChannel(0x01, 0x0567F8E0, 0x05867D60, atten3)
	chArray.extend(ch3)
	ch4 = prepChannel(0x01, 0x0567F8E0, 0x05867D60, atten4)
	chArray.extend(ch4)
	ch5 = prepChannel(0x01, 0x063470A0, 0x0652F520, atten5)
	chArray.extend(ch5)
	ch6 = prepChannel(0x01, 0x063470A0, 0x0652F520, atten6)
	chArray.extend(ch6)
	ch7 = prepChannel(0x01, 0x063470A0, 0x0652F520, atten7)
	chArray.extend(ch7)
	ch8 = prepChannel(0x01, 0x063470A0, 0x0652F520, atten8)
	chArray.extend(ch8)
	
	payload = filterPayload(chArray)

	length = 0x0051		# 80 bytes from channels and 1 byte from checksum
	length_MSB = 0x00
	length_LSB = 0x51
	checksum = 0x100 - (cmd + length_MSB + length_LSB + payload)
	checksum = checksum & 0x000000FF
	
	# prepares message packet
	packet = filterPrepPacket(PREAMBLE, cmd, length_MSB, length_LSB, chArray, checksum, TRAILER)	
	packet = byteStuffing(packet)
	return packet