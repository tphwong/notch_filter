import serial
import time
import nf, nf_header

# specify which COM port to open
com = nf.comOpen('COM32')
nf.handover_const_atten_AA_Det(com, 35, 1) 
nf.comClose(com)