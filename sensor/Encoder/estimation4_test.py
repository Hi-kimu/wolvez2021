import motor
import estimation4
import constant as ct
import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
MotorR = motor.motor(ct.const.RIGHT_MOTOR_IN1_PIN,ct.const.RIGHT_MOTOR_IN2_PIN,ct.const.RIGHT_MOTOR_VREF_PIN)
MotorL = motor.motor(ct.const.LEFT_MOTOR_IN1_PIN,ct.const.LEFT_MOTOR_IN2_PIN,ct.const.LEFT_MOTOR_VREF_PIN)
Encoder = estimation4.estimation(ct.const.RIGHT_MOTOR_ENCODER_A_PIN,ct.const.RIGHT_MOTOR_ENCODER_B_PIN,ct.const.LEFT_MOTOR_ENCODER_A_PIN,ct.const.LEFT_MOTOR_ENCODER_B_PIN)
#Motor2 = motor.motor(20,21,12)
x=0
y=0
q=0
del_t=0.2

start_time=time.time()
print("cansat-x :",x,"[m]")
print("cansat-y :",y,"[m]")
print("cansat-q :",q,"[rad]")

try:
    print("motor run") 
    MotorR.go(90)
    MotorL.go(60)
    #print("-------------speed60----------------")
    while True:
        """
        v1,v2=Encoder.callback(19,20) #motor's speed [revolution/sec]
        print(v1)
        print(v2)
        """
        t1=time.time()
        cansat_speed,cansat_rad_speed=Encoder.est_v_w(19,20)
        #time.sleep(del_t)
        t2=time.time()
        x,y,q=Encoder.odometri(cansat_speed,cansat_rad_speed,t2-t1,x,y,q)
        print("cansat speed :",cansat_speed,"[m/s]")
        print("cansat rad speed :",cansat_rad_speed,"[rad/s]")
        print("cansat-x :",x,"[m]")
        print("cansat-y :",y,"[m]")
        print("cansat-q :",q,"[rad]")
        
    #time.sleep(1)
except KeyboardInterrupt:
    end_time=time.time()
    print("motor stop")
    print(end_time-start_time,"[s]")
    MotorR.stop()
    MotorL.stop()
    #Motor2.stop()
    GPIO.cleanup()

GPIO.cleanup()
