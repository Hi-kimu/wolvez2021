import RPi.GPIO as GPIO
import sys
import time
import math
import numpy as np
PULSE = 898
ITERATION = 100

class estimation():
    def __init__(self,pin_a,pin_b,pin_c,pin_d): #各ピンのセットアップ
        GPIO.setmode(GPIO.BCM)
        
        #motorR set up
        GPIO.setup(pin_a, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(pin_b, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        self.pin_a = pin_a 
        self.pin_b = pin_b
    
        self.r_mot_speed = 0 #motor-revolution/sec
        self.r_numpulse = 0
        self.r_start = 0
        self.r_prev = 1
        self.r_itr = -1

        GPIO.add_event_detect(self.pin_a, GPIO.BOTH, callback=self.callback_right)
        GPIO.add_event_detect(self.pin_b, GPIO.BOTH, callback=self.callback_right)
        
        #motorL set up
        GPIO.setup(pin_c, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(pin_d, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        self.pin_c = pin_c
        self.pin_d = pin_d
    
        self.l_mot_speed=0 #motor-revolution/sec
        self.l_numpulse =0 
        self.l_start = 0
        self.l_prev = 1
        self.l_itr = -1  

        GPIO.add_event_detect(self.pin_c,GPIO.BOTH, callback=self.callback_left)
        GPIO.add_event_detect(self.pin_d,GPIO.BOTH, callback=self.callback_left)
        
        self.cansat_speed = 0 
        self.cansat_rad_speed = 0

    def callback_right(self,pin):
        print("right start")
        current_a=GPIO.input(self.pin_a)
        current_b=GPIO.input(self.pin_b)
        if self.r_itr==-1:
            self.r_start=time.time()
        encoded=(current_a<<1)|current_b
        sum=(self.r_prev<<2)|encoded
        self.r_prev=encoded
        self.r_itr+=1
        if sum==0b0010:
            self.r_numpulse+=1
        elif sum==0b0001:
            self.r_numpulse-=1
        elif sum==0b0011:
            print("right opps! skip pulse")
        
        delta_t = time.time()-self.r_start
        if self.r_itr==ITERATION or delta_t > 0.2:
            self.r_mot_speed=self.r_numpulse/(PULSE*delta_t) # revolution per second
            self.r_numpulse=0
            self.r_itr=0
            self.r_start=time.time()
        print("right end")



    def callback_left(self,pin):
        # print(f"{pin} callback")
        current_a=GPIO.input(self.pin_c)
        current_b=GPIO.input(self.pin_d)
        if self.l_itr==-1:
            self.l_start=time.time()
        encoded=(current_a<<1)|current_b
        sum=(self.l_prev<<2)|encoded
        self.l_prev=encoded
        self.l_itr+=1
        if sum==0b0010:
            self.l_numpulse+=1
        elif sum==0b0001:
            self.l_numpulse-=1
        elif sum==0b0011:
            print("left opps! skip pulse")
        
        delta_t = time.time()-self.l_start
        if self.l_itr==ITERATION or delta_t > 0.2:
            self.l_mot_speed=self.l_numpulse/(PULSE*delta_t) # revolution per second
            self.l_numpulse=0
            self.l_itr=0
            self.l_start=time.time()

    


    def est_vel(self, pin_a, pin_b, isRight):
        pre_a=1 # not to be 0010 or 0001 at first
        pre_b=1 # not to be 0010 or 0001 at first
        prev_data=1 # not to be 0010 or 0001 at first
        t_start=time.time()
        numpulse = 0
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
                elif sum==0b0011:
                    print("opps! skip pulse")
                
                if abs(numpulse)==ITERATION:
                    delta_t = time.time()-t_start
                    mot_speed=numpulse/(PULSE*delta_t) # revolution per second
                    if isRight == True:
                        #print("right encoder updated")
                        self.r_mot_speed, self.r_numpulse = mot_speed, numpulse
                    else:
                        #print("left encoder updated")
                        self.l_mot_speed, self.l_numpulse = mot_speed, numpulse
                    numpulse=0
                    t_start=time.time()
                    
            pre_a = current_a
            pre_b = current_b  

            # moter is stopping  
#             if time.time() - t_start > 1:
#                 mot_speed = 0
#                 if isRight == True:
#                     #print("right encoder updated")
#                     self.r_mot_speed, self.r_numpulse = mot_speed, numpulse
#                 else:
#                     #print("left encoder updated")
#                     self.l_mot_speed, self.l_numpulse = mot_speed, numpulse
            
    
    def est_v_w(self):
        self.cansat_speed = 2*3.14*(0.0665/2)*self.r_mot_speed + 2*3.14*(0.0665/2)*self.l_mot_speed
        self.cansat_rad_speed = (0.0665/0.196)*self.r_mot_speed - (0.0665/0.196)*self.l_mot_speed
        return self.cansat_speed, self.cansat_rad_speed

    def odometri(self,v,w,t,x,y,q):
        x_new=x+v*t*math.cos(q)
        y_new=y+v*t*math.sin(q)
        q_new=q+w*t
        return x_new,y_new,q_new