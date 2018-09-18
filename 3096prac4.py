#!/usr/bin/python
import spidev
from time import sleep
import os
import sys
import RPi.GPIO as GPIO
import time
import datetime
GPIO.setmode(GPIO.BCM)

# connect switches to pins on Rpi
switch_reset = 4
switch_freq = 17
switch_stop = 27
switch_display = 22

#global timer
timer = 0
mins = 0
minApp = ""
item = 0

output = []

# Setup GPIO pins
GPIO.setup(switch_reset, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(switch_freq, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(switch_stop, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(switch_display, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Open SPI bus
spi = spidev.SpiDev() # create spi object
spi.open(0,0)
spi.max_speed_hz=1000000
# RPI has one bus (#0) and two devices (#0 & #1)
# function to read ADC data from a channel

#gets data from ADC
def GetData(channel): # channel must be an integer 0-7
    adc = spi.xfer2([1,(8+channel)<<4,0]) # sending 3 bytes
    data = ((adc[1]&3) << 8) + adc[2]
    return data

# function to convert data to voltage level,
# places: number of decimal places needed

def ConvertVolts(data,places):
    volts = (data * 3.3) / float(1023)
    volts = round(volts,places)
    return volts

def ConvertTemp(volts):
    temp = (volts - 0.5)*100
    return round(temp,2)

# Define sensor channels
channel = 2

# Define delay between readings
#global delay
delay = .5

def resetCall(channel):
    print("resetCall")
    #for i in range(50):
    print("\n" * 50)
    global timer
    timer = 0
    #print(timer)

def freqCall(channel):
    print("freqCall")
    global delay
    delay += 0.5
    if delay == 1.5:
        delay = 2
    if delay > 2:
        delay = 0.5
    print(delay)

isReading = True

#lookrandomedit

def stopCall(channel):
    print("stopCall")
    global isReading
    isReading = not isReading
    global output
    #output = []
    global item
    item = 0
    

def dispCall(channel):
    print("____________________________________________")
    print("Time     | Timer      | Pot  | Temp  | Light")
   
    global output
    
    if len(output) >= 5:
        for i in range(0,5):
            print(output[i])
    else:
        for i in output:
            print(i)
    output = []

GPIO.add_event_detect(switch_reset,GPIO.FALLING,callback=resetCall,bouncetime=200)
GPIO.add_event_detect(switch_freq,GPIO.FALLING,callback=freqCall,bouncetime=200)
GPIO.add_event_detect(switch_stop,GPIO.FALLING,callback=stopCall,bouncetime=200)
GPIO.add_event_detect(switch_display,GPIO.FALLING,callback=dispCall,bouncetime=200)

def convToLight(volts):
    maxV = 3
    percent = (volts/maxV)*100
    return round(percent,2)

print("______________________________________________")
print("Time     | Timer      | Pot    | Temp  | Light")
try:
    while True:
         # Read the data
         
         
        if timer > 59.5:
            timer = 0
            mins += 1

        if isReading:
            sensor_data_pot = GetData (0)
            sensor_volt_pot = ConvertVolts(sensor_data_pot,2)
            
            sensor_data_LDR = GetData (1)
            sensor_LDR = convToLight(ConvertVolts(sensor_data_LDR,2))

            sensor_data_temp = GetData (2)
            sensor_temp = ConvertTemp(ConvertVolts(sensor_data_temp,2))

            ts = time.time()
            st = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S') #%Y-%m-%d
            
            timeAppend = "00:"+ str(mins).zfill(2)+":"+str(timer).zfill(4) 
            appendStr = st + " | " +timeAppend+" | "+str(sensor_volt_pot)+"V | "+str(sensor_temp)+"C | "+str(sensor_LDR)+"%"
            print(appendStr)
            output.append(appendStr)

            #print(output[item])
            item += 1
        
        sleep(delay)
                      
        timer += delay


except KeyboardInterrupt:
    spi.close()
