#!/usr/src/Python-2.7.13/python
from   common import *
import requests
import json
import time

##
url = 'http://10.0.6.232:5000/pms/datamon/'
SCPI_HEAD = 'APEX:PV'

### The pv plant runs a json server with several monitoring points... in principle
### I just read the source code in the pv computer and guess the meaning of the 
### items in each dictionary
###
### The system answers to POST commands with certains dictionaries and the return 
### is a json object that has several keys.. the keywords for each message are 
### stored as a tuple where the first item is the message for the http server
### and the second item is a dictonary where the keys are also the keys of the 
### json answer and the associated item of the key is the SCPI command of the monitor db.
### If you want to add another field to the monitoring just uncomment and put the
### associated SCPI cmd (you also would need to create the field in the monitoring table)
###
###


pv_state = [{'DataType':'PVstate'}, {
    'operState': SCPI_HEAD+':PV_STATE', 
    'acPower': SCPI_HEAD+':PV_POW',
    'temPerature1': SCPI_HEAD+':PV_TEMP',
    'acVoltageAVG': SCPI_HEAD+':PV_AVG_VOLT',
    'acCurrentSUM': SCPI_HEAD+':PV_SUM_CURR',
    #'acVoltageR': SCPI_HEAD+':PV_VOLT_R',
    #'acVoltageS': SCPI_HEAD+':PV_VOLT_S',
    #'acVoltageT': SCPI_HEAD+':PV_VOLT_T',
    #'acCurrentR': SCPI_HEAD+':PV_CURR_R',
    #'acCurrentS': SCPI_HEAD+':PV_CURR_S',
    #'acCurrentT': SCPI_HEAD+':PV_CURR_T',
    #'acPowerR': SCPI_HEAD+':PV_POW_R',
    #'acPowerS':SCPI_HEAD+':PV_POW_S',
    #'acPowerT':SCPI_HEAD+':PV_POW_T',
    #'modelName',
    #'deviceId', 
    #'version', 
    #'inverterCapacity',
    #'reactivePowerR',
    #'reactivePowerS',
    #'reactivePowerT',
    #'reactivePower',
    #'acVaAll',
    #'acVaR',
    #'acVaS',
    #'acVaT',
    #'frequency',
    #'pfactorR',
    #'pfactorS',
    #'pfactorT',
    #'cosPhi',
    #'beginEnergy',
    #'todayTotalPower',
    #'todayTotalTime',
    #'powDelivered',
    #'powCharged',
    #'energyR',
    #'energyS',
    #'energyT',
    #'getTime', 
    }
]

##the system can display more stuffs changing the deviceid, that can be
##PCSM, PCSS, PCS1, PCS2, PCS3,PCS4
pcs_state = [{'DataType':'PCSstate', 'DeviceID':'PCS'},{
    'operState': SCPI_HEAD+':ESS_STATE',
    'acCurrentR': SCPI_HEAD+':ESS_CURR_R',
    'acCurrentS': SCPI_HEAD+':ESS_CURR_S',
    'acCurrentT': SCPI_HEAD+':ESS_CURR_T',
    'acPower': SCPI_HEAD+':ESS_AC_POW',
    'acVoltageR': SCPI_HEAD+':ESS_VOLT_R',
    'acVoltageS': SCPI_HEAD+':ESS_VOLT_S',
    'acVoltageT': SCPI_HEAD+':ESS_VOLT_T',
    #'acPowerR': SCPI_HEAD+':ESS_POW_R',
    #'acPowerS': SCPI_HEAD+':ESS_POW_S',
    #'acPowerT': SCPI_HEAD+':ESS_POW_T',
    #'frequency': SCPI_HEAD+':ESS_FREQ',
    #'getTime',
    #'modelName',
    #'deviceId',
    #'version',
    #'inverterCapacity',
    #'reactivePowerR',
    #'reactivePowerS',
    #'reactivePowerT',
    #'reactivePower',
    #'acVoltageAVG',
    #'acCurrentSUM',
    #'acVaAll',
    #'acVaR',
    #'acVaS',
    #'acVaT',
    #'pfactorR',
    #'pfactorS',
    #'pfactorT',
    #'cosPhi',
    #'beginEnergy',
    #'beginEnergyChg',
    #'todayTotalPower',
    #'todayTotalTime',
    #'powDelivered',
    #'powCharged',
    #'temPerature1',
    #'acVoltage',
    #'acCurrent',
    #'energyR',
    #'energyS',
    #'energyT',
    #'beingEnergyChg'
    }
]

