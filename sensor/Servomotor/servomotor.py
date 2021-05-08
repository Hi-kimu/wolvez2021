import time
import RPi.GPIO as GPIO
 
class servomotor():
    def __init__(self,pin): #各ピンのセットアップ
        GPIO.setmode(GPIO.BCM) 
        GPIO.setup(pin, GPIO.OUT)
        self.pin = pin
        self.pwm = GPIO.PWM(vref,50) #電圧を参照するピンを周波数50HZに指定
        self.pwm.start(0.0)
        
    def right(self):#正転90度
        self.pwm.ChangeDutyCycle(2.5)
        
    def mid(self):#もとの場所
        self.pwm.ChangeDutyCycle(7.5)
        
    def left(self):#逆転90度
        self.pwm.ChangeDutyCycle(12.5)
        
    def stop(self):
        self.pwm.stop()