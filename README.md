# apex_misc
Miscellaneous codes used in apex (mostly monitoring sensors).

I made this repo only because there is a lack of documentation on the some monitoring points in APEX.. I only put here codes that I have worked with, since I already have to decipher them.


The monitor system is quite easy, there is a main computer that is running several codes that queries values to all the sensors in the APEX telescope and insert them in a database. In another machine the monitoring system runs, reading from the former database, comparing the results with some threshold values and generating an alarm if the thresholds were traspased.
