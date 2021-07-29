#ライブラリの読み込み
import time
import RPi.GPIO as GPIO
import sys
import numpy as np
import datetime
import os
import constant as ct

import motor
import bno055

GPIO.setmode(GPIO.BCM) #GPIOの設定

#オブジェクトの生成
rightmotor = motor.motor(ct.const.RIGHT_MOTOR_IN1_PIN,ct.const.RIGHT_MOTOR_IN2_PIN,ct.const.RIGHT_MOTOR_VREF_PIN)
leftmotor = motor.motor(ct.const.LEFT_MOTOR_IN1_PIN,ct.const.LEFT_MOTOR_IN2_PIN,ct.const.LEFT_MOTOR_VREF_PIN)
bno055 = bno055.BNO055()

bno055.setupBno()

def integ():
    rightmotor.go(60)
    leftmotor.go(60)

def keyboardinterrupt():
    rightmotor.stop()
    leftmotor.stop()



try:
    while True:
        integ()  
        
        bno055.bnoread()
        print(bno055.ex)

        time.sleep(0.05)
     
except KeyboardInterrupt:
    print('finished')
    keyboardinterrupt()
    GPIO.cleanup()
    pass