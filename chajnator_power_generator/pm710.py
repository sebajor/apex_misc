#!/usr/local/bin/python2.7

##
##  This code uses python2.
##

from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.utilities import computeCRC, computeLRC

import sys, os
import signal
import socket
import time
import logging
import struct

from common import *

##set the loglevel
log_level = 'INFO'
log_file = './log/pm710.log'


###scpi_commands for the database
scpi_IA  ="APEX:POWERGEN:TOTALPWR:A1"
scpi_IB  ="APEX:POWERGEN:TOTALPWR:A2"
scpi_IC  ="APEX:POWERGEN:TOTALPWR:A3"
scpi_VAB  ="APEX:POWERGEN:TOTALPWR:V1"
scpi_VBC  ="APEX:POWERGEN:TOTALPWR:V2"
scpi_VCA  ="APEX:POWERGEN:TOTALPWR:V3"
scpi_FREQ="APEX:POWERGEN:TOTALPWR:FREQ"
scpi_PFA="APEX:POWERGEN:TOTALPWR:PWRFACTOR"
scpi_PWA="APEX:POWERGEN:TOTALPWR:PWRA"
scpi_PWB="APEX:POWERGEN:TOTALPWR:PWRB"
scpi_PWC="APEX:POWERGEN:TOTALPWR:PWRC"
scpi_PWT="APEX:POWERGEN:TOTALPWR:PWRT"

# ----- Network adapter params  -----
IP_PM710 = '10.0.6.66' 	# IP address of RS485 to IP Interface
PR_PM710 = 10002		# Comm port (sock port)


# ----- Electric Parameters. See Annex table on PM710 Doc   -----
FRE_PM710 = 4013		# Frequency
I_A_PM710 = 4020		# Current A (Phase #1)
I_B_PM710 = 4021		# Current B (Phase #2)
I_C_PM710 = 4022		# Current C (Phase #3)
PFA_PM710 = 4009		# Power Factor
VAB_PM710 = 4030		# Phase to Phase Voltaje - 1-2
VBC_PM710 = 4031		# Phase to Phase Voltaje - 2-3
VCA_PM710 = 4032		# Phase to Phase Voltaje - 3-1
VAN_PM710 = 4033		# Phase to Phase Voltaje - 1-N
VBN_PM710 = 4034		# Phase to Phase Voltaje - 2-N
VCN_PM710 = 4035		# Phase to Phase Voltaje - 3-N

PWA_PM710 = 4036
PWB_PM710 = 4037
PWC_PM710 = 4038
PWT_PM710 = 4006

#  ---- PM710 Device configuration  -----
LNG_PM710 = 1			# Amount of consecutive data to be read
FCN_PM710 = 0x04  		# Kind of register to be polled
ADDR_PM710 = 0x01  		# PM710 Modbus Address (set locally on device)

###
RATE = 90			# Measurement rate in seconds
GLITCH_FILTER_SIZE = 3

###################################
###################################
###################################


def signal_handler(signal, frame):
    print("Ctrl+C pressed, making a safe exit")
    pm710.close()
    sys.exit()

def create_request(electrical_param, lng, fcn, addr):
    """
    msg_format:
    modbus_addr, function_type, register, length to read, crc
    """
    addr_msg = struct.pack('>BB', addr , fcn)
    data = struct.pack('>HH', (electrical_param - 1), lng)
    request =  addr_msg+ data
    crc = struct.pack(">H", computeCRC(request))
    request = request+crc
    return request

def request_data(sock, request, sleep=0.1):
    sock.sendall(request)
    time.sleep(sleep)
    data = sock.recv(32)
    time.sleep(sleep)
    return data

def parse_data(bin_data, index, dtype='>bbbHH'):
    """
    if im correct the message should be:
    modbus_addr, function code, lenght, data, checksum
    """
    parsed = struct.unpack(dtype, bin_data)
    return parsed[index]


###################################
###################################
###################################


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
request_freq = create_request(FRE_PM710, LNG_PM710, FCN_PM710, ADDR_PM710)
request_IA= create_request(I_A_PM710, LNG_PM710, FCN_PM710, ADDR_PM710)
request_IB= create_request(I_B_PM710, LNG_PM710, FCN_PM710, ADDR_PM710)
request_IC= create_request(I_C_PM710, LNG_PM710, FCN_PM710, ADDR_PM710)
request_VAB= create_request(VAB_PM710, LNG_PM710, FCN_PM710, ADDR_PM710)
request_VBC= create_request(VBC_PM710, LNG_PM710, FCN_PM710, ADDR_PM710)
request_VCA= create_request(VCA_PM710, LNG_PM710, FCN_PM710, ADDR_PM710)
request_PFA= create_request(PFA_PM710, LNG_PM710, FCN_PM710, ADDR_PM710)
request_PWA= create_request(PWA_PM710, LNG_PM710, FCN_PM710, ADDR_PM710)
request_PWB= create_request(PWB_PM710, LNG_PM710, FCN_PM710, ADDR_PM710)
request_PWC= create_request(PWC_PM710, LNG_PM710, FCN_PM710, ADDR_PM710)
request_PWT= create_request(PWT_PM710, LNG_PM710, FCN_PM710, ADDR_PM710)


