"""
A small script that uses the piservo library to actuate a single servo
Stanford Student Space Initiative - Biopolymer Research for In-situ Construction
Written by Leo Glikbarg
"""
from piservo import Servo
import time

GPIO_PORT_NUM = 12

def run():
    """"opens or closes a servo repeastedly as directed through user prompts"""
    single_servo = Servo(GPIO_PORT_NUM)
    stop = False
    while not stop:
        choice = prompt()
        if choice == 'stop':
            stop = True
        elif choice == 'open':
            print("\nopening the servo")
            single_servo.write(180)
            # give the servo time to actuate
            time.sleep(1)
        else:
            print("\nclosing the servo")
            single_servo.write(0)
            # give the servo time to actuate
            time.sleep(1)


def prompt():
    """"ask the user what they would like to do, and return their response"""
    print("\nWould you like to \'open\' or \'close\' the servo?\nType \'stop\' to end the program.\n")
    return raw_input("")

if __name__ == "__main__":
    """starts the run() method. Read the run() docstring for more information"""
    run()