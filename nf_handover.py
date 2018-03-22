import serial
import time
import nf, nf_header

# specify which COM port to open
com = nf.comOpen('COM32')
nf.handover_AA_Det(com)	# Ann Arbor -> Detroit
#nf.handover_Det_AA(com) # Detroit -> Ann Arbor
nf.comClose(com)