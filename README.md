# apex_misc
Miscellaneous codes used in apex (mostly monitoring sensors).

I made this repo only because there is a lack of documentation on the some monitoring points in APEX.. I only put here codes that I have worked with, since I already have to decipher them.


The monitor system is quite easy, there is a main computer that is running several codes that queries values to all the sensors in the APEX telescope and insert them in a database. In another machine the monitoring system runs, reading from the former database, comparing the results with some threshold values and generating an alarm if the thresholds were traspased.

BTW: I change all the credentials and passwords to bullshit, so you would need to correct that if you want to use the codes (this should be stored in one .env variables or something like that to avoid this... but whatever)


## About the Monitoring system
In all the codes there is a line that imports a common.py script.. In that scripts are the credentials and the functions to insert data in the monitoring database.
For reasons that I dont quite understand, each monitoring point have (among several other fields): 
    - an ID that is a number
    - an associated SCPI command (that is the actual thing that all the python codes have to identify the points)
    - a NAME that is deploy in the monitoring web page
    - a LOC wich is the tab in the webpage where the point will appear (eg: sequitor, cerro chico, etc... but in the Database the actual names are different than the one used in the web page, so you have to check for the right ones)

Even if in the codes the SCPI command is stated, when calling the insertdB function the function will check the database points that have the same SCPI command and use the ID to make the insertion. Also the monitor webpage doesnt show the SCPI command so the way to look for the actual item is also with the ID (that is hidden, to get it you have to place the mouse in the histogram symbol near the monitor point and it will display the ID)
For those reasons its a pain in the ass generate a new monitoring point.. And if you make a mistake its also a pain to modify the fields.. For that reason I created the python code that does the job to check for free IDs and creates a monitor point.


## About some lantronix-modbus conversion
There are several devices that dont work with ethernet modbus. Then to put them into the network a lantronix is placed, the caveat is that the lantronix only generates a media change and then the message that you send to the lantronix should have the modbus format (ie the headers, checksums and all the stuffs inherent to the modbus protocol) even if you are sending a socket message.. So when you see that the modbus python library is being used to generated headers and/or checksums is because of that. 
This also means that you need to parse the answers using the bare modbus protocol.

## About PLCs and MANGO
MANGO is a platform that allows you to interface several devices.. it supports several communication protocols, but is a damn nightmare to debug since there is no feedback and you have to guess what is going on.. 
To make the situation worst, the PLCs only allows one modbus client (as far as I understand, maybe Im wrong...). Since MANGO is the prefered option to control the devices in the APEX system then you have to ask MANGO for the data points in the PLCs that it interface. 


