import serial
import time
import nf, nf_header

# specify which COM port to open
com = nf.comOpen('COM32')
nf.handover_unstable_AA_Det(com, 140, 1, 5)	
#nf.handover_unstable_Det_AA(com, 140, 1, 5)
nf.comClose(com)