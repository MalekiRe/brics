""" 
Stanford Student Space Initiative
Written by: Leo Glikbarg 

This file contains the Payload class. Payload is a controller for configuring and interacting with the hardware.
"""
from datetime import datetime
import time
import logging
import threading
import sys
import os
import RPi.GPIO as GPIO
import bme680
import smbus

MULTIPLEXER_I2C_ADDR = 0x70 # this is defined by hardware for TCA9548As
MULTIPLEXER_CHANNEL_ARRAY = [0b00000001,0b00000010,0b00000100,0b00001000,0b00010000,0b00100000,0b01000000,0b10000000]

class Payload:
    def __init__(self, sensor_speed, ports, sensor_num):
        """initializes class fields and begins logging"""
        self.active = False # sensor thread control flag
        self.servo_ports = ports # servo gpio hardware ports
        self.servos = {}
        self.sensor_count = sensor_num

        # setup loggers and data collection
        self.status = self.configure_logger("status", ("{time}_status.log").format(time = str(datetime.now())))
        self.data = self.configure_logger("data", ("{time}_data.log").format(time = str(datetime.now())))
        self.status.info("loggers configured")
        self.bus = "" # I2C adress bus that sensor are located on
        self.sensors = []
        self.sense_thread = threading.Thread(target=self.log_sense, args=(sensor_speed,))
        self.sense_thread.start()


    def secure_sleep(self, sleep_length):
        """A wrapper for time.sleep to make it more reliable/accurate"""
        start = time.time()
        gap_time = time.time() - start
        while (gap_time < sleep_length):
            if gap_time < 60:
                time.sleep(gap_time)
            else:
                time.sleep(60) # repeatedly uses time.sleep for 60s then reassesses the sitation
            gap_time = time.time() - start


    def get_humidity(self, device):
        """get the sensed humidty from the humidity sensor and return the value"""
        try:
            self.sensors[device].get_sensor_data()
            hum = self.sensors[device].data.humidity
            self.data.debug(("sensor {sense_num} humidity: {humidity} %RH").format(sense_num=device, humidity=hum))
            return hum
        except:
            self.data.debug(("sensor {sense_num} humidity: ERROR %RH").format(sense_num=device))
            return None


    def get_temperature(self, device):
        """get the sensed temperature  from the temperature sensor and return the value"""
        try:
            self.sensors[device].get_sensor_data()
            temp = self.sensors[device].data.temperature
            self.data.debug(("sensor {sense_num} temperature: {temperature} C").format(sense_num=device, temperature=temp))
            return temp
        except:
            self.data.debug(("sensor {sense_num} temperature: ERROR C").format(sense_num=device))
            return None


    def open_valve(self, servo):
        """actuate a servo to open a pinch valve"""
        self.status.info(("attempting to open valve {valve_id}").format(valve_id=servo))
        self.servos[servo]["instance"].ChangeDutyCycle(9.5) # valve opening
        self.secure_sleep(2) # wait for valve to complete movement
        self.servos[servo]["instance"].ChangeDutyCycle(0.0) # stop valve movement
        self.secure_sleep(1.5) # wait for valve to fully stop
        self.status.info(("valve {valve_id} open").format(valve_id=servo))


    def close_valve(self, servo):
        """actuate a servo to close a pinch valve"""
        self.status.info(("attempting to close valve {valve_id}").format(valve_id=servo))
        self.servos[servo]["instance"].ChangeDutyCycle(5.0) # valve closing
        self.secure_sleep(2) # wait for valve to complete movement
        self.servos[servo]["instance"].ChangeDutyCycle(0.0) # stop valve movement
        self.secure_sleep(1.5) # wait for valve to fully stop
        self.status.info(("valve {valve_id} closed").format(valve_id=servo))


    def configure_logger(self, logger_name, file_name):
        """configure a logger to record the timestamped info to a log file"""
        # set up formatters and handlers
        logFormatter = logging.Formatter("[%(asctime)s] [%(name)s] %(message)s")
        fileHandler = logging.FileHandler(file_name)
        consoleHandler = logging.StreamHandler()
        fileHandler.setFormatter(logFormatter)
        consoleHandler.setFormatter(logFormatter)
        fileHandler.setLevel(logging.DEBUG)
        consoleHandler.setLevel(logging.INFO)
        # create a logger, add handlers/formatters
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(fileHandler)
        logger.addHandler(consoleHandler)
        return logger


    def change_multiplexer_channel(self, channel):
        """change which channel is active on the i2c multiplexer"""
        self.bus.write_byte(MULTIPLEXER_I2C_ADDR, MULTIPLEXER_CHANNEL_ARRAY[channel]) # 0x70 is defined by hardware to be the multiplexer's I2C adress


    def log_sense(self, wait):
        """Log the temp and humidity sense data to a file every {wait}s"""
        self.status.info("sensor data collection started")
        self.active = True
        self.bus = smbus.SMBus(1)
        for device in range(self.sensor_count):
            sensor = ''
            self.change_multiplexer_channel(device)
            # configure sensor
            try:
                try:
                    sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
                except (RuntimeError, IOError):
                    sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)
                # oversampling settings that trade noise vs accuracy
                sensor.set_humidity_oversample(bme680.OS_2X)
                sensor.set_pressure_oversample(bme680.OS_4X)
                sensor.set_temperature_oversample(bme680.OS_8X)
                sensor.set_filter(bme680.FILTER_SIZE_3)
                self.sensors.append(sensor)
            except:
                self.sensors.append("No sensor connected")
        while self.active:
            # if there is new data, get it
            for device in range(self.sensor_count):
                self.change_multiplexer_channel(device)
                self.secure_sleep(0.1)
                self.get_humidity(device)
                self.get_temperature(device)
            self.secure_sleep(wait)
        self.status.info("sensor data collection ended")


    def cleanup_gpio(self):
        """cleans up the GPIO connections to the servo"""
        GPIO.cleanup()


    def configure_servos(self, servo_pair_num):
        """create a number of paired servo objects with specific adresses and set them to be closed"""
        GPIO.setmode(GPIO.BCM)
        for pair in range(1, servo_pair_num + 1):
            # generate name
            servo_name_a = ("{num}a").format(num=pair)
            servo_name_b = ("{num}b").format(num=pair)
            # generate pwm channel number
            servo_channel_a = self.servo_ports[(pair - 1) * 2]
            servo_channel_b = self.servo_ports[((pair - 1) * 2) + 1]
            # initialize gpio pins and servos
            GPIO.setup(servo_channel_a, GPIO.OUT)
            servo_a = GPIO.PWM(servo_channel_a, 50)
            servo_a.start(0)
            GPIO.setup(servo_channel_b, GPIO.OUT)
            servo_b = GPIO.PWM(servo_channel_b, 50)
            servo_b.start(0)
            # add to servos dict
            self.servos[servo_name_a] = {"channel": servo_channel_a, "instance": servo_a}
            self.servos[servo_name_b] = {"channel": servo_channel_b, "instance": servo_b}
            # start servos as closed
            self.close_valve(servo_name_a)
            self.close_valve(servo_name_b)

