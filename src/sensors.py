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
from datetime import datetime

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
    x = datetime.now()
    print(x.strftime('%c'))

    # init I2C comms with BME680
    bus = smbus.SMBus(1)

    print("Connecting to i2c...")
    i2c = board.I2C()
    time.sleep(0.5)

    print("Changing multiplexers...")
    change_multiplex_bus(bus, 0)
    time.sleep(0.5)

    print("Initializing sensors...")
    sensor = adafruit_bme680.Adafruit_BME680_I2C(i2c)
    time.sleep(5)
    print("Praying to a god of our choosing...")

    print("-"*8)
    get_data(sensor, bus)

def change_multiplex_bus(bus, channel):
    bus.write_byte(MULTIPLEXER_I2C_ADDR, MULTIPLEXER_CHANNEL_ARRAY[channel])

def get_data(sensor, bus):
    """print all available data from the bme680"""
    for i in range(3):
        change_multiplex_bus(bus, i)
        print("Getting info from sensor: " + str(i))
        print('Temperature: {} degrees C'.format(sensor.temperature))
        print('Gas: {} ohms'.format(sensor.gas))
        print('Humidity: {}%'.format(sensor.humidity))
        print('Pressure: {}hPa'.format(sensor.pressure))
        print("-"*8)
   
if __name__ == "__main__":
    """starts the run() method. Read the run() docstring for more information"""
    run()
