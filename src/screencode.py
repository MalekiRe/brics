# Import LCD library
from RPLCD import i2c
from time import sleep
from collections import deque

# constants to initialise the LCD
lcdmode = 'i2c'
cols = 20
rows = 4
charmap = 'A00'
i2c_expander = 'PCF8574'

# Generally 27 is the address;Find yours using: i2cdetect -y 1 
address = 0x27 
port = 1 # 0 on an older Raspberry Pi

# Switch off backlight
# lcd.backlight_enabled = False

# Initialise the LCD
lcd = i2c.CharLCD(i2c_expander, address, port=port, charmap=charmap,
                  cols=cols, rows=rows)

# Returns the last n lines of a file
def tail(filename, n):
    with open(filename) as f:
        return deque(f, n)

endoffile = tail('../log/sensor.log',5)

# Write a string on first line and move to next line
def printinfo():
    for i in endoffile:
        if '-' in i:
            continue
        lcd.write_string(i)
        lcd.crlf()
    sleep(5) 

while True:
    printinfo()
