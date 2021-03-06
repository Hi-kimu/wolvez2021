import motor
import estimation
import constant as ct
import RPi.GPIO as GPIO
import time
from math import sqrt
import bno055
from math import radians
from math import sin
from math import fabs

GPIO.setwarnings(False)
MotorR = motor.motor(ct.const.RIGHT_MOTOR_IN1_PIN,ct.const.RIGHT_MOTOR_IN2_PIN,ct.const.RIGHT_MOTOR_VREF_PIN)
MotorL = motor.motor(ct.const.LEFT_MOTOR_IN1_PIN,ct.const.LEFT_MOTOR_IN2_PIN,ct.const.LEFT_MOTOR_VREF_PIN)
Encoder = estimation.estimation(ct.const.RIGHT_MOTOR_ENCODER_A_PIN,ct.const.RIGHT_MOTOR_ENCODER_B_PIN,ct.const.LEFT_MOTOR_ENCODER_A_PIN,ct.const.LEFT_MOTOR_ENCODER_B_PIN)
bno055 = bno055.BNO055()

bno055.setupBno()
x=0
y=0
q=0
del_t=0.2
hantei = 0
state = 1
x_remind = []
y_remind = []
q_remind = []
thread1 = []
thread2 = []
# MotorR.stop()
# MotorL.stop()

start_time=time.time()
print("cansat-x :",x,"[m]")
print("cansat-y :",y,"[m]")
print("cansat-q :",q,"[rad]")
bno055.bnoread()
try:
    print("motor run")
    MotorR.stop()
    MotorL.stop()
    
    MotorR.go(81)
    MotorL.go(80)
#     MotorR.back(80)
#     MotorL.back(80)
    
    while True:
        t1=time.time()
        cansat_speed,cansat_rad_speed, thread1, thread2=Encoder.est_VW(ct.const.RIGHT_MOTOR_ENCODER_A_PIN,ct.const.LEFT_MOTOR_ENCODER_A_PIN, thread1, thread2)
        t2=time.time()
        x,y,q=Encoder.odometri(cansat_speed,cansat_rad_speed,t2-t1,x,y,q)
        bno055.bnoread()
        q=radians(round(bno055.ex,3))
        print("cansat speed :",cansat_speed,"[m/s]")
        print("cansat rad speed :",cansat_rad_speed,"[rad/s]")
        print("cansat-x :",x,"[m]")
        print("cansat-y :",y,"[m]")
        print("cansat-q :",q,"[rad]")    
# bno055.bnoread()
# try:
#     print("motor run")
#     while True:
#         if state == 1:
#             q_remind=[]
#             MotorR.go(85)
#             MotorL.go(85)
#             t1=time.time()
# #             print(0)
#             cansat_speed,cansat_rad_speed, thread1, thread2=Encoder.est_VW(ct.const.RIGHT_MOTOR_ENCODER_A_PIN,ct.const.LEFT_MOTOR_ENCODER_A_PIN, thread1, thread2)
#             t2=time.time()
#             x,y,q=Encoder.odometri(cansat_speed,cansat_rad_speed,t2-t1,x,y,q)
#             bno055.bnoread()
#             q=radians(round(bno055.ex,3))
#             print("cansat speed :",cansat_speed,"[m/s]")
#             print("cansat rad speed :",cansat_rad_speed,"[rad/s]")
#             print("cansat-x :",x,"[m]")
#             print("cansat-y :",y,"[m]")
#             print("cansat-q :",q,"[rad]")
#             print("cansat-q :",bno055.ex,"[degree]")
#             print("sin",sin(q))
#             x_remind.append(x)
#             y_remind.append(y)
# #             if sqrt((abs(x_remind[-1]-x_remind[0]))**2 + (abs(y_remind[-1]-y_remind[0]))**2) >= 2.5:
#             if sqrt((abs(x))**2 + (abs(y))**2) >= 2:
#                 state = 2
#                 thread1 = []
#                 thread2 = []
#         elif state == 2:
#             x_remind=[]
#             y_remind = []
# #             print("motor curve") 
#             MotorR.go(60)
#             MotorL.go(5)
#             t1=time.time()
#             cansat_speed,cansat_rad_speed=Encoder.est_VW_for_c(ct.const.RIGHT_MOTOR_ENCODER_A_PIN,ct.const.LEFT_MOTOR_ENCODER_A_PIN)
# #             cansat_speed,cansat_rad_speed, thread1, thread2=Encoder.est_VW(ct.const.RIGHT_MOTOR_ENCODER_A_PIN,ct.const.LEFT_MOTOR_ENCODER_A_PIN, thread1, thread2)
#             t2=time.time()
#             x,y,q=Encoder.odometri(cansat_speed,cansat_rad_speed,t2-t1,x,y,q)
#             bno055.bnoread()
#             q=round(bno055.ex,6)
#             print("cansat speed :",cansat_speed,"[m/s]")
#             print("cansat rad speed :",cansat_rad_speed,"[rad/s]")
#             print("cansat-x :",x,"[m]")
#             print("cansat-y :",y,"[m]")
#             print("cansat-q :",q,"")
#             print("sin",sin(radians(q)))
#             q_remind.append(radians(q))
#             """
#             if sin((abs(q_remind[-1]-q_remind[0])))>=0.9:
#                 state = 1
#                 """
#             if fabs(q-270)<2:
#                 state=1
#                 thread1 = []
#                 thread2 = []
#         elif state == 3:
#             MotorR.go(81)
#             MotorL.go(80)
            

# try:
#     print("motor run") 
#     MotorR.back(80)
#     MotorL.go(80)
#     
#     while hantei == 0:
#         hantei = Encoder.callback2(ct.const.RIGHT_MOTOR_ENCODER_A_PIN,ct.const.LEFT_MOTOR_ENCODER_A_PIN)
#         if hantei == 1:
#             break
#     MotorR.stop()
#     MotorL.stop()
#     GPIO.cleanup()
        
    #time.sleep(1)
except KeyboardInterrupt:
    t2=time.time()
    MotorR.stop()
    MotorL.stop()
    x,y,q=Encoder.odometri(cansat_speed,cansat_rad_speed,t2-t1,x,y,q)
    q=radians(round(bno055.ex,3))
    print("cansat speed :",cansat_speed,"[m/s]")
    print("cansat rad speed :",cansat_rad_speed,"[rad/s]")
    print("cansat-x :",x,"[m]")
    print("cansat-y :",y,"[m]")
    print("cansat-q :",q,"[rad]")
    end_time=time.time()
    print("motor stop")
    print(end_time-start_time,"[s]")
    
    GPIO.cleanup()

GPIO.cleanup()

