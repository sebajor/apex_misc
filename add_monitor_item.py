from   string   import *
import MySQLdb
import logging
import sys

###
### Code to add a monitoring point easilly
###


##
##
#ID=  This one is given by the last id available in the table
###Parameters to fill.. Some of this parameters will determine where is located in the monitor webpage
params = {}
params["ITEM"]= "INVERTER_ERROR_CODE"
params["SENSING"]= "ERROR CODE"          ##THIS ARE THE UNITS!
params["NAME"]="INVERTER ERROR CODE"
params["SCPI"]="APEX:CCH:SOLARPOW:INVERTER_ERROR"

params["LOC"]="CH"                  ###THIS ONE SETS THE TAB WHERE THE DATA APPEARS IN THE WEBPAGE (eg: CH for cerro chico, PH for powerhouse, etc
params["SYSTEM"]= "CCH"             ##CCH, PGEN
params["SUBSYSTEM"]= "SOLARPOW"     ##TO GROUP INFO IN THE WEBPAGE
params["COMMENT"]=""
params["WBS_AREA"]= ""
params["WBS_SYSTEM"]= ""
params["WBS_SUBSYSTEM"] = ""
params["script_name"] = "CerroChicoMon.py"  
###
### Bullshit that can be set after 
params["MIN"]=0
params["MAX"]=8
params["GAP"]=2
params["FREQ"]=0
params["REL"]=0
params["ACTIVE"]=0
params["ALARM"]=0
params["SIG"]=0
params["ANN"]=0
params["VALUE"]=0
params["STATE"]=0
params["TIMESTAMP"]="2024-06-05 16:08:21" ##whatever I just want to create the new one
params["EQUIPMENT"]="0"
params["PORT"]="0"

def myConn():
  HOST="FAKE_HOST"
  USER="FAKE_USER"
  PASSWD="FAKE_PASS"
  conn = MySQLdb.connect (host = HOST,
                           user = USER,
                           passwd = PASSWD,
                           db = "FAKE_DB")
  return conn



###
conn = myConn()
cursor = conn.cursor ()
query = "select max(ID) from monItems;"
cursor.execute (query)
row = cursor.fetchone()
if(row is None):
  sys.exit()
available_id = row[0]+1
params["ID"] = available_id

msg = "insert into monItems ("
values = "("

for key, item in params.items():
  msg+="%s,"%str(key)
  values+="'%s',"%str(item)

query = msg[:-1]+") values "+values[:-1]+");"
print(query)
cursor.execute(query)  








