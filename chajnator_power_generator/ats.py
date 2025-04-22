#!/usr/local/bin/python

import requests
import time
from common import *


###
### Since PLCs are the worst they only can communicate with one client at the time,
### and since we are stuck with mango, it has the priority for the communication
### Then we need to communicate with mango via its rest API to get the info of the PLC
### To make it worst, the damn rest API needs the XID of the point that you want to take
###

sleep_time = 60



def get_by_XID(xid):
    s = requests.Session()
    ##this is the token to identify yourself
    hdr = {'Accept':'application/json', 'Authorization':'FAKE_AUTH'}    ##ask the software people for the actual token..
    s.headers.update(hdr)
    r = s.get('http://monitor:9000/rest/v1/users/current')
    #print r.text
    if r.status_code != 200:
        print('Error: '+str(r.status_code))
        return float('inf')
    msg = 'http://monitor:9000/rest/v1/realtime/by-xid/'
    ans = s.get(msg+xid)
    ans = ans.json()['value']
    return ans



if __name__ == '__main__':
    ## SCPI monitoring, mango XID
    info_points = { 'APEX:POWER:ATS:CRITICAL_MODE': 'DP_adda46bc-3c06-462c-aefd-5d727ec09629'}
    while(1):
        now = time.strftime('%Y-%m-%dT%H:%M:%S',time.localtime(time.time()))
        for key, value in info_points.items():
            try:
                item = get_by_XID(value)
                print(item)
                if(item!= float('inf')):
                    insertDB(key, str(item), now)
            except:
                continue 
        time.sleep(sleep_time)
