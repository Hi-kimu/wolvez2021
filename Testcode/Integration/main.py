# -*- coding: utf-8 -*-

import cansat
import time
import RPi.GPIO as GPIO
import sys
import constant as ct


can=cansat.Cansat()
can.setup()
can.state = 5
GPIO.setwarnings(False)

try:
    while True:
<<<<<<< HEAD
#         can.integ()
=======
        #can.integ()
>>>>>>> 5ab9fb7d062a75cde5964984cc920853075b0659
        can.sensor()
        time.sleep(0.05)
        can.sequence()

except KeyboardInterrupt:
    print('finished')
    can.keyboardinterrupt()
    GPIO.cleanup()
    can.rightmotor.stop()
    can.leftmotor.stop()
    pass
