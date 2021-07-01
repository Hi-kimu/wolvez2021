#実際にモーター買って試してみないとわからないかも、コードはこれでいけると思うんだけど...

import RPi.GPIO as GPIO
import sys
import time
import math
import numpy as np

class motor():
    def __init__(self,pin_a,pin_b,pin1,pin2,vref): #各ピンのセットアップ
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin_a, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(pin_b, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        GPIO.setup(pin1, GPIO.OUT)
        GPIO.setup(pin2, GPIO.OUT)
        GPIO.setup(vref, GPIO.OUT)
        
        self.pin_a = pin_a
        self.pin_b = pin_b
        self.pin1 = pin1 #入力1
        self.pin2 = pin2 #入力2
        self.vref = vref #電圧を参照するピン PWM
        self.velocity = 0
        self.pwm = GPIO.PWM(vref,50) #電圧を参照するピンを周波数50HZに指定（Arduinoはデフォルトで490だけど、ラズパイはネットだと50HZがメジャーそうだった）
        
        self.angle=0.
        self.prev_angle=0.
        self.prev_data=0
        self.delta=360./15
        self.enc_time=[]
        self.enc_del_time=[]
        self.enc_ave_time=0
        motor.mot_speed=0 #motor-revolution/sec
        
        GPIO.add_event_detect(self.pin_a,GPIO.BOTH)
        GPIO.add_event_detect(self.pin_b,GPIO.BOTH)
        
        GPIO.output(self.pin1,GPIO.LOW)
        GPIO.output(self.pin2,GPIO.LOW)
        
#正転
    def go(self,v):
        if v>100:
            v=0
        if v<0:
            v=0 #vに辺な値があった時の処理のための4行,backのも同じ
        self.velocity=v #vは0から100のDuty比、速度を表す指標として利用、後々stopslowlyで使用
        GPIO.output(self.pin1,GPIO.HIGH)
        GPIO.output(self.pin2,GPIO.LOW)
        self.pwm.start(v)#Duty比の指定、以下同様
        
#逆転        
    def back(self,v):
        if v>100:
            v=0
        if v<0:
            v=0
        self.velocity=-v
        GPIO.output(self.pin1,GPIO.LOW)
        GPIO.output(self.pin2,GPIO.HIGH)
        self.pwm.start(v)
        print(v)
        
#回転ストップ
    def stop(self):
        self.velocity=0
        self.pwm.stop(0)
        GPIO.output(self.pin1,0)
        GPIO.output(self.pin2,0)
        
#徐々に回転遅くして最終的にストップ
    def stopslowly(self):
        if not self.velocity==0:
            for _velocity in range(self.velocity,0,-10): #少しずつDuty比を落として速度を落とす、-10のところは実験によって変えられそう
                self.pwm.ChangeDutyCycle(_velocity)
                GPIO.output(self.pin1,1)
                GPIO.output(self.pin2,0)
                time.sleep(0.5)
            self.velocity=0
        self.pwm.ChangeDutyCycle(0)
        GPIO.output(self.pin1,0)
        GPIO.output(self.pin2,0)
        
#ブレーキ（何であるんだろう？）
    def brake(self):
        self.velocity=0
        self.pwm.ChangeDutyCycle(0)
        GPIO.output(self.pin1,1)
        GPIO.output(self.pin2,1)
        
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
            
#             return self.mot_speed
            
        
            
            
            
        
        #print("aaaaaa",self.current_a)
        #print("bbbbbb",self.current_b)
        """
        print(bin(sum))
        
        if(sum==0b0010 or sum==0b1011 or sum==0b1101 or sum==0b0100):
            self.angle+=self.delta
            print("plus",gpio_pin,self.angle)
        elif(sum==0b0001 or sum==0b0111 or sum==0b1110 or sum==0b1000):
            self.angle-=self.delta
            print("minus",gpio_pin,self.angle)
        
        #self.w_r=(self.angle-self.prev_angle)/0.1
        #print("-----w_speed------",self.w_r)
        """
        
        #self.w_r=(self.encoded-self.prev_data)*2*math.pi/(1*74.83*0.1)
        #print("-----w_speed------",self.w_r)
        
        self.prev_data=self.encoded
        self.prev_angle = self.angle
            


