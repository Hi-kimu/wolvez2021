import motor
import estimation_interrupt
import constant as ct
import RPi.GPIO as GPIO
import time
from math import sqrt
import threading

GPIO.setwarnings(False)
MotorR = motor.motor(ct.const.RIGHT_MOTOR_IN1_PIN,ct.const.RIGHT_MOTOR_IN2_PIN,ct.const.RIGHT_MOTOR_VREF_PIN)
MotorL = motor.motor(ct.const.LEFT_MOTOR_IN1_PIN,ct.const.LEFT_MOTOR_IN2_PIN,ct.const.LEFT_MOTOR_VREF_PIN)
Encoder = estimation_interrupt.estimation(ct.const.RIGHT_MOTOR_ENCODER_A_PIN,ct.const.RIGHT_MOTOR_ENCODER_B_PIN,ct.const.LEFT_MOTOR_ENCODER_A_PIN,ct.const.LEFT_MOTOR_ENCODER_B_PIN)


x=0
y=0
q=0
DEL_T = 0.5
t_now = time.time()
state = 1
x_remind = []
y_remind = []
q_remind = []

start_time=time.time()
print("cansat-x :",x,"[m]")
print("cansat-y :",y,"[m]")
print("cansat-q :",q,"[rad]")


try:
    print("motor run") 
    while True:
        if state == 1:
            q_remind=[]
            MotorR.go(81)
            MotorL.go(80)
            t_pre = t_now
            t_now=time.time()
            cansat_speed,cansat_rad_speed=Encoder.est_v_w()           
            x,y,q=Encoder.odometri(cansat_speed,cansat_rad_speed,t_now-t_pre,x,y,q)
            print(f"r:{Encoder.r_mot_speed},l:{Encoder.l_mot_speed}")
            print("cansat speed :",cansat_speed,"[m/s]")
            print("cansat rad speed :",cansat_rad_speed,"[rad/s]")
            print("cansat-x :",x,"[m]")
            print("cansat-y :",y,"[m]")
            print("cansat-q :",q,"[rad]")
            x_remind.append(x)
            y_remind.append(y)

            if sqrt((abs(x_remind[-1]-x_remind[0]))**2 + (abs(y_remind[-1]-y_remind[0]))**2) >= 1:
                print("stop")
                #state = 2
                MotorR.stop()
                MotorL.stop()
                time.sleep(100)

            time.sleep(DEL_T)
        elif state == 2:
            x_remind=[]
            y_remind = []
            MotorR.go(60)
            MotorL.go(60)
            t_pre = t_now
            t_now=time.time()
            cansat_speed,cansat_rad_speed=Encoder.est_v_w()
            x,y,q=Encoder.odometri(cansat_speed,cansat_rad_speed,t_now-t_pre,x,y,q)
            print("cansat speed :",cansat_speed,"[m/s]")
            print("cansat rad speed :",cansat_rad_speed,"[rad/s]")
            print("cansat-x :",x,"[m]")
            print("cansat-y :",y,"[m]")
            print("cansat-q :",q,"[rad]")
            q_remind.append(q)
            if abs(q_remind[-1]-q_remind[0]) >=1.57:
                state = 1
            time.sleep(DEL_T)

except KeyboardInterrupt:
    print("cansat speed :",cansat_speed,"[m/s]")
    print("cansat rad speed :",cansat_rad_speed,"[rad/s]")
    print("cansat-x :",x,"[m]")
    print("cansat-y :",y,"[m]")
    print("cansat-q :",q,"[rad]")
    end_time=time.time()
    print("motor stop")
    print(end_time-start_time,"[s]")
    MotorR.stop()
    MotorL.stop()
    GPIO.cleanup()

GPIO.cleanup()
