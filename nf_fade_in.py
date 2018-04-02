import serial
import time
import nf, nf_header

# specify which COM port to open
com = nf.comOpen('COM32')
#nf.fade_in_AA(com, 140, 1)	
nf.fade_in_Det(com, 140, 1)	
nf.comClose(com)