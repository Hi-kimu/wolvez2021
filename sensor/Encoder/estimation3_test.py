import motor
import estimation3
import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
MotorR = motor.motor(6,5,13)
MotorL = motor.motor(27,22,17)
Encoder = estimation3.estimation(19,26,20,21)
#Motor2 = motor.motor(20,21,12)

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
        cansat_speed,cansat_rad_speed=Encoder.est_v_w(19,20)
        print("cansat speed :",cansat_speed,"[m/s]")
        print("cansat rad speed :",cansat_rad_speed,"[rad/s]")
        
    time.sleep(1)
except KeyboardInterrupt:
    print("motor stop")
    MotorR.stop()
    MotorL.stop()
    #Motor2.stop()
    GPIO.cleanup()

GPIO.cleanup()





