"""
A small script that uses the adafruit_bme680 library to get sensor data from a single bme680.
Stanford Student Space Initiative - Biopolymer Research for In-situ Construction
Written by Leo Glikbarg
"""
import board
import adafruit_bme680
import time
import sys


def run(speed = 2.0):
    """"gets data from a single bme680 at a specified speed (Hz)"""
    # check that speed param is valid
    speed = float(speed)
    if speed <= 0.0:
        speed = 2.0
    # init I2C comms with BME680
    i2c = board.I2C()
    sensor = adafruit_bme680.Adafruit_BME680_I2C(i2c)
    print("\nType \'ctrl-c\' at any time to end the program.\n")
    time.sleep(5)
    while True:
        get_data()
        time.sleep(1.0/float(speed))


def get_data():
    """print all available data from the bme680"""
    print('Temperature: {} degrees C'.format(sensor.temperature))
    print('Gas: {} ohms'.format(sensor.gas))
    print('Humidity: {}%'.format(sensor.humidity))
    print('Pressure: {}hPa'.format(sensor.pressure))


def prompt():
    """"ask the user what they would like to do, and return their response"""
    print("\nWould you like to get_data the servo?\nType \'stop\' to end the program.\n")
    return input("")


if __name__ == "__main__":
    """starts the run() method. Read the run() docstring for more information"""
    if len(sys.argv) > 1:
        run(sys.argv[1])
    else:
        run()