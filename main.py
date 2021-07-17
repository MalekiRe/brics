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

active = True

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


def open_valve(num, status):
    """actuate a servo to open a pinch valve"""
    status.info(("attempting to open valve {valve_id}").format(valve_id=num))
    # TODO implement
    status.info(("valve {valve_id} opened").format(valve_id=num))
    pass


def close_valve(num, status):
    """actuate a servo to close a pinch valve"""
    status.info(("attempting to close valve {valve_id}").format(valve_id=num))
    # TODO implement
    status.info(("valve {valve_id} closed").format(valve_id=num))
    pass


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
        time.sleep(wait)
    status.info("sensor data collection ended")


def run(servo_num, sense_report_time, test_start_time, test_gap_time):
    """periodically actuate servos to open/close valves and log sensor data"""
    # setup loggers and data collection
    global active
    status = configure_logger("status", "status.log")
    data = configure_logger("data", "data.log")
    status.info("loggers configured")
    sense_thread  = threading.Thread(target=log_sense, args=(30, status, data))
    sense_thread.start()
    # active testing
    status.info(("waiting {start_wait}s before beginning valve movement").format(start_wait=test_start_time))
    time.sleep(test_start_time)
    for servo in range(servo_num):
        open_valve(servo, status)
        if servo != servo_num - 1:
            time.sleep(test_gap_time)
            status.info(("waiting {gap_time}s before starting the next test").format(gap_time=test_gap_time))
    # cleanup
    status.info("active testing done, data logging will continue")
    active = False
    sense_thread.join()


if __name__ == "__main__":
    """calls run() either with default args or command lind args"""
    if len(sys.argv) == 5:
        run(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        run(3, 4, 5, 6)
{"mode":"full","isActive":false}