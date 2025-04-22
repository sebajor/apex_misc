#!/usr/local/bin/python
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.utilities import computeCRC, computeLRC

import struct
import string
import os
import signal
import sys
import math
import socket
from   time import *
import logging
from common import *

"""
The measurement is made by a Wm14-96.av5.3.d.s, the voltage is measured rigth away but the current is reduced by a set of transformers so the current that reach the equipemnt is in the 1A range or so.

Like the wm14 only comunicates via serial commands there is a lantronix connected.

Here is the communication protocol https://carlogavazzisales.com/usermanuals/WM14BXCPv2r0ENG0804.pdf 
http://productos-iot.com/wp-content/uploads/2019/10/wm1496-manual-de-instalaci%C3%B3n.pdf


Note that if you go and measure the actual currents from the sequitor generators will not match the read values by the wm14 since there is a part of the circuit that is not being measured..
"""

##
voltage_cf = 1. /10     ##voltage is given with 1 decimal in V
current_cf = 20./1000   ##current is given in mA
power_cf = 1./10        ##

##SCPI commands
SCPI_L1_AMP = "APEX:SEQPWR:L1:AMP"
SCPI_L1_VOLT = "APEX:SEQPWR:L1:VOLT"
SCPI_L2_AMP = "APEX:SEQPWR:L2:AMP"
SCPI_L2_VOLT = "APEX:SEQPWR:L2:VOLT"
SCPI_L3_AMP = "APEX:SEQPWR:L3:AMP"
SCPI_L3_VOLT = "APEX:SEQPWR:L3:VOLT"


SCPI_L1_2_VOLT = "APEX:SEQPWR:L1-2:VOLT"
SCPI_L3_1_VOLT = "APEX:SEQPWR:L3-1:VOLT"
SCPI_L2_3_VOLT = "APEX:SEQPWR:L2-3:VOLT"


SCPI_FREQ = "APEX:SEQPWR:TOTALPWR:FREQ"
SCPI_PF = "APEX:SEQPWR:TOTALPWR:PF"


#  ---- Cummins configuration  -----

LNG_Cummins_1 = 12         # Amount of consecutive data to be read in request 1
LNG_Cummins_2 = 8
FCN_Cummins = 0x04                # Kind of register to be polled
ADR_Cummins = 0x01           # NSX Modbus Address (set locally on device)
RATE = 1                         # Measurement rate in seconds

# ----- Lantronix Network Parameters  -----
Lantronix_IP = '10.0.6.243'
port = 10001
register_1 = 40640
register_2 = 40690

# 12 Register request structure starting from register_1

Data = struct.pack('>HH', (register_1 -40000), LNG_Cummins_1)
request_1 = struct.pack('>BB', ADR_Cummins , FCN_Cummins) + Data
request_1 = request_1 + struct.pack(">H", computeCRC(request_1))

# 10 Register request structure starting from register_2

Data_2 = struct.pack('>HH', (register_2 -40000), LNG_Cummins_2)
request_2 = struct.pack('>BB', ADR_Cummins , FCN_Cummins) + Data_2
request_2 = request_2 + struct.pack(">H", computeCRC(request_2))

###connect to the lantronix
NSX = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
NSX.settimeout(2.0)
NSX.connect((Lantronix_IP, port))

def request_a(voltage_cf, current_cf, power_cf, insert_db=False):
  NSX.sendall(request_1)
  sleep(0.3)
  data_1 = NSX.recv(29)
  now = strftime('%Y-%m-%dT%H:%M:%S',localtime(time()))
  data = struct.unpack('13H', data_1[3:])
  print(data)
  [vl1n, il1, pl1, vl2n, il2, pl2, vl3n, il3, pl3, vl1_2, vl3_1, vl2_3, _] = data 
  vl1n *= voltage_cf
  vl2n *= voltage_cf
  vl3n *= voltage_cf
  pl1 *= power_cf
  pl2 *= power_cf
  pl3 *= power_cf
  il1 *= current_cf
  il2 *= current_cf
  il3 *= current_cf
  if(not insert_db):
    return [vl1n, il1, pl1, vl2n, il2, pl2, vl3n, il3, pl3, vl1_2, vl3_1, vl2_3]
  insertDB(SCPI_L1_VOLT, vl1n, now)
  insertDB(SCPI_L1_AMP, il1, now)
  insertDB(SCPI_L2_VOLT, vl2n, now)
  insertDB(SCPI_L2_AMP, il2, now)
  insertDB(SCPI_L3_VOLT, vl3n, now)
  insertDB(SCPI_L3_AMP, il3, now)
  insertDB(SCPI_L1_2_VOLT, vl1_2, now)
  insertDB(SCPI_L3_1_VOLT, vl3_1, now)
  insertDB(SCPI_L2_3_VOLT, vl2_3, now)



def request_b():
	NSX.sendall(request_2)
	sleep(0.3)
        data_2 = NSX.recv(21)
	x = [f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13,f14,f15,f16,f17,f18,f19,f20,f21] = struct.unpack('>21B', data_2)
	get_bin = lambda x, n: format(x, 'b').zfill(n)

	now = strftime('%Y-%m-%dT%H:%M:%S',localtime(time()))
	
	# frec
        b1 = x[9]
        b2 = x[10]
        a1 = get_bin(int(b2), 8)
        a2 = get_bin(int(b1), 8)
        x1 = str(a1)+ str(a2)
        frec = float((int(x1, 2)))/10.
	pfl1 = float(x[13])/100.
	pfl2 = float(x[14])/100.
	pfl3 = float(x[15])/100.
	pftot = float(x[16])/100.

	#print SCPI_FREQ + ' ' + str(frec) + ' ' + now
	#print SCPI_PF + ' ' + str(pftot) + ' ' + now

	insertDB(SCPI_FREQ, frec, now)
	insertDB(SCPI_PF, pftot, now)


if __name__ == '__main__':
  while(1):
    try:
      request_a(voltage_cf, current_cf, power_cf, insert_db=True)
      request_b()
      sleep(60)		
    except KeyboardInterrupt:
            print 'Cancelled by keyboard \n'
            sys.exit()
  NSX.close()
  
