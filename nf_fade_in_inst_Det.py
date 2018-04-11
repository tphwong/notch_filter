import serial
import time
import nf, nf_header

# specify which COM port to open
com = nf.comOpen('COM32')
nf.fade_in_inst_Det(com)	
nf.comClose(com)