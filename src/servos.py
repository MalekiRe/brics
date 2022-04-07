from datetime import datetime
import time
import sys
import RPi.GPIO as GPIO

PORTS = [14, 15, 4, 23 ,17, 27]

LOGFILE = "/home/pi/brics/log/servos.log"

# TODO: change these
EXP_WAIT_TIME = 1 # 5 days
INTRA_WAIT_TIME = 10 # 10 seconds
INTER_WAIT_TIME = 60 # 5 days

NUM_VALVES = 3
servos = {}

def configure_servos(num_valves):
    GPIO.setmode(GPIO.BCM)

    for pair in range(num_valves):
        for i in range(2):
            if i == 0:
                name = ("{num}A").format(num=pair)
            else: 
                name = ("{num}B").format(num=pair)
            channel = PORTS[pair * 2 + i]

            GPIO.setup(channel, GPIO.OUT)
            servo = GPIO.PWM(channel, 50)
            servo.start(0)

            servos[name] = {"channel": channel, "instance": servo}
            #close_valve(name)

def open_valve(name):
    x = os.popen('uptime -p').read()[:-1]
    f = open(LOGFILE, 'a')
    sys.stdout = f
    print("TIME:{}  ACTION: Opening servo {}".format(x.strftime('%c'), name))
    f.close()
    set_valve(name, 9.5, 0.0)

def close_valve(name):
    x = datetime.now()
    print("TIME:{}  ACTION: Closing servo {}".format(x.strftime('%c'), name))
    set_valve(name, 2.0, 0.0)

def set_valve(name, moveVal, stopVal):
    servos[name]["instance"].ChangeDutyCycle(moveVal) # move servo
    time.sleep(0.25) # wait for it to finish moving
    servos[name]["instance"].ChangeDutyCycle(0.0) # stop moving servo
    time.sleep(1.5) # wait for it to fully stop


if __name__ == "__main__":
    #f = open(LOGFILE, 'a')
    #sys.stdout = f
    
    configure_servos(NUM_VALVES)
    time.sleep(EXP_WAIT_TIME)
    for i in range(NUM_VALVES):
        open_valve("{}A".format(i))
        time.sleep(INTRA_WAIT_TIME)
        open_valve("{}B".format(i))
        time.sleep(INTER_WAIT_TIME)

