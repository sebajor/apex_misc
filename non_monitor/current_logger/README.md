
# Current Logger

This project was born since we need several measuring points in the telescope power network to debug huge current spikes that lead to black outs. 

For that I used a raspberry pi pico board that has 3 ADCs that in theory could run up to 500kSa/s. Since we want a stable sampling interval I used a ADC DMA with a round robin scheme and write the buffered data via a serial console.
Since the DMA FIFO connected to the ADC has a size of just 4 samples it generates issues if we use the 3 ADC samples (bcs the channels wil keep shuffling). To solve that I added the 4 channel wich is the temperature sensor, but since I didnt initialize it, it has a near constant value that can be use to verify that the ADC channels are being sampled correctly.

The ADCs are connected to the HTS023R sensor, that returns is an current sensor that returns the sinusoidal signal plus an offset, then being able to digitilize ithe sinusoidal signal plus an offset, then being able to digitilize it right away by the pico.
[We bought these sensors..](https://es.aliexpress.com/item/1005001605989714.html?spm=a2g0o.productlist.main.57.46a5fF7rfF7rvK&algo_pvid=eae983b8-9e70-47f3-98bb-12f84ed92cd6&algo_exp_id=eae983b8-9e70-47f3-98bb-12f84ed92cd6-28&pdp_ext_f=%7B%22order%22%3A%227%22%2C%22eval%22%3A%221%22%7D&pdp_npi=4%40dis%21CLP%2117237%2117237%21%21%2116.66%2116.66%21%402103201917360992344201144ec10c%2112000044490894701%21sea%21CL%212489487147%21X&curPageLogUid=fjyMNkaItpfN&utparam-url=scene%3Asearch%7Cquery_from%3A)

Since we want to store this data, the pico board is connected via a serial to a single board computer that is checking for data in the serial connection (/dev/ttyACM file descriptor) and write it to a file. In principle I want to check the orange pi zero that is a very cheap board.
This computer is connected to a small ups, then if there is power outage we could go and check the collected data.



In principle we have 1024x4 samples and a header that is 0xAABBCCDD, that indicates the begining of a DMA data frame, then we could check the correctness of it (also we could use the temperature channel to check if there is missing data around).
After playing a bit I set the sampling frequency in 2kSa/s in each channel, with that you should have enough samples to make a frequency analysis.

## Building toolflow

To get the pico SDK you need to clone the SDK git repo:
`git clone -b master https://github.com/raspberrypi/pico-sdk.git`

Then you have to move inside the cloned repo and run:
`git submodule update --init`

You need to install the needed packages:
`sudo apt install cmake gcc-arm-none-eabi libnewlib-arm-none-eabi build-essential`

Finally you have to set the enviroment variable (you can add it to the ~/.bashrc file):
`export PICO_SDK_PATH=<where you installed> `

