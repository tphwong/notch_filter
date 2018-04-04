import serial
import time
import nf, nf_header

# specify which COM port to open
com = nf.comOpen('COM32')
#nf.handover_unstable_simple_AA(com, 50, 5)	
nf.handover_unstable_simple_Det(com, 50, 5)
nf.comClose(com)