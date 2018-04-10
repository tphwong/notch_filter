# def handover_unstable_simple_AA(ser, duration, period):
	# # AA signal is periodically toggled on/off
	# print("91.7MHz signal is unstable... toggled on/off every ", period, " seconds")
	
	# print("Setting preconditions...")
	# # first lock on to 91.7
	# packet = nf_header.setFilterConfig_handover(1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
	# ser.write(packet)
	# nf_header.getFilterConfig_resp(ser)
	# time.sleep(45)
	# # allow 105.1 while still locked on to 91.7
	# packet = nf_header.setFilterConfig_handover(1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
	# ser.write(packet)
	# nf_header.getFilterConfig_resp(ser)
	# time.sleep(3)
	# print("Preconditions are set.")
	
	# timer = 0	# keeping track of time -> toggle signal every period
	# signalOn = 1	# flag for toggling signal on/off
	# periodCnt = 0	# keep count of the number of periods passed
	
	# while (timer < duration):
		# # toggle the signalOn flag every period
		# if ((timer != 0) and (timer % period == 0)):	
			# periodCnt += 1
			# print("Period count: ", periodCnt)
			# signalOn = 1 - signalOn
			# packet = nf_header.setFilterConfig_handover(signalOn, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
			# ser.write(packet)
			# nf_header.getFilterConfig_resp(ser)
		
		# timer += 1
		# time.sleep(3)
		
# def handover_unstable_simple_Det(ser, duration, period):
	# # Detroit signal is periodically toggled on/off
	# print("105.1MHz signal is unstable... toggled on/off every ", period, " seconds")
	
	# print("Setting preconditions...")
	# # first lock on to 105.1
	# packet = nf_header.setFilterConfig_handover(0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
	# ser.write(packet)
	# nf_header.getFilterConfig_resp(ser)
	# time.sleep(45)
	# # allow 91.7 while still locked on to 105.1
	# packet = nf_header.setFilterConfig_handover(1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
	# ser.write(packet)
	# nf_header.getFilterConfig_resp(ser)
	# time.sleep(3)
	# print("Preconditions are set.")
	
	# timer = 0	# keeping track of time -> toggle signal every period
	# signalOn = 1	# flag for toggling signal on/off
	# periodCnt = 0	# keep count of the number of periods passed
	
	# while (timer < duration):
		# # toggle the signalOn flag every period
		# if ((timer != 0) and (timer % period == 0)):	
			# periodCnt += 1
			# print("Period count: ", periodCnt)
			# signalOn = 1 - signalOn
			# packet = nf_header.setFilterConfig_handover(1, 0, 0, 0, signalOn, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
			# ser.write(packet)
			# nf_header.getFilterConfig_resp(ser)
		
		# timer += 1
		# time.sleep(3)
	
# def simul_fade_in(ser, maxAtten, step):
	# # fade in AA and Detroit signals simultaneously
	# print("Simultaneous fade in... with step size ", step)
	# var = 0
	# while (var  < maxAtten or var == maxAtten):
		# print("+++ Input variable = ", var, " +++")
		# if (var < 35 or var == 35):
			# packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 1, 1, 1, 1, 35-var, 35, 35, 35, 35-var, 35, 35, 35)
			# ser.write(packet)
		# elif ((var > 35 and var < 70) or var == 70):
			# packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 1, 1, 1, 1, 0, 35-(var-35), 35, 35, 0, 35-(var-35), 35, 35)
			# ser.write(packet)
		# elif ((var > 70 and var < 105) or var == 105):
			# packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 35-(var-70), 35, 0, 0, 35-(var-70), 35)
			# ser.write(packet)
		# else: 
			# packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 35-(var-105), 0, 0, 0, 35-(var-105))
			# ser.write(packet)
	
		# nf_header.getFilterConfig_resp(ser)
		# var += step
		# time.sleep(1)
		
# def simul_fade_out(ser, maxAtten, step):
	# # fade out AA and Detroit signals simultaneously
	# print("Simultaneous fade out... with step size ", step)
	# var = 0
	# while (var  < maxAtten or var == maxAtten):
		# print("+++ Input variable = ", var, " +++")
		# if (var < 35 or var == 35):
			# packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 1, 1, 1, 1, var, 0, 0, 0, var, 0, 0, 0)
			# ser.write(packet)
		# elif ((var > 35 and var < 70) or var == 70):
			# packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 1, 1, 1, 1, 35, var-35, 0, 0, 35, var-35, 0, 0)
			# ser.write(packet)
		# elif ((var > 70 and var < 105) or var == 105):
			# packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 1, 1, 1, 1, 35, 35, var-70, 0, 35, 35, var-70, 0)
			# ser.write(packet)
		# else: 
			# packet = nf_header.setFilterConfig_handover(1, 1, 1, 1, 1, 1, 1, 1, 35, 35, 35, var-105, 35, 35, 35, var-105)
			# ser.write(packet)
	
		# nf_header.getFilterConfig_resp(ser)
		# var += step
		# time.sleep(1)
	
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
	