import serial
import socket
import logging

###
### Code that runs in the raspberry pi. It reads the messages that are broadcasted via
### the USB by the vaisala and send them to the monitoring system. (This can be done
### way better if this code would be smart and only answer to requests from the monitoring
### computer...but it is what it is..)
###
### Since there were a lot of issues with the broken pipe error there is a cronjob
### checking that this code is running
###
### Cronjob
### */5 * * * * /home/apex/check_running.sh
###


ip = '10.0.6.70'    ##monitor
#ip = '127.0.0.1'
port = 12334
ttyfile = '/dev/ttyUSB0'

log = True
log_file = 'change_media.log'
log_level='INFO'

###
###
###
if(log):
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', filename=log_file, level=log_level)
    logging.info("start logging")


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
sock.connect((ip, port))

weath = serial.Serial(ttyfile, baudrate=19200)

while(1):
    try:
        msg = weath.readline()
        print(msg)
        sock.send(msg)
    except KeyboardInterrupt:
        print("Error!!")
        break
    except socket.error as e:
        if(log):
            logging.error("socket error: %s"%repr(e))
        break
    except Exception as e:
        if(log):
            logging.error("%s" %repr(e))

logging.error("out of the loop!")


