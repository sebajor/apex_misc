#!/usr/local/bin/python

import time
from common import *
import socket 

"""
This code runs in the monitor computer and talks witht the nodemcu to query the values of the sensors in the water tank.
Check the .ino code to program the nodemcu.

"""


waterTankBoxIP = '10.0.33.47'
port = 12334
timeout = 5
sleep_period = 60


SCPI_WT_MAX = 'APEX:SEQ:WATERTANK:MAX'
SCPI_WT_LEAK = 'APEX:SEQ:WATERTANK:LEAKSENSOR'
SCPI_WT_MIN = 'APEX:SEQ:WATERTANK:MIN'

def request_data(sock, scpi, sleep=0.1):
    sock.send((scpi+'\n').encode())
    time.sleep(sleep)
    ans = sock.recv(512).decode()
    if('\r\n' in ans):
        data = int(ans.split('\r\n')[0])
        return data
    raise Exception("Some error occurred D:")
        


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(10)
    sock.connect((waterTankBoxIP, port))
    
    while(1):
        now = time.strftime('%Y-%m-%dT%H:%M:%S',time.localtime(time.time()))
        try:
            max_data = request_data(sock, SCPI_WT_MAX)
            time.sleep(1)
            insertDB(SCPI_WT_MAX, max_data, now)
        except:
            print("Error getting max")

        try:
            min_data = request_data(sock, SCPI_WT_MIN)
            time.sleep(1)
            insertDB(SCPI_WT_MIN, min_data, now)
        except:
            print("Error getting min")

        try: 
            leak_data = request_data(sock, SCPI_WT_LEAK)
            time.sleep(1)
            insertDB(SCPI_WT_LEAK, leak_data, now)
        except:
            print("Error gettin leak")
        time.sleep(sleep_period)