bms_state = [{'DataType':'BMSstate'},{
    'soc': SCPI_HEAD+':BATT_SOC',
    'soh': SCPI_HEAD+':BATT_SOH',
    'dcVoltage': SCPI_HEAD+':BATT_DC_VOLT',
    'dcCurrent': SCPI_HEAD+':BATT_DC_CURR',
    'dcPower': SCPI_HEAD+':BATT_DC_POW',
    'maxTmp': SCPI_HEAD+':BATT_HIGH_TEMP',
    'minTmp': SCPI_HEAD+':BATT_LOW_TEMP',
    #'getTime',
    #'deviceId',
    'maxCellVolt': SCPI_HEAD+':BATT:CELL_HIGH_V',
    'minCellVolt': SCPI_HEAD+':BATT:CELL_LOW_V',
    #'Protect1',
    #'Protect2',
    #'Protect3',
    #'Protect4',
    #'Alarm1': SCPI_HEAD+':BATT:ALARM1',
    #'Alarm2': SCPI_HEAD+':BATT:ALARM2',
    #'Alarm3': SCPI_HEAD+':BATT:ALARM3',
    #'Alarm4': SCPI_HEAD+':BATT:ALARM1',
    #'chargeLimit',
    #'dischargeLimit': SCPI_HEAD+':BATT:DISCHARGE_LIM',
    #'ChargedEnergy':SCPI_HEAD+':BATT:CHARGE_ENERGY',
    #'DischargedEnergy':SCPI_HEAD+':BATT:DISCHARGE_ENERGY',
    #'todayTotalTime',
    }
]


pg_state = [{'DataType':'DGstate'}, {
    'operState': SCPI_HEAD+':GEN_STATE',
    #'acVoltageR': SCPI_HEAD+':GEN_VOLT_R',
    #'acVoltageS': SCPI_HEAD+':GEN_VOLT_S',
    #'acVoltageT': SCPI_HEAD+':GEN_VOLT_T',
    #'acCurrentR': SCPI_HEAD+':GEN_CURR_R',
    #'acCurrentS': SCPI_HEAD+':GEN_CURR_S',
    #'acCurrentT': SCPI_HEAD+':GEN_CURR_T',
    #'acPowerR': SCPI_HEAD+':GEN_POW_R',
    #'acPowerS': SCPI_HEAD+':GEN_POW_S',
    #'acPowerT': SCPI_HEAD+':GEN_POW_T',
    'acPower': SCPI_HEAD+':GEN_POW',
    'acVoltageAVG': SCPI_HEAD+':GEN_VOLT',
    'acCurrentSUM': SCPI_HEAD+':GEN_CURR_SUM',
    'frequency': SCPI_HEAD+':GEN_FREQ',
    #'getTime',
    #'modelName',
    #'deviceId',
    #'version',
    #'inverterCapacity',
    #'reactivePowerR',
    #'reactivePowerS',
    #'reactivePowerT',
    #'reactivePower',
    #'acVoltageAVG',
    #'acVaAll',
    #'acVaR',
    #'acVaS',
    #'acVaT',
    #'pfactorR',
    #'pfactorS',
    #'pfactorT',
    #'cosPhi',
    #'beginEnergy',
    #'todayTotalPower',
    #'todayTotalTime',
    #'powDelivered',
    #'powCharged',
    #'temPerature1',
    #'acCurrent',
    #'energyR',
    #'energyS',
    #'energyT',
    #'modeType'
    }
]

#no idea what is this
#button_chk = {'ButtonCHK':
#    ['operationMode', 
#     'sysAction']
#}

sys_state = [{'DataType':'SYS_STATE'},{
    'temperature1': SCPI_HEAD+':TEMP1',
    'temperature2': SCPI_HEAD+':TEMP2',
    'invCommErr': SCPI_HEAD+':INV_COMM_ERR',
    'envCommErr': SCPI_HEAD+':ENV_COMM_ERR',
    'tempCommErr': SCPI_HEAD+':TEMP_COMM_ERR',
    'essCommErr': SCPI_HEAD+':ESS_COMM_ERR',
    'pcsmCommErr': SCPI_HEAD+':PCSM_COMM_ERR',
    'pcssCommErr': SCPI_HEAD+':PCSS_COMM_ERR',
    'dgCommErr': SCPI_HEAD+':GEN_COMM_ERR',
    #'insolation1',
    #'envErr1',
    #'humidity',
    #'timeDataPV',
    #'timeDataPCS',
    #'timeDataDG',
    #'timeDataLOAD',
    #'maxInverter',
    #'inv0stt',
    #'inv1stt',
    #'inv2stt',
    #'inv3stt',
    #'inv4stt'
    }
]



