import serial
import time
import nf, nf_header

# specify which COM port to open
com = nf.comOpen('COM32')
nf.handover_simple_Det_AA(com) 
nf.comClose(com)