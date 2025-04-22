# apex_misc
Miscellaneous codes used in apex (mostly monitoring sensors).

I made this repo only because there is a lack of documentation on the some monitoring points in APEX.. I only put here codes that I have worked with, since I already have to decipher them.


The monitor system is quite easy, there is a main computer that is running several codes that queries values to all the sensors in the APEX telescope and insert them in a database. In another machine the monitoring system runs, reading from the former database, comparing the results with some threshold values and generating an alarm if the thresholds were traspased.


## About some lantronix-modbus conversion
There are several devices that dont work with ethernet modbus. Then to put them into the network a lantronix is placed, the caveat is that the lantronix only generates a media change and then the message that you send to the lantronix should have the modbus format (ie the headers, checksums and all the stuffs inherent to the modbus protocol) even if you are sending a socket message.. So when you see that the modbus python library is being used to generated headers and/or checksums is because of that. 
This also means that you need to parse the answers using the bare modbus protocol.
