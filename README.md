# brics
mars-iss-bricks repo for SPOCS

This branch is used for testing a single bme680 servo connected to a Raspberry Pi.

Contact _lglik_ if you have any questions!

## Setup Instructions

cd to your _brics_ directory where requirements.txt is located.
activate your virtualenv if you have one.
run ```pip install -r requirements.txt``` in your shell.

## Running the script

run ```python SingleSensor.py``` in your shell to run the program with the default sensor rate of 0.5Hz.

Or, run ```python SingleSensor.py speed``` where ```speed``` is the desired read rate of the sensor in Hz. 
