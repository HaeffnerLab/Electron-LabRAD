from PyQt4 import QtGui, QtCore, uic
# from qtui.QCustomSpinBoxION import QCustomSpinBoxION
from qtui.QCustomSpinBox import QCustomSpinBox
from twisted.internet.defer import inlineCallbacks, returnValue
import sys
# sys.path.append('/home/LabRAD/common/okfpgaservers/dacserver/')
from common.okfpgaservers.dacserver.DacConfiguration import hardwareConfiguration as hc
# from DacConfiguration import hardwareConfiguration as hc
import time 
from labrad.wrappers import connectAsync
from labrad.types import Error
import labrad
import numpy as np
import os
import datetime

######################################################################
############# OTHER PARAMETERS #######################################
######################################################################
RF_amp = 4.2 #dBm
RF_freq = 1.4745 #GHz

#copy from electron_histogram_saver.ipynb notebook
wait_time = 20*1.E-6
pulse_delay_ao = 20*1.E-6 #sampling_time
pulse_width_ej = 800.E-9
pulse_delay_ej = 3*1e-6
pulse_width_ao = 400*1.E-6 + pulse_delay_ao
exp_cycles = 25e4

other_notes = "390 power: 2.5 mW, 422 power: 0.9 mW"
######################################################################

sleep_time = 240.8 #sleep_minutes*60 #s, wait time between scan points

Ey_scan = [0]#np.arange(-0.5, 0.5, 0.1)
Ex_scan = [0]#np.arange(-1, 1, 0.1)
Ez_scan = [0]#np.arange(-2, 2, 0.1)
U1_scan = [0] 
U2_scan = (np.arange(-2, -0.2, 0.1))
U3_scan = [0] 
U4_scan = [0] 
U5_scan = [0]

num_scan_pts = len(Ey_scan)*len(Ex_scan)*len(Ez_scan)*len(U1_scan)*len(U2_scan)*len(U3_scan)*len(U4_scan)*len(U5_scan)

def run_scan():

    print "duration of scan: ", num_scan_pts*sleep_time/60, " min"

    cxn = labrad.connect()
    dacserver = cxn.dac_server
    multipoles = dacserver.get_multipole_names()

    cumm = 0
    for U2 in U2_scan:
        for Ey in Ey_scan:
            for Ez in Ez_scan:
                for U1 in U1_scan:
                    for Ex in Ex_scan:
                        for U3 in U3_scan:
                            for U4 in U4_scan:
                                for U5 in U5_scan:
                                    print "scan point", cumm, "/", num_scan_pts
                                    
                                    dacserver.set_multipole_values([('U5', U5), ('U4', U4), ('U1', U1), ('U3', U3), ('U2', U2), ('Ey', Ey), ('Ex', Ex), ('Ez', Ez)]) 
                                    cumm += 1

                                    timestamp = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
                                    data_folder = '/home/electron/Documents/cryo_data/'
                                    filename = os.path.join(data_folder, timestamp+'.txt')


                                    multipole_lines = ["Ex: " +str(round(Ex,3)) + "\n","Ey: " +str(round(Ey,3)) + "\n","Ez: " +str(round(Ez,3)) + "\n","U1: " +str(round(U1,3)) + "\n","U2: " +str(round(U2,3)) + "\n","U3: " +str(round(U3,3)) + "\n","U4: " +str(round(U4,3)) + "\n","U5: " +str(round(U5,3)) + "\n"]
                                    other_params = ["RF amplitude: " +str(round(RF_amp,3))+" dBm \n", "RF frequency: " +str(round(RF_freq,4))+" GHz \n", "wait time: " + str(round(wait_time*1e6, 3)) +" us \n", "pulse delay ao: " + str(round(pulse_delay_ao*1e6,3)) +" us \n", "pulse width ej: "+str(round(pulse_width_ej*1e9,3))+" ns \n", "pulse delay ej: "+str(round(pulse_delay_ej*1e6))+" us \n","pulse width ao: "+str(round(pulse_width_ao*1e6, 3))+" us \n", "experiment cycles: "+str(round(exp_cycles,))+"\n", "other notes: " + other_notes +"\n"]
                                   
                                    f = open(filename,'w')
                                    f.writelines(multipole_lines)
                                    f.writelines(other_params)
                                    f.close()

                                    time.sleep(sleep_time)
start_time = '15:17:30'
t = 0 
while t<120:
    time.sleep(1)
    timenow = datetime.datetime.now().strftime('%H:%M:%S')
    t+=1
    print "waiting for start time:", start_time, ", time now:", timenow,t
    if timenow ==start_time:
        run_scan()
        break