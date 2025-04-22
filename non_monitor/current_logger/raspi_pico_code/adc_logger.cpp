#include <stdio.h>
#include <stdint.h>
#include "pico/stdlib.h"
#include "hardware/adc.h"
#include "hardware/dma.h"

/*
 *  The idea is to follow the template in https://github.com/vha3/Hunter-Adams-RP2040-Demos/blob/master/Audio/f_Audio_FFT/fft.c
 *  I never understood why they use 2 DMA channels (one DMA to get the ADC data and the second
 *  to reset the ADC channel) I just write the address by hand with the pointers.
 *
 *  In this code I create 2 DMA channels for the ADC, when one is full I start the second channel
 *  while I read the first one.
 *  With this scheme I got good results.
 *
 */

constexpr int samples = 1024;//128;
constexpr int n_adcs = 4;
const float ADCCLK = 48000000;
const float ADC_FS = 2000;  //with 1000 I got 750Hz of fs
//const float ADC_FS = 3000; 


const float conversion_factor = 3.3f/(256);    //factor to convert to voltage

uint8_t capture_buffer0[n_adcs*samples];
uint8_t capture_buffer1[n_adcs*samples];
uint8_t* capture_buffer0_pointer = &capture_buffer0[0];
uint8_t* capture_buffer1_pointer = &capture_buffer1[0];

uint8_t adc0_data[samples];
uint8_t adc1_data[samples];
uint8_t adc2_data[samples];

void adc_round_robin_config(){
    //initialize the ADC pins 
    for(int i=0; i<n_adcs; ++i){
        adc_gpio_init(26+i);
    }
    adc_select_input(0);
    adc_init();

    //set the bitmask to select the ADCs to use in the DMA
    adc_set_round_robin((1<<(n_adcs))-1);

    adc_fifo_setup(
        1,          //write each completed conversion ot the fifo
        1,          //enable DMA data request (DREQ)
        1,          //DREQ and IRQ asserted when there is at least 1 sample available
        0,          //you can use the last bit of the ADC to check correctness, we dont care and leave that option off
        1           //shift each sample when pushing to FIFO (to have 8 bits samples)
    );
    adc_set_clkdiv(static_cast<float>(ADCCLK/ADC_FS/n_adcs)); 
}


int main(){
    //start the serial communication
    stdio_init_all();

    char msg {};
    adc_round_robin_config();
    sleep_ms(3000);

    //set data dma, read from cte address writting in increasing way
    int data_dma0 = dma_claim_unused_channel(1);
    dma_channel_config conf_data_dma0 = dma_channel_get_default_config(data_dma0);
    channel_config_set_transfer_data_size(&conf_data_dma0, DMA_SIZE_8);
    channel_config_set_read_increment(&conf_data_dma0, 0);
    channel_config_set_write_increment(&conf_data_dma0, 1); 
    //set the data request based on the availability of ADC samples
    channel_config_set_dreq(&conf_data_dma0, DREQ_ADC);
    
    dma_channel_configure(
        data_dma0,
        &conf_data_dma0,     //configuration struct
        capture_buffer0,     //dest
        &adc_hw->fifo,      //src
        4*samples,          //number of samples
        0                   //dont start right away
    );


    int data_dma1 = dma_claim_unused_channel(1);
    dma_channel_config conf_data_dma1 = dma_channel_get_default_config(data_dma1);
    channel_config_set_transfer_data_size(&conf_data_dma1, DMA_SIZE_8);
    channel_config_set_read_increment(&conf_data_dma1, 0);
    channel_config_set_write_increment(&conf_data_dma1, 1); 
    //set the data request based on the availability of ADC samples
    channel_config_set_dreq(&conf_data_dma1, DREQ_ADC);
    
    dma_channel_configure(
        data_dma1,
        &conf_data_dma1,     //configuration struct
        capture_buffer1,     //dest
        &adc_hw->fifo,      //src
        4*samples,          //number of samples
        0                   //dont start right away
    );


    //here I will wait until got a signal from the usb connection
    msg =getchar(); //this is blocking right?
    
    //start adc
    dma_channel_start(data_dma0);
    adc_run(1);
    while(1){
        dma_channel_wait_for_finish_blocking(data_dma0);
        adc_fifo_drain(); 
        adc_select_input(0);  
        dma_channel_start(data_dma1);
        //print while the other dma channel is taking data
        printf("%c%c%c%c", 0xaa,0xbb, 0xcc, 0xdd);
        fwrite(capture_buffer0, 1, n_adcs*samples, stdout);
        //reset the DMA0 channel
        dma_hw->ch[data_dma0].write_addr = (long int)capture_buffer0_pointer;
         
        //wait until the DMA2 is done
        dma_channel_wait_for_finish_blocking(data_dma1);
        adc_fifo_drain();
        adc_select_input(0);
        dma_channel_start(data_dma0);
        //print while the other dma channel is taking data
        printf("%c%c%c%c", 0xaa,0xbb, 0xcc, 0xdd);
        fwrite(capture_buffer1, 1, n_adcs*samples, stdout);
        dma_hw->ch[data_dma1].write_addr = (long int)capture_buffer1_pointer;

    }
}

//BTW if we want a real-time analysis we could have done it instead of just broadcasting the
//data to a computer to save it... but I have no idea how much spare time the pico has between the 
//DMA reads, but my first guess is that printing out the data is the most expensive task