##in this dictionary store all the parameters of the desired data to collect
info_obj = {'freq': {
            'request': request_freq,
            'ans_format': '>bbbHH',
            'ans_index': 3,
            'scpi_cmd':scpi_FREQ,
            'ans': "",
            'scale':100
            },
            'IA': {
            'request': request_IA,
            'ans_format': '>bbbHH',
            'ans_index': 3,
            'scpi_cmd':scpi_IA,
            'ans': "",
            'filter':GLITCH_FILTER_SIZE*[1],
            'scale':10
            },
            'IB': {
            'request': request_IB,
            'ans_format': '>bbbHH',
            'ans_index': 3,
            'scpi_cmd':scpi_IB,
            'ans': "",
            'filter':GLITCH_FILTER_SIZE*[1],
            'scale':10
            },
            'IC': {
            'request': request_IC,
            'ans_format': '>bbbHH',
            'ans_index': 3,
            'scpi_cmd':scpi_IC,
            'ans': "",
            'filter':GLITCH_FILTER_SIZE*[1],
            'scale':10
            },
             'VAB': {
            'request': request_VAB,
            'ans_format': '>bbbHH',
            'ans_index': 3,
            'scpi_cmd':scpi_VAB,
            'ans': "",
            'filter':GLITCH_FILTER_SIZE*[1],
            'scale':10
            },
             'VBC': {
            'request': request_VBC,
            'ans_format': '>bbbHH',
            'ans_index': 3,
            'scpi_cmd':scpi_VBC,
            'ans': "",
            'filter':GLITCH_FILTER_SIZE*[1],
            'scale':10
            },
             'VCA': {
            'request': request_VCA,
            'ans_format': '>bbbHH',
            'ans_index': 3,
            'scpi_cmd':scpi_VCA,
            'ans': "",
            'filter':GLITCH_FILTER_SIZE*[1],
            'scale':10
            },
             'PFA': {
            'request': request_PFA,
            'ans_format': '>bbbHH',
            'ans_index': 3,
            'scpi_cmd':scpi_PFA,
            'ans': "",
            'filter':GLITCH_FILTER_SIZE*[1],
            'scale':100
            },
            'PWA': {
            'request': request_PWA,
            'ans_format': '>bbbHH',
            'ans_index': 3,
            'scpi_cmd':scpi_PWA,
            'ans': "",
            'scale':10
            },
            'PWB': {
            'request': request_PWB,
            'ans_format': '>bbbHH',
            'ans_index': 3,
            'scpi_cmd':scpi_PWB,
            'ans': "",
            'scale':10
            },
             'PWC': {
            'request': request_PWC,
            'ans_format': '>bbbHH',
            'ans_index': 3,
            'scpi_cmd':scpi_PWC,
            'ans': "",
            'scale':10
            },
             'PWT': {
            'request': request_PWT,
            'ans_format': '>bbbHH',
            'ans_index': 3,
            'scpi_cmd':scpi_PWT,
            'ans': "", 
            'scale':10
            }
        }


if __name__ == '__main__':
    while(1):
        ##create socket
        try:
            pm710 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            pm710.settimeout(0.1)
            pm710.connect((IP_PM710, PR_PM710))
        except:
            print("cant connet to socket :(")
            logging.error("cant connect socket")
            continue
        
        for key, items in info_obj.items():
            items['ans'] = ""
            print(items)
            try:
                response = request_data(pm710,items['request'])
                items['ans'] = response
            except:
                logging.error("error request %s: %s"%(key, sys.exc_info()[0])) 
        
        now = time.strftime('%Y-%m-%dT%H:%M:%S',time.localtime(time.time()))
        
        ##write the data into the database
        for key, items in info_obj.items():
            if(len(items['ans']) == 7):
                out = parse_data(items['ans'], items['ans_index'],items['ans_format'])
                out =  float(out)/items['scale']
                print("%s :%s"%(key, out))
                if(key in ['freq', 'PWA', 'PWB', 'PWC', 'PWT' ]):
                    insertDB(items['scpi_cmd'], str(out), now)
                else:
                    ###to filter out the glitches, only triggers the alarm when there are GLITCH_FILTER_SIZE consecutive bad data
                    items['filter'].pop(0)
                    items['filter'].append(out)
                    if(out>0):
                        insertDB(items['scpi_cmd'], str(out), now)
                    elif(out<0 and all(x<=0 for x in items['filter'])):
                        insertDB(items['scpi_cmd'], str(out), now)
        pm710.close()
        time.sleep(RATE)
