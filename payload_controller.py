""" 
Stanford Student Space Initiative
Written by: Leo Glikbarg 

This file contains the Payload class. Payload is a controller for configuring and interacting with the hardware.
"""
import time
import logging
import threading
import sys
import os
import RPi.GPIO as GPIO
import bme680

class Payload:
    def __init__(self, sensor_speed, ports):
        """initializes class fields and begins logging"""
        self.active = False # sensor thread control flag
        self.servo_ports = ports # servo gpio hardware ports
        self.servos = {}

        # setup loggers and data collection
        self.status = self.configure_logger("status", ("{time}_status.log").format(time = str(time.time())))
        self.data = self.configure_logger("data", ("{time}_data.log").format(time = str(time.time())))
        self.status.info("loggers configured")
        self.sensor = ''
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


    def get_humidity(self):
        """get the sensed humidty from the humidity sensor and return the value"""
        hum = self.sensor.data.humidity
        self.data.debug(("humidity: {humidity} %RH").format(humidity=hum))
        return hum


    def get_temperature(self):
        """get the sensed temperature  from the temperature sensor and return the value"""
        temp = self.sensor.data.temperature
        self.data.debug(("temperature: {temperature} C").format(temperature=temp))
        return temp


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
        # create a logger, add handlers/formatters
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        logger.addHandler(fileHandler)
        logger.addHandler(consoleHandler)
        return logger


    def log_sense(self, wait):
        """Log the temp and humidity sense data to a file every {wait}s"""
        self.status.info("sensor data collection started")
        self.active = True
        # configure sensor
        try:
            self.sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
        except (RuntimeError, IOError):
            self.sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)
        # oversampling settings that trade noise vs accuracy
        self.sensor.set_humidity_oversample(bme680.OS_2X)
        self.sensor.set_pressure_oversample(bme680.OS_4X)
        self.sensor.set_temperature_oversample(bme680.OS_8X)
        self.sensor.set_filter(bme680.FILTER_SIZE_3)
        while self.active:
            # if there is new data, get it
            if self.sensor.get_sensor_data():
                self.get_humidity()
                self.get_temperature()
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

