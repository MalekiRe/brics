""" 
Stanford Student Space Initiative
Written by: Leo Glikbarg, 

This file contains code that should be run by the Raspberry Pi when it is powered on. Read run() for more information.
"""
import time
import logging
import threading
import sys
import os
import RPi.GPIO as GPIO

active = True
servo_ports = [4, 17, 18, 19, 20, 21]

def secure_sleep(sleep_length):
    """A wrapper for time.sleep to make it more reliable/accurate"""
    start = time.time()
    gap_time = time.time() - start
    while (gap_time < sleep_length):
        if gap_time < 60:
            time.sleep(gap_time)
        else:
            time.sleep(10)
        gap_time = time.time() - start


def get_humidity(data):
    """get the sensed humidty from the humidity sensor and return the value"""
    # TODO implement
    hum = 0
    data.info(("humidity: {humidity}").format(humidity=hum))
    return hum

def get_temperature(data):
    """get the sensed temperature  from the temperature sensor and return the value"""
    # TODO implement
    temp = 0
    data.info(("temperature: {temperature}").format(temperature=temp))
    return temp


def open_valve(servo, status):
    """actuate a servo to open a pinch valve"""
    status.info(("attempting to open valve {valve_id}").format(valve_id=servo))
    servos[servo]["instance"].ChangeDutyCycle(9.5) # valve opening
    secure_sleep(2) # wait for valve to complete movement
    servos[servo]["instance"].ChangeDutyCycle(0.0) # stop valve movement
    secure_sleep(1.5) # wait for valve to fully stop
    status.info(("valve {valve_id} open").format(valve_id=servo))


def close_valve(servo, status):
    """actuate a servo to close a pinch valve"""
    status.info(("attempting to close valve {valve_id}").format(valve_id=servo))
    servos[servo]["instance"].ChangeDutyCycle(5.0) # valve closing
    secure_sleep(2) # wait for valve to complete movement
    servos[servo]["instance"].ChangeDutyCycle(0.0) # stop valve movement
    secure_sleep(1.5) # wait for valve to fully stop
    status.info(("valve {valve_id} closed").format(valve_id=servo))


def remove_old_log(name):
    """if stale logs with a certain name exist, delete them"""
    if os.path.isfile(name):
        os.system(("echo Brics! | sudo rm -f {file}").format(file=name))


def configure_logger(logger_name, file_name):
    """configure a logger to record the timestamped info to a log file"""
    remove_old_log(file_name)
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


def log_sense(wait, status, data):
    """Log the temp and humidity sense data to a file every {wait}s"""
    status.info("sensor data collection started")
    global active
    while active:
        humidity_reading = get_humidity(data)
        temperature_reading = get_temperature(data)
        status.info(("waiting {wait_time}s before recording more sensor data").format(wait_time=wait))
        secure_sleep(wait)
    status.info("sensor data collection ended")


def configure_servos(servo_pair_num, status):
    """create a number of paired servo objects with specific adresses and set them to be closed"""
    global servos
    servos = {}
    GPIO.setmode(GPIO.BCM)
    for pair in range(1, servo_pair_num + 1):
        # generate name
        servo_name_a = ("{num}a").format(num=pair)
        servo_name_b = ("{num}b").format(num=pair)
        # generate pwm channel number
        servo_channel_a = servo_ports[(pair - 1) * 2]
        servo_channel_b = servo_ports[((pair - 1) * 2) + 1]
        # initialize gpio pins
        status.info(("servo {name} will is using port {port}").format(name=servo_name_a, port=servo_channel_a))
        GPIO.setup(servo_channel_a, GPIO.OUT)
	servo_a = GPIO.PWM(servo_channel_a, 50)
        servo_a.start(0)
        GPIO.setup(servo_channel_b, GPIO.OUT)
	servo_b = GPIO.PWM(servo_channel_b, 50)
        servo_b.start(0)
        # add to servos dict
        servos[servo_name_a] = {"channel": servo_channel_a, "instance": servo_a}
        servos[servo_name_b] = {"channel": servo_channel_b, "instance": servo_b}
        # start servos as closed
        close_valve(servo_name_a, status)
        close_valve(servo_name_b, status)


def run(sense_report_time, test_start_time, short_gap_time, long_gap_time, test_end_time):
    """periodically actuate servos to open/close valves and log sensor data"""
    # setup loggers and data collection
    global active
    status = configure_logger("status", "status.log")
    data = configure_logger("data", "data.log")
    status.info("loggers configured")
    try:
        sense_thread  = threading.Thread(target=log_sense, args=(sense_report_time, status, data))
        sense_thread.start()
        servo_pair_num = int((len(servo_ports)/2))
        configure_servos(servo_pair_num, status)
        status.info("servos configured")
        # active testing
        status.info(("waiting {start_wait} minutes before beginning first valve movement").format(start_wait=float(test_start_time)/60.0))
        secure_sleep(test_start_time)
        for pair_num in range(1, servo_pair_num + 1):
            open_valve(("{num}a").format(num=pair_num), status)
            secure_sleep(short_gap_time)
            status.info(("waiting {gap_time}s before moving on").format(gap_time=short_gap_time))
            open_valve(("{num}b").format(num=pair_num), status)
            secure_sleep(long_gap_time)
            status.info(("waiting {gap_time} hours before moving on").format(gap_time=float(short_gap_time)/3600.0))
        # cleanup
        status.info(("active testing done, data logging will continue for {end_time}hours").format(end_time=float(test_end_time)/3600.0))
        secure_sleep(test_end_time)
        active = False
        sense_thread.join()
        GPIO.cleanup()
    except Exception and KeyboardInterrupt as e:
        status.info(("ERROR: {err}").format(err=e))
	GPIO.cleanup()
        active=False
	sense_thread.join()


if __name__ == "__main__":
    """calls run() either with default args or command lind args"""
    if len(sys.argv) == 5:
        run(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        # dev: 1hz sensor spped 15s, 10s, 20s, 12s
        # flight: 1hz sensor speed, 1 hour, 10s, 48 hours, 120 hours
        run(1, 15, 10, 20, 12)
