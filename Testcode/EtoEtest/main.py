# -*- coding: utf-8 -*-

import cansat
import cv2
import time
import RPi.GPIO as GPIO
import sys
import constant as ct

can=cansat.Cansat()
can.setup()

try:
    can.capture = cv2.VideoCapture(0)
    #can.capture.set(cv2.CAP_PROP_FRAME_WIDTH,640)
    #can.capture.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
    #can.capture.set(cv2.CAP_PROP_FOURCC,cv2.VideoWriter_fourcc('H','2','6','4'));
    #while cv2.waitKey(1) < 0:
    while True:
        can.sensor()
        t1=time.time()
        #time.sleep(0.05)
        can.sequence()
        t2=time.time()
        time.sleep(0.05)
        #print(t2-t1)
except KeyboardInterrupt:
    print('finished')
    GPIO.output(ct.const.RELEASING_PIN,0) #焼き切りが危ないのでlowにしておく
    GPIO.cleanup()
    pass