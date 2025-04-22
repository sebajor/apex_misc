#!/usr/local/bin/python
import socket
import time
import serial
from common import *
import logging

###
### This code runs in the monitoring computer and receives the messages from the raspberry pi that is 
### reading the vaisala.
###
### The Vaisala that PCA repair is constantly sendig data through its USB connection that is 
### just a standard serial console.
### To put it only a raspberry pi is connected to it to get the values and send the values
### via a socket... In principle the raspberry pi acts just as a media change.
###

update_time = 1     ##minute

ip = '0.0.0.0'
port = 12334

log = True
log_file = '/home/apexmon/monitoringV2/seqTasks/log/weather.log'
log_level="INFO"


scpi_cmds = {
        "Dm": "APEX:SEQWEATHER:WIND_DIR",
        "Sm": "APEX:SEQWEATHER:WIND_SPEED_AVG",
        "Sx": "APEX:SEQWEATHER:WIND_SPEED_MAX",
        "Ta": "APEX:SEQWEATHER:AIR_TEMPERATURE",
        "Ua": "APEX:SEQWEATHER:AIR_HUMIDITY",
        "Pa": "APEX:SEQWEATHER:AIR_PRESSURE",
        "Rc": "APEX:SEQWEATHER:RAIN_ACC",
        "Rd": "APEX:SEQWEATHER:RAIN_DURATION",
        "Ri": "APEX:SEQWEATHER:RAIN_INTENSITY",
        #"Hc": "APEX:SEQWEATHER:HAIL_ACC",
        #"Hd": "APEX:SEQWEATHER:HAIL_DURATION",
        #"Hi": "APEX:SEQWEATHER:HAIL_INTENSITY",
        }



###Vaisala parsing 
class vaisala_weather():
    ##class to parse the weather station message

    def __init__(self, usb=False,ttyfile='/dev/ttyUSB0',baudrate=19200):
        if(usb):
            self.ser = serial.Serial(ttyfile, baudrate)

    def get_message(self, msg=None, logger=None):
        if(msg is None):
            msg = self.ser.readline()
            print(msg)
        msg = msg.decode().split(',')
        if('r1' in msg[0]):
            parse_msg = self.wind_msg_decode(msg, logger=logger)
            parse_msg['type'] = 'wind'
        elif('r2' in msg[0]):
            parse_msg = self.pressure_msg_decode(msg, logger=logger)
            parse_msg['type'] = 'pressure'
        elif('r3' in msg[0]):
            parse_msg = self.precipitation_msg_decode(msg, logger=logger)
            parse_msg['type'] = 'precipitation'
        elif('r5' in msg[0]):
            ##supervision msg (like how is the voltage.)
            parse_msg = dict()
            parse_msg['type'] = 'bullshit'
            pass
        else:
            parse_msg = dict()
        return parse_msg

    def wind_msg_decode(self, msg, logger=None):
        parse_msg = dict()
        for word in msg[1:]:
            try:
                if('Dn' in word):
                    ##wind direction minimum
                    data = word.split('=')[-1].split('D')[0]
                    parse_msg['Dn'] = float(data)
                elif('Dm' in word):
                    ##wind direction average
                    data = word.split('=')[-1].split('D')[0]
                    parse_msg['Dm'] = float(data)
                elif('Dx' in word):
                    ##wind direction max
                    data = word.split('=')[-1].split('D')[0]
                    parse_msg['Dx'] = float(data)
                elif('Sn' in word):
                    #min wind speed
                    data = word.split('=')[-1][:-1]
                    parse_msg['Sn'] = float(data)
                elif('Sm' in word):
                    ##avg wind speed in m/s
                    data = word.split('=')[-1].split('M')[0]
                    parse_msg['Sm'] = float(data)
                elif('Sx' in word):
                    ##max wind speed in m/s
                    data = word.split('=')[-1].split('M')[0]
                    parse_msg['Sx'] = float(data)
            except:
                if(logger is not None):
                    logging.exception("message")
                continue
    
        return parse_msg

    def pressure_msg_decode(self, msg, logger=None):
        parse_msg = dict()
        for word in msg[1:]:
            try:
                if('Ta' in word):
                    #air temperature
                    data = word.split('=')[-1].split('C')[0]
                    parse_msg['Ta'] = float(data)
                elif('Ua' in word):
                    #relative humidity
                    data = word.split('=')[-1].split('P')[0]
                    parse_msg['Ua'] = float(data)
                elif('Pa' in word):
                    #air pressure hPa
                    data = word.split('=')[-1].split('H')[0]
                    parse_msg['Pa'] = float(data)
            except:
                if(logger is not None):
                    logging.exception("message")
                continue
        return parse_msg

    def precipitation_msg_decode(self, msg, logger=None):
        parse_msg = dict()
        for word in msg[1:]:
            try:
                if('Rc' in word):
                    #rain accumulation in mm
                    data = word.split('=')[-1].split('M')[0]
                    parse_msg['Rc'] = float(data)
                elif('Rd' in word):
                    #rain duration in sec
                    data = word.split('=')[-1].split('s')[0]
                    parse_msg['Rd'] = float(data)
                elif('Ri' in word):
                    #rain intensity in mm/h
                    data = word.split('=')[-1].split('M')[0]
                    parse_msg['Ri'] = float(data)
                elif('Hc' in word):
                    #hail accumulation hits/cm^2
                    data = word.split('=')[-1].split('M')[0]
                    parse_msg['Hc'] = float(data)
                elif('Hd' in word):
                    ##hail duration in sec
                    data = word.split('=')[-1].split('s')[0]
                    parse_msg['Hd'] = float(data)
                elif('Hi' in word):
                    ##hail intensity in hits/cm^2h
                    data = word.split('=')[-1].split('M')[0]
                    parse_msg['Hi'] = float(data)
                elif('Rp' in word):
                    ##rain peak intensity in mm/h
                    data = word.split('=')[-1].split('M')[0]
                    parse_msg['Rp'] = float(data)
                elif('Hp' in word):
                    ##hail peak intensity in hits/cm/h
                    data = word.split('=')[-1].split('M')[0]
                    parse_msg['Rp'] = float(data)
            except:
                if(logger is not None):
                    logging.exception("message")
                continue
        return parse_msg


    def close(self):
        self.ser.close()



if __name__ == '__main__':
    if(log):
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', filename=log_file, level=log_level)
        logging.info("Starting sequitor weather")
    parser = vaisala_weather()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((ip, port))
    sock.listen(1)

    while(1):
        client, client_addr = sock.accept()
        logging.info('Connected to {:}'.format(client_addr))
        start = time.time()
        acc_data = dict()
        while(1):
            try:
                data = client.recv(1024)
                if(data == b""):
                    if(log):
                        logging.error("client disconnected")
                    break
                msg = parser.get_message(msg=data, logger=log)
                del msg['type']
                print(msg)
                if((time.time()-start)>update_time*60):
                    print("Inserting data")
                    print(acc_data)
                    print(" ")
                    now = time.strftime('%Y-%m-%dT%H:%M:%S',time.localtime(time.time()))
                    for key, value in acc_data.items():
                        if(not (key in scpi_cmds.keys())):
                           continue 
                        if(log):
                            logging.info("inserting {:} in {}".format(sum(value)/len(value), scpi_cmds[key]))
                            print("inserting {:} in {}".format(sum(value)/len(value), scpi_cmds[key]))

                        if((key=='Sx')):
                            insertDB(scpi_cmds[key], max(value), now)
                        else:
                            insertDB(scpi_cmds[key], sum(value)/len(value), now)
                        print("another iter\n")
                    print('stop inserting data')
                    time.sleep(0.1)
                    ##reset the accumulated data
                    acc_data = dict()
                    start = time.time()
                else:
                    for key, value in msg.items():
                        if(not key in acc_data.keys()):
                            acc_data[key] = []
                        acc_data[key].append(value)
            except KeyboardInterrupt:
                print('closing')
                break
            except ValueError:
                if(log):
                    logging.error("value error!")
                    logging.exception("message")
                print('ups')
            except Exception as e:
                if(log):
                    logging.error("Exception: %s"%repr(e))
                print('%s'%repr(e))

    sock.close()
    if(log):
        logging.error("Finish code D:")





