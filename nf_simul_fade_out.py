import serial
import time
import nf, nf_header

# specify which COM port to open
com = nf.comOpen('COM32')
nf.simul_fade_out(com, 140, 1)
nf.comClose(com)