# -*- coding: utf-8 -*-

import cansat
import time
import RPi.GPIO as GPIO
import sys
import constant as ct


can=cansat.Cansat()
can.setup()


try:
    while True:
        can.sensor()
        can.integ()
        time.sleep(0.05)
        can.sequence()

except KeyboardInterrupt:
    print('finished')
    GPIO.cleanup()
    pass