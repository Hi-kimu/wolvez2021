#実際にモーター買って試してみないとわからないかも、コードはこれでいけると思うんだけど...

import RPi.GPIO as GPIO
import sys
import time
import math
import numpy as np

class estimation():
    def __init__(self,pin_a,pin_b): #各ピンのセットアップ
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin_a, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(pin_b, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        self.pin_a = pin_a
        self.pin_b = pin_b
        
        self.angle=0.
        self.prev_angle=0.
        self.prev_data=0
        self.delta=360./15
        self.enc_time=[]
        self.enc_del_time=[]
        self.enc_ave_time=0
        self.mot_speed=0 #motor-revolution/sec
        
        GPIO.add_event_detect(self.pin_a,GPIO.BOTH)
        GPIO.add_event_detect(self.pin_b,GPIO.BOTH)
        
        
    def callback(self, gpio_pin):
        
        while self.mot_speed==0:
            self.current_a=GPIO.input(self.pin_a)
            self.current_b=GPIO.input(self.pin_b)
            
            self.encoded=(self.current_a<<1)|self.current_b
            sum=(self.prev_data<<2)|self.encoded
        
            if sum==0b0010:
                self.enc_time.append(time.time())
            
            if len(self.enc_time)==1000:
                for i in range(0,len(self.enc_time)-1):
                    self.enc_del_time.append(0)
                for i in range(0,len(self.enc_time)-1):
                    self.enc_del_time[i]=self.enc_time[i+1]-self.enc_time[i]
                
                self.enc_ave_time=np.mean(self.enc_del_time)
                self.mot_speed=1/(898*self.enc_ave_time)
                    
                #print("motor-revolution/sec",self.mot_speed)
                self.enc_time=[]
                self.enc_del_time=[]
            
            self.prev_data=self.encoded
            self.prev_angle = self.angle
        
        return self.mot_speed
        
            



