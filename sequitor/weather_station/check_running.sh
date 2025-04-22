#!/bin/bash

#Code inside the raspberry pi that checks that the code is change media code is running.
cmd='/home/apex/weather_media_change.py'
if [[ $(pgrep python -a) = *$cmd* ]]; then
	echo "program already running\n"
else
	python /home/apex/weather_media_change.py &
fi
