#!/usr/local/bin/python

####################################################################################
# ModBus Monitoring points retrieval from Cerro Chico Charge Controller.
#
#
# Author: Jorge Ramirez, Juan Pablo Araneda
# Created: 2018/04/09
# Modified: 2025/?/?
#   I modify this since was not working... I have to dive in the registers addresses to check
#   where the errors were.
#   The info for this code was taken from here https://www.victronenergy.com/live/ccgx:modbustcp_faq
#   there is a link to a excel spreadsheet with the registers addresses
#
#   Note that there victronics also has a webpage that you could access to 
#   check that the read values are correct.
###################################################################################

import numpy as np
import os
from   time import *
from pymodbus.client.sync import ModbusTcpClient
from common import *


def get_battery_voltage(client, dev_id):
    ans = client.read_holding_registers(771, unit=dev_id)
    return (ans.getRegister(0)/100.)

def get_battery_current(client, dev_id):
    ans = client.read_holding_registers(772, unit=dev_id)
    return (ans.getRegister(0)/10.)


def get_pv_voltage(client, dev_id):
    ans = client.read_holding_registers(776, unit=dev_id)
    return (ans.getRegister(0)/100.)

def get_pv_current(client, dev_id):
    ans = client.read_holding_registers(777, unit=dev_id)
    return (ans.getRegister(0)/10.)

def get_pv_power(client, dev_id):
    ans = client.read_holding_registers(789, unit=dev_id)
    return (ans.getRegister(0)/10.)

def get_solar_charger_error(client, dev_id):
    ans = client.read_holding_registers(788, unit=dev_id)
    return (ans.getRegister(0))


def get_inverter_dc_voltage(client, dev_id):
    ans = client.read_holding_registers(26, unit=dev_id)    #
    dc_volt = (ans.getRegister(0)/100.)
    return dc_volt


def get_inverter_dc_curr(client, dev_id):
    ans = client.read_holding_registers(27, unit=dev_id)    #
    dc_curr = (ans.getRegister(0))
    ##two complement
    if(dc_curr>2**15):
        dc_curr -=2**16
    dc_curr = dc_curr/10.
    return dc_curr

def get_inverter_ac_volt(client, dev_id):
    ans = client.read_holding_registers(15, unit=dev_id)
    ac_volt = (ans.getRegister(0)/10.)
    return ac_volt

def get_inverter_ac_curr(client, dev_id):
    ans = client.read_holding_registers(18, unit=dev_id)
    ac_curr = (ans.getRegister(0)/10.)
    return ac_curr

def get_inverter_ac_freq(client, dev_id):
    ans = client.read_holding_registers(21, unit=dev_id)
    freq = (ans.getRegister(0)/100.)
    return freq


def get_inverter_ac_power(client, dev_id):
    ans = client.read_holding_registers(23, unit=dev_id)
    ac_pow = (ans.getRegister(0)*10)
    return ac_pow


def get_inverter_error(client, dev_id):
    ans = client.read_holding_registers(32, unit=dev_id)
    error_code = (ans.getRegister(0))    
    return error_code


def get_inverter_state(client, dev_id):
    ans = client.read_holding_registers(31, unit=dev_id)
    state = (ans.getRegister(0))    #0=Off;1=Low Power;2=Fault;3=Bulk;4=Absorption;5=Float;6=Storage;7=Equalize;8=Passthru;9=Inverting;10=Power assist;11=Power supply;244=Sustain;252=External control
    return state









if __name__ == '__main__':
    host = '10.0.6.211'
    port = 502
    refresh_time = 60     ##seconds  
    blue_solar_id = 226   ##for the switches
    smart_solar_id = 224  ##for all the rest (communication)
    multiplus_id = 227    ##inverter

    ##multiplus compact 24/2000/50-30   id=227      --> vebus
    ##smartsolar mppt 150/85            id=224      --> solarcharger
    ##bluesolar charger mppt 100/50     id=226      --> solarcharger
    ##victronics energysys              id=100      --> system
    
    client = ModbusTcpClient(host, port)
    client.connect()
    ##The tables names are not intuitive.. I think is better to renamed them
    ##Both devices had readings for the PV and their batteries.. 
    ##but is not clear what is the correct table.
    SCPI = [
        ['APEX:CCH:SOLARPOW:BATVOLT', get_battery_voltage, smart_solar_id],
        ['APEX:CCH:SOLARPOW:BATCURR', get_battery_current, smart_solar_id],
        ['APEX:CCH:SOLARPOW:PV_VOLT', get_pv_voltage, smart_solar_id],
        ['APEX:CCH:SOLARPOW:PV_CURR', get_pv_current, smart_solar_id],
        ['APEX:CCH:SOLARPOW:PV_POW', get_pv_power, smart_solar_id],
        ['APEX:CCH:SOLARPOW:SMART_SOLAR_ERROR', get_solar_charger_error, smart_solar_id], #

        ['APEX:CCH:SOLARPOW:COMM_BATVOLT', get_battery_voltage, blue_solar_id],
        ['APEX:CCH:SOLARPOW:COMM_BATCURR', get_battery_current, blue_solar_id],
        ['APEX:CCH:SOLARPOW:COMM_PV_VOLT', get_pv_voltage, blue_solar_id],
        ['APEX:CCH:SOLARPOW:COMM_PV_CURR', get_pv_current, blue_solar_id],
        ['APEX:CCH:SOLARPOW:COMM_PV_POW', get_pv_power, blue_solar_id],
        ['APEX:CCH:SOLARPOW:BLUE_SOLAR_ERROR', get_solar_charger_error, blue_solar_id], #

        ['APEX:CCH:SOLARPOW:INVERTER_DC_V', get_inverter_dc_voltage, multiplus_id],
        ['APEX:CCH:SOLARPOW:INVERTER_DC_A', get_inverter_dc_curr, multiplus_id],
        ['APEX:CCH:SOLARPOW:INVERTER_AC_V', get_inverter_ac_volt, multiplus_id],
        ['APEX:CCH:SOLARPOW:INVERTER_AC_A', get_inverter_ac_curr, multiplus_id],
        ['APEX:CCH:SOLARPOW:INVERTER_AC_FREQ', get_inverter_ac_freq, multiplus_id],
        ['APEX:CCH:SOLARPOW:INVERTER_AC_POW', get_inverter_ac_power, multiplus_id],
        ['APEX:CCH:SOLARPOW:INVERTER_STATE', get_inverter_state, multiplus_id],
        ['APEX:CCH:SOLARPOW:INVERTER_ERROR', get_inverter_error, multiplus_id],
    ]
    while True:
        now = strftime('%Y-%m-%dT%H:%M:%S',localtime(time())) 
        for scpi_cmd in SCPI:
            try:
                ans = scpi_cmd[1](client, scpi_cmd[2])
                print("%s =_cmd[0], %f"%(scpi_cmd[0], ans))
                insertDB(scpi_cmd[0], ans, now)
            except:
                continue
        sleep(refresh_time)
