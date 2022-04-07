"""
A small script that uses the adafruit_bme680 library to get sensor data from a single bme680.
This file is run every minute via cron. To change the frequency use crontab

Stanford Student Space Initiative - Biopolymer Research for In-situ Construction
"""
import board
import adafruit_bme680
import time
import sys
import smbus
import os
from datetime import datetime

# Screencode libraries
from RPLCD import i2c
from time import sleep
from collections import deque

# Constants to initialise the LCD
lcdmode = 'i2c'
cols = 20
rows = 4
charmap = 'A00'
i2c_expander = 'PCF8574'

# Generally 27 is the address;Find yours using: i2cdetect -y 1 
address = 0x27 
port = 1 # 0 on an older Raspberry Pi

# Initialise the LCD
lcd = i2c.CharLCD(i2c_expander, address, port=port, charmap=charmap,
                  cols=cols, rows=rows)

# Switch on  backlight
lcd.backlight_enabled = True

# Returns the last n lines of a file
def tail(filename, n):
    with open(filename) as f:
        return deque(f, n)

endoffile = tail('../log/sensor.log',5)

# Writes string onto screen
def printinfo():
    for i in endoffile:
        if '-' in i:
            continue
        lcd.write_string(i)
        lcd.crlf()

#TODO: change run frequency via crontab

MULTIPLEXER_I2C_ADDR = 0x70
MULTIPLEXER_CHANNEL_ARRAY = [0b00000001, 0b00000010, 0b00000100]

LOGFILE = "/home/pi/brics/log/sensor.log"

def run(log=True):
    # redirects print statement to LOGFILE
    if log:
        f = open(LOGFILE, 'a')
        sys.stdout = f
    print()

    # log time
    x = os.popen('uptime -p').read()[:-1]
    print(x)

    # init I2C comms with BME680
    bus = smbus.SMBus(1)

    print("Connecting to i2c...")
    i2c = board.I2C()
    time.sleep(0.5)

    print("Changing multiplexers...")
    change_multiplex_bus(bus, 1)
    time.sleep(0.5)

    print("Initializing sensors...")
    sensor = adafruit_bme680.Adafruit_BME680_I2C(i2c, address = 0x77)
    time.sleep(5)
    print("Praying to a god of our choosing...")

    print("-"*8)
    get_data(sensor, bus)

def change_multiplex_bus(bus, channel):
    bus.write_byte(MULTIPLEXER_I2C_ADDR, MULTIPLEXER_CHANNEL_ARRAY[channel])

def get_data(sensor, bus):
    """print all available data from the bme680"""
    for i in range(1):
        #change_multiplex_bus(bus, i)
        print("Getting info from sensor: " + str(i))
        print('Temp: {} C'.format(round(sensor.temperature, 3)))
        print('Gas: {} ohms'.format(round(sensor.gas, 3)))
        print('Hum: {}%'.format(round(sensor.humidity, 3)))
        print('Press: {}hPa'.format(round(sensor.pressure, 3)))
        print("-"*8)
   
if __name__ == "__main__":
    """starts the run() method. Read the run() docstring for more information"""
    run()
    printinfo()