#the system returns a list with 26 values (i dont know all of them yet)
# [dc_volt, dc_volt, dc_current, no_idea, ac_volt_r, ac_volt_s, ac_volt_t, no_idea,
# ac_curr_r, ac_curr_s, ac_curr_t, no_idea, ac_pow_r, ac_pow_r, ac_pow_t, ...no idea]


#inv1: PV_inverter
#inv2: PCS_M
#inv3: PCS_S
#inv4: LOAD
#inv5: Adam.. this is a dictionary with the keys relayState, dieselPower (this is the value that goes into the ADAM)

inverters = [{'DataType':'INVERTER'},{
    'inv1': SCPI_HEAD+':PV_INVERTER',
    'inv2': SCPI_HEAD+':PCS_M_INVERTER',
    'inv3': SCPI_HEAD+':PCS_S_INVERTER',
    'inv4': SCPI_HEAD+':LOAD_INVERTER',
    #'inv5': SCPI_HEAD+':ADAM'          ##like this is different I put it inside the function
    #'maxInverter',
    #'getTime'
    }
]


###query and insertion functions

def query_values(info, url, insert_db=False):
    """
    info is the previously defined tuples, this function doesnt work
    for the inverters query
    """
    try:
      ans = requests.post(url, data=info[0])
    except Exception as e:
      print("Exception catch: {:}".format(e))
      return 0
    if(ans.status_code!=200):
        print('Query error!')
        return 0
    dat = json.loads(ans.content.decode())
    stamp = time.strftime('%Y-%m-%dT%H:%M:%S',time.localtime(time.time()))
    out = {}
    for key, value in info[1].items():
        out[key] = dat[key]
        if(insert_db):
            insertDB(value, dat[key], stamp)
    return out

def query_inverters(info,url, insert_db=False):
    subfields = {':DC_VOLT':0, 
                 ':DC_CURR':2,
                 #':AC_VOLT_R':4,
                 #':AC_VOLT_S':5,
                 #':AC_VOLT_T':6,
                 #':AC_CURR_R':8,
                 #':AC_CURR_S':9,
                 #':AC_CURR_T':10,
                 ':AC_POW_R':12,
                 ':AC_POW_S':13,
                 ':AC_POW_T':14,
                 ':AC_POW_SUM':15
            }   ##CHECK!!!
    try:
      ans = requests.post(url, data=info[0])
    except Exception as e:
      print("Exception catch: {:}".format(e))
      return 0
    if(ans.status_code!=200):
        print('Query error!')
        return 0
    dat = json.loads(ans.content.decode())
    stamp = time.strftime('%Y-%m-%dT%H:%M:%S',time.localtime(time.time()))
    if(insert_db):
        for key, scpi_msg in info[1].items():
            data = dat[key]
            for scpi_sub, index in subfields.items():
                scpi = scpi_msg+scpi_sub
                value = data[index]
                insertDB(scpi, value, stamp) 
        ##now we deal with the adam
        adam = dat['inv5']
        insertDB('APEX:PV:ADAM:RELAY_STATE',
                 adam['relayState'],
                 stamp)
        ##right nowthis is just the number at the dac.. it should be converted to 
        ##requested power to the generator
        insertDB('APEX:PV:ADAM:DAC_VALUE',
                 adam['dieselPower'],
                 stamp)
    return dat

##debug function
#def insertDB(scpi, data, stamp):
#    print(scpi+"\t"+str(data)+"\t"+str(stamp))

if __name__ == '__main__':
  sleep = 30
  # MCA: The queries were separated by 0.5 secs. This might be overwhelming the JSON server, speciually if nthe program does not
  # create one thread per query servicing, increasing this to 3 secs 
  inter_query_sleep = 3
  while(1):
    print('asd')
    query_values(pv_state, url, insert_db=True)
    time.sleep(inter_query_sleep)
    query_values(pcs_state, url, insert_db=True)
    time.sleep(inter_query_sleep)
    query_values(bms_state, url, insert_db=True)
    time.sleep(inter_query_sleep)
    query_values(pg_state, url, insert_db=True)
    time.sleep(inter_query_sleep)
    query_values(sys_state, url, insert_db=True)
    time.sleep(inter_query_sleep)
    # MCA, not necessary: aux = query_inverters(inverters, url, insert_db=True)
    query_inverters(inverters, url, insert_db=True)
    time.sleep(sleep)
      

