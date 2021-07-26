"""
A small script that uses the piservo library to actuate a single servo
Stanford Student Space Initiative - Biopolymer Research for In-situ Construction
Written by Leo Glikbarg
"""
import RPi.GPIO as GPIO
import time
import sys


def run(gpio_port=12):
    """opens or closes a servo repeastedly as directed through user prompts"""
    servoPIN = gpio_port
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(servoPIN, GPIO.OUT)
    servo = GPIO.PWM(servoPIN, 50)
    servo.start(0)
    stop = False
    while not stop:
        choice = prompt()
        if choice == "stop":
            stop = True
        elif choice == "open":
            print("\nopening the servo")
            servo.ChangeDutyCycle(100.0)
            # give the servo time to actuate
            time.sleep(1)
        else:
            print("\nclosing the servo")
            servo.ChangeDutyCycle(0.0)
            # give the servo time to actuate
            time.sleep(1)


def prompt():
    """ask the user what they would like to do, and return their response"""
    print(
        "\nWould you like to 'open' or 'close' the servo?\nType 'stop' to end the program.\n"
    )
    return raw_input("")


if __name__ == "__main__":
    """starts the run() method. Read the run() docstring for more information"""
    if len(sys.argv) > 1:
        run(sys.argv[1])
    else:
        run()
