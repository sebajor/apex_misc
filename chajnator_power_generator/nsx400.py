#!/usr/local/bin/python2.7

#This code was made with python2.7

from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.utilities import computeCRC, computeLRC

import sys, os
import signal
import socket
import time
import logging
import struct

from common import *

###
### The NSX is a circuit breaker that let you read the values of the network
###



###
### Hyperparameters
###

##set the loglevel
log_level = 'INFO'
log_file = './log/nsx.log'#'/home/apexmon/monitoringV2/pgenTasks/log/NSX.log'

###scpi_commands for the database
scpi_FREQ="APEX:ANTENNA:TOTALPWR:FREQ"
scpi_A1  ="APEX:ANTENNA:TOTALPWR:A1"
scpi_A2  ="APEX:ANTENNA:TOTALPWR:A2"
scpi_A3  ="APEX:ANTENNA:TOTALPWR:A3"
scpi_V1  ="APEX:ANTENNA:TOTALPWR:V1"
scpi_V2  ="APEX:ANTENNA:TOTALPWR:V2"
scpi_V3  ="APEX:ANTENNA:TOTALPWR:V3"
scpi_PWRF="APEX:ANTENNA:TOTALPWR:PWRFACTOR"

###network parameters
IP_NSX = '10.0.6.67' 	# IP address of RS485 to IP Interface
PR_NSX = 10001		# Comm port (sock port)

###electrical parameters, see nsx documentation
### https://www.studiecd.dk/pdfs/all/lv434107_modbus_user_manual.pdf
FRE_NSX = 1054		# Corriente de fase
I_A_NSX = 1016		# Current A (Phase #1)
I_B_NSX = 1017		# Current B (Phase #2)
I_C_NSX = 1018		# Current C (Phase #3)
PF_NSX  = 1049		# Total Power Factor
VAB_NSX = 1000		# Phase to Phase Voltaje - 1-2
VBC_NSX = 1001		# Phase to Phase Voltaje - 2-3
VCA_NSX = 1002		# Phase to Phase Voltaje - 3-1
VAN_NSX = 1003		# Phase to Phase Voltaje - 1-N
VBN_NSX = 1004		# Phase to Phase Voltaje - 2-N
VCN_NSX = 1005		# Phase to Phase Voltaje - 3-N

#  ---- NSX Device configuration  -----
LNG_NSX = 1			    # Amount of consecutive data to be read
FCN_NSX = 0x03  		# Kind of register to be polled
ADDR_NSX = 0x01  		# NSX Modbus Address (set locally on device)

RATE = 40               # Measurement rate in seconds

###################################
###################################
###################################
def signal_handler(signal, frame):
    print("Ctrl+C pressed, making a safe exit")
    nsx.close()
    sys.exit()

def create_request(electrical_param, lng_nsx, fcn_nsx, addr_nsx):
    """
    msg_format:
    modbus_addr, function_type, register, length to read, crc
    """
    addr_msg = struct.pack('>BB', addr_nsx , fcn_nsx)
    data = struct.pack('>HH', (electrical_param - 1), lng_nsx)
    request =  addr_msg+ data
    crc = struct.pack(">H", computeCRC(request))
    request = request+crc
    return request

def request_data(sock, request, sleep=0.1):
    sock.sendall(request)
    time.sleep(sleep)
    data = sock.recv(16)
    time.sleep(sleep)
    return data

def parse_data(bin_data, index, dtype='>bbbHH'):
    """
    if im correct the message should be:
    modbus_addr, function code, lenght, data, checksum
    """
    parsed = struct.unpack(dtype, bin_data)
    return parsed[index]

##create logging folder if it doesnt exists
if(not os.path.exists(os.path.dirname(log_file))):
    os.makedirs(os.path.dirname(log_file))
    logging.info("Creating loging folder")

##create logger
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', filename=log_file, level=log_level)
logging.info("Starting NSX monitor")


#safe killing
signal.signal(signal.SIGINT, signal_handler)

##create the request messages
request_Freq = create_request(FRE_NSX, LNG_NSX, FCN_NSX, ADDR_NSX)
request_I_A = create_request(I_A_NSX, LNG_NSX, FCN_NSX, ADDR_NSX)
request_I_B = create_request(I_B_NSX, LNG_NSX, FCN_NSX, ADDR_NSX)
request_I_C = create_request(I_C_NSX, LNG_NSX, FCN_NSX, ADDR_NSX)
request_PFA = create_request(PF_NSX, LNG_NSX, FCN_NSX, ADDR_NSX)
request_VAB = create_request(VAB_NSX, LNG_NSX, FCN_NSX, ADDR_NSX)
request_VBC = create_request(VBC_NSX, LNG_NSX, FCN_NSX, ADDR_NSX)
request_VCA = create_request(VCA_NSX, LNG_NSX, FCN_NSX, ADDR_NSX)


##in this dictionary store all the parameters of the desired data to collect
info_obj = {'freq': {
            'request': request_Freq,
            'ans_format': '>bbbHH',
            'ans_index': 3,
            'scpi_cmd':scpi_FREQ,
            'ans': ""
            },
            'IA':{
            'request': request_I_A,
            'ans_format': '>bbbHH',
            'ans_index': 3,
            'scpi_cmd':scpi_A1,
            'ans': ""
                },
            'IB':{
            'request': request_I_B,
            'ans_format': '>bbbHH',
            'ans_index': 3,
            'scpi_cmd':scpi_A2,
            'ans': ""
            },
            'IC':{
            'request': request_I_C,
            'ans_format': '>bbbHH',
            'ans_index': 3,
            'scpi_cmd':scpi_A3,
            'ans': ""
            },
            'PFA':{
            'request': request_PFA,
            'ans_format': '>bbbhH',
            'ans_index': 3,
            'scpi_cmd':scpi_PWRF,
            'ans': ""
            },
            'VAB':{
            'request': request_VAB,
            'ans_format': '>bbbHH',
            'ans_index': 3,
        'scpi_cmd':scpi_V1,
            'ans': ""
            },
            'VBC':{
            'request': request_VBC,
            'ans_format': '>bbbHH',
            'ans_index': 3,
            'scpi_cmd':scpi_V2,
            'ans': ""
            },
            'VCA':{
            'request': request_VCA,
            'ans_format': '>bbbHH',
            'ans_index': 3,
            'scpi_cmd':scpi_V3,
            'ans': ""
            }
        }


if __name__ == '__main__':
    while(1):
        ##create socket
        try:
            nsx = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            nsx.settimeout(1)
            nsx.connect((IP_NSX, PR_NSX))
        except:
            logging.error("cant connect to the socket")
            continue 
        for key, items in info_obj.items():
            print(items)
            items['ans'] = ""
            try:
                nsx_response = request_data(nsx,items['request'])
                items['ans'] = nsx_response
            except:
                logging.error("error request %s: %s"%(key, sys.exc_info()[0])) 
        
        now = time.strftime('%Y-%m-%dT%H:%M:%S',time.localtime(time.time()))
        for key, items in info_obj.items():
            if(len(items['ans']) == 7):
                out = parse_data(items['ans'], items['ans_index'],items['ans_format'])
                ##add modificaiton over the frequency
                if(key=='freq'):
                    out = float(out)/10
                out = str(out)
                print("%s :%s"%(key, out))
                insertDB(items['scpi_cmd'], out, now)
        nsx.close()
        time.sleep(RATE)
