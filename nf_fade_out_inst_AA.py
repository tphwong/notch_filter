import serial
import time
import nf, nf_header

# specify which COM port to open
com = nf.comOpen('COM32')
nf.fade_out_inst_AA(com)	
nf.comClose(com)