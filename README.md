# brics
mars-iss-bricks repo for SPOCS

This branch is used for testing a single servo connected to a Raspberry Pi.

Contact _lglik_ if you have any questions!

## Setup Instructions

cd to your _brics_ directory where requirements.txt is located.

activate your virtualenv if you have one.

run ```pip install -r requirements.txt``` in your shell.

## Running the script

run ```python TestSingleServo.py``` in your shell to run the program with the default servo gpio port set to 12.

Or, run ```python TestSingleServo.py port``` where ```port``` is the gpio port number the servo is connected to.
