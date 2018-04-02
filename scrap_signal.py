import serial
import time
import nf, nf_header

# specify which COM port to open
com = nf.comOpen('COM32')
nf.signal_off(com)
nf.signal_on(com)
nf.comClose(com)