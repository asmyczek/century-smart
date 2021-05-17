# Basic commands for webrepl
from sensor.sensor import PIN_LIGHT
from sensor.main import LOOP
import machine
import os

# Get current reading from light sensor
def sunlight():
    print(PIN_LIGHT.read())

# Reboot ESP
def reboot():
    machine.reset()

# Change current dir to sensor module
def cd_sensor():
    os.chdir('sensor')

# Change current dir to root
def cd_root():
    os.chdir('/')

# List current dir, avoids another import
def listdir():
    os.listdir()

# Stop application event loop
def stop():
    if LOOP:
        LOOP.stop()