# Basic commands for webrepl
from sensor.sensor import PIN_LIGHT
from sensor.main import LOOP
from besp import WDT
import machine
import os


SERVICE = 'gate-sensor'

# Stop watch dog when loading cmd module
print('Stopping watchdog process...')
WDT.deinit()

print('Commands: reboot, cd_sensor, cd_root, ls, stop, cat_error, rm_error, sunlight')


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
def ls():
    print(os.listdir())

# Stop application event loop
def stop():
    if LOOP:
        LOOP.stop()

# Print error from file
def cat_error():
    try:
        f = open('error.log', 'r')
        print(f.read())
        f.close()
    except OSError:
        print('No error file.')

# Remove error file
def rm_error():
    try:
        os.remove('error.log')
        print('Error file removed.')
    except OSError:
        print('No error file.')