#import gps
#from MicropyGPS import MicropyGPS
#from LoRa_SOFT.LoRa import LoRa
import sys
sys.path.append("/home/pi/Desktop/wolvez2021/Testcode/sensor_integration/LoRa_SOFT")
from bno055 import BNO055
from encoder_motor2 import motor
from servomotor import servomotor
import time
import RPi.GPIO as GPIO
import numpy as np
import LoRa
import os

class Cansat():
    def __init__(self):
        GPIO.setwarnings(False)
        #self.microgps = MicropyGPS(9,'dd')# MicroGPSオブジェクトを生成する。
        self.bno055 = BNO055()
        self.rightMotor = motor(19,26,5,6,13)
        self.leftMotor = motor(8,7,16,20,21)
        self.servomotor = servomotor(18)
        self.bno055.setupBno()
        self.LoRa = LoRa.LoRa()
        GPIO.setmode(GPIO.BCM) #GPIOの設定
         
    def run(self):  
        try:
            #self.getgps()
            #self.rightMotor.go(60)#rightmotor
            #self.leftMotor.go(60)#leftmotor
            if self.bno055.begin() is not True:
                print("Error initializing device")
            os.system("sudo insmod LoRa_SOFT/soft_uart.ko")
            self.LoRa.setup()
            while True:
                self.getbno055()
                self.LoRa.sensor()
                #self.rotate_servo()#servomotor
                #self.rotate_motor()# motor
                #time.sleep(1)
                #time.sleep(1)
            print("motor stop")
            #self.rightMotor.stop()
            #self.leftMotor.stop()
            #time.sleep(1)
            
        except KeyboardInterrupt:
            GPIO.cleanup()
            pass
            
    def getgps(self):
        thread()# 引数はタイムゾーンの時差と出力フォーマット
        gpsread()
        
    def getbno055(self):      
        self.bno055.bnoread()
        self.bno055.ax=round(self.bno055.ax,3)
        self.bno055.ay=round(self.bno055.ay,3)
        self.bno055.az=round(self.bno055.az,3)
        self.bno055.gx=round(self.bno055.gx,3)
        self.bno055.gy=round(self.bno055.gy,3)
        self.bno055.gz=round(self.bno055.gz,3)
        self.bno055.ex=round(self.bno055.ex,3)
        self.bno055.ey=round(self.bno055.ey,3)
        self.bno055.ez=round(self.bno055.ez,3)
        accel="ax="+str(self.bno055.ax)+","\
              +"ay="+str(self.bno055.ay)+","\
              +"az="+str(self.bno055.az)
        grav="gx="+str(self.bno055.gx)+","\
              +"gy="+str(self.bno055.gy)+","\
              +"gz="+str(self.bno055.gz) # including gravity
        euler="ex="+str(self.bno055.ex)+","\
              +"ey="+str(self.bno055.ey)+","\
              +"ez="+str(self.bno055.ez)
        magnet="mx="+str(self.bno055.mx)+","\
              +"my="+str(self.bno055.my)+","\
              +"mz="+str(self.bno055.mz)
        print(grav,euler,magnet) 
              
        
    def rotate_servo(self):
        print("servomotor run") 
        self.servomotor.servo_angle(-90)               #サーボモータ -90°
        self.servomotor.servo_angle(0)                 #サーボモータ  0°
        self.servomotor.servo_angle(90)
                
    def rotate_motor(self):
        self.rightMotor.callback(19)
        #print("19 to 26")
        self.rightMotor.callback(26)
        #print("8")
        self.leftMotor.callback(8)
        #print("7")
        self.leftMotor.callback(7)
                #time.sleep(0.01)
                #if speed1 !=0 and speed2 !=0:
                    #print(speed1,speed2)
        
cansat = Cansat()
if __name__ == "__main__":
    cansat.run()