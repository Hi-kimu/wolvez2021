import RPi.GPIO as GPIO
import sys
import time
import math
import numpy as np
PULSE = 898
ITERATION = 10

class estimation():
    def __init__(self,pin_a,pin_b,pin_c,pin_d): #各ピンのセットアップ
        GPIO.setmode(GPIO.BCM)
        
        #motorR set up
        GPIO.setup(pin_a, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(pin_b, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        self.pin_a = pin_a 
        self.pin_b = pin_b
    
        self.r_mot_speed=0 #motor-revolution/sec
        self.r_numpulse = 0
        
        GPIO.add_event_detect(self.pin_a,GPIO.BOTH)
        GPIO.add_event_detect(self.pin_b,GPIO.BOTH)
        
        #motorL set up
        GPIO.setup(pin_c, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(pin_d, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        self.pin_c = pin_c
        self.pin_d = pin_d
    
        self.l_mot_speed=0 #motor-revolution/sec
        self.l_numpulse = 0   

        GPIO.add_event_detect(self.pin_c,GPIO.BOTH)
        GPIO.add_event_detect(self.pin_d,GPIO.BOTH)
        
        self.cansat_speed = 0 
        self.cansat_rad_speed = 0
        

    def est_vel(self, pin_a, pin_b):
        pre_a=1 # not to be 0010 or 0001 at first
        pre_b=1 # not to be 0010 or 0001 at first
        prev_data=1 # not to be 0010 or 0001 at first
        t_start=time.time()
        while True:
            current_a=GPIO.input(pin_a)
            current_b=GPIO.input(pin_b)
            
            if current_a!=pre_a or current_b!=pre_b:
                encoded=(current_a<<1)|current_b
                sum=(prev_data<<2)|encoded
                prev_data=encoded
        
                if sum==0b0010:
                    numpulse+=1
                elif sum==0b0001:
                    numpulse-=1
                
                if abs(numpulse)==ITERATION:
                    delta_t = time.time()-t_start
                    mot_speed=numpulse/(PULSE*delta_t) # revolution per second 
                    break
            pre_a = current_a
            pre_b = current_b  

            # moter is stopping  
            if time.time() - t_start > 0.1:
                mot_speed = 0                    
        return mot_speed, numpulse
                    #print("motor-revolution/sec",self.mot_speed)


    def est_right_vel(self):
        while True:
            self.r_mot_speed, self.r_numpulse=self.est_vel(self, self.pin_a, self.pin_b)
    
    def est_left_vel(self):
        while True:
            self.l_mot_speed, self.l_numpulse=self.est_vel(self, self.pin_c, self.pin_d)
    
    def est_v_w(self):
        self.cansat_speed = 2*3.14*(0.0665/2)*self.r_mot_speed + 2*3.14*(0.0665/2)*self.l_mot_speed
        self.cansat_rad_speed = (0.0665/0.196)*self.r_mot_speed - (0.0665/0.196)*self.l_mot_speed
        return self.cansat_speed, self.cansat_rad_speed

    def odometri(self,v,w,t,x,y,q):
        x_new=x+v*t*math.cos(q)
        y_new=y+v*t*math.sin(q)
        q_new=q+w*t
        return x_new,y_new,q_new