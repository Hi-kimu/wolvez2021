#実際にモーター買って試してみないとわからないかも、コードはこれでいけると思うんだけど...

import RPi.GPIO as GPIO
import sys
import time
import math
import numpy as np

class estimation():
    def __init__(self,pin_a,pin_b,pin_c,pin_d): #各ピンのセットアップ
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin_a, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(pin_b, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(pin_c, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(pin_d, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        self.pin_a = pin_a
        self.pin_b = pin_b
        self.pin_c = pin_c
        self.pin_d = pin_d
        
        self.angle=0.
        self.prev_angle=0.
        self.prev_data=0
        self.delta=360./15
        self.enc_time=[]
        self.enc_del_time=[]
        self.enc_ave_time=0
        self.mot_speed=0 #motor-revolution/sec
        
        self.angle2=0.
        self.prev_angle2=0.
        self.prev_data2=0
        self.delta2=360./15
        self.enc_time2=[]
        self.enc_del_time2=[]
        self.enc_ave_time2=0
        self.mot_speed2=0
        
        GPIO.add_event_detect(self.pin_a,GPIO.BOTH)
        GPIO.add_event_detect(self.pin_b,GPIO.BOTH)
        GPIO.add_event_detect(self.pin_c,GPIO.BOTH)
        GPIO.add_event_detect(self.pin_d,GPIO.BOTH)
        
    def callback(self, gpio_pin):
        
        self.current_a=GPIO.input(self.pin_a)
        self.current_b=GPIO.input(self.pin_b)
        
        self.encoded=(self.current_a<<1)|self.current_b
        sum=(self.prev_data<<2)|self.encoded
        
        if sum==0b0010:
            self.enc_time.append(time.time())
        
        if len(self.enc_time)==100:
            for i in range(0,len(self.enc_time)-1):
                self.enc_del_time.append(0)
            for i in range(0,len(self.enc_time)-1):
                self.enc_del_time[i]=self.enc_time[i+1]-self.enc_time[i]
            
            self.enc_ave_time=np.mean(self.enc_del_time)
            self.mot_speed=1/(898*self.enc_ave_time)
                
            #print(self.enc_time)
            #print(self.enc_del_time)
            #print(self.enc_ave_time)
            print("motor-revolution/sec",self.mot_speed)
            self.enc_time=[]
            self.enc_del_time=[]
        
        self.prev_data=self.encoded
        self.prev_angle = self.angle
        
    def callback2(self, gpio_pin,gpio_pin2):
        
        self.current_a=GPIO.input(self.pin_a)
        self.current_b=GPIO.input(self.pin_b)
        self.current_c=GPIO.input(self.pin_c)
        self.current_d=GPIO.input(self.pin_d)
        
        self.encoded=(self.current_a<<1)|self.current_b
        sum=(self.prev_data<<2)|self.encoded
        self.encoded2=(self.current_c<<1)|self.current_d
        sum2=(self.prev_data2<<2)|self.encoded2
        
        if sum==0b0010:
            self.enc_time.append(time.time())
        if sum2==0b0000:
            self.enc_time2.append(time.time())
        
        if (len(self.enc_time)>=100) and (len(self.enc_time2)>=100):
            for i in range(0,len(self.enc_time)-1):
                self.enc_del_time.append(0)
            for i in range(0,len(self.enc_time)-1):
                self.enc_del_time[i]=self.enc_time[i+1]-self.enc_time[i]
            
            self.enc_ave_time=np.mean(self.enc_del_time)
            self.mot_speed=1/(898*self.enc_ave_time)
            
            for i in range(0,len(self.enc_time2)-1):
                self.enc_del_time2.append(0)
            for i in range(0,len(self.enc_time2)-1):
                self.enc_del_time2[i]=self.enc_time2[i+1]-self.enc_time2[i]
            
            self.enc_ave_time2=np.mean(self.enc_del_time2)
            self.mot_speed2=1/(898*self.enc_ave_time2)
                
            #print(self.enc_time)
            #print(self.enc_del_time)
            #print(self.enc_ave_time)
            print("1motor-revolution/sec",self.mot_speed)
            self.enc_time=[]
            self.enc_del_time=[]
            print("2motor-revolution/sec",self.mot_speed2)
            self.enc_time2=[]
            self.enc_del_time2=[]
            


