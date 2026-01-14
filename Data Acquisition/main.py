#!/usr/bin/python
# -*- coding:utf-8 -*-


import time
import ADS1256
import RPi.GPIO as GPIO


try:
    ADC = ADS1256.ADS1256()
    ADC.ADS1256_init()
    counter = 0
    start_time = time.perf_counter()
    new_value = 0
    while(1):
        
        counter+=1
        
        ADC_Value = ADC.ADS1256_GetAll()
        
        new_value = ADC_Value[0]*5.0/0x7fffff
        if counter % 5000 == 0:
            current_time = time.perf_counter() - start_time
        # SPS (örnekleme hızı) hesaplama
            sps = counter / current_time
            print(f"SPS (Samples Per Second): {sps:.2f} Hz\n")
            print ("\33[4A")
        

        
except :
    GPIO.cleanup()
    print ("\r\nProgram end     ")
    exit()
