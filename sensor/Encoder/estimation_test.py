import motor
import estimation
import constant as ct
import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
MotorR = motor.motor(ct.const.RIGHT_MOTOR_IN1_PIN,ct.const.RIGHT_MOTOR_IN2_PIN,ct.const.RIGHT_MOTOR_VREF_PIN)
MotorL = motor.motor(ct.const.LEFT_MOTOR_IN1_PIN,ct.const.LEFT_MOTOR_IN2_PIN,ct.const.LEFT_MOTOR_VREF_PIN)
Encoder = estimation.estimation(ct.const.RIGHT_MOTOR_ENCODER_A_PIN,ct.const.RIGHT_MOTOR_ENCODER_B_PIN,ct.const.LEFT_MOTOR_ENCODER_A_PIN,ct.const.LEFT_MOTOR_ENCODER_B_PIN)

x=0
y=0
q=0
del_t=0.2
hantei = 0

start_time=time.time()
print("cansat-x :",x,"[m]")
print("cansat-y :",y,"[m]")
print("cansat-q :",q,"[rad]")

try:
    print("motor run") 
    MotorR.go(81)
    MotorL.go(80)
    
    while True:
        t1=time.time()
        cansat_speed,cansat_rad_speed=Encoder.est_v_w(ct.const.RIGHT_MOTOR_ENCODER_A_PIN,ct.const.LEFT_MOTOR_ENCODER_A_PIN)
        #time.sleep(del_t)
        t2=time.time()
        x,y,q=Encoder.odometri(cansat_speed,cansat_rad_speed,t2-t1,x,y,q)
        print("cansat speed :",cansat_speed,"[m/s]")
        print("cansat rad speed :",cansat_rad_speed,"[rad/s]")
        print("cansat-x :",x,"[m]")
        print("cansat-y :",y,"[m]")
        print("cansat-q :",q,"[rad]")
"""
try:
    print("motor run") 
    MotorR.go(81)
    MotorL.go(80)
    
    while True:
        t1=time.time()
        cansat_speed,cansat_rad_speed=Encoder.est_v_w(ct.const.RIGHT_MOTOR_ENCODER_A_PIN,ct.const.LEFT_MOTOR_ENCODER_A_PIN)
        #time.sleep(del_t)
        t2=time.time()
        x,y,q=Encoder.odometri(cansat_speed,cansat_rad_speed,t2-t1,x,y,q)
        print("cansat speed :",cansat_speed,"[m/s]")
        print("cansat rad speed :",cansat_rad_speed,"[rad/s]")
        print("cansat-x :",x,"[m]")
        print("cansat-y :",y,"[m]")
        print("cansat-q :",q,"[rad]")
        
        if x >= 6:
            print("motor run") 
            MotorR.go(81)
            MotorL.go(50)
"""
# try:
#     print("motor run") 
#     MotorR.go(82)
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
    x,y,q=Encoder.odometri(cansat_speed,cansat_rad_speed,t2-t1,x,y,q)
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
