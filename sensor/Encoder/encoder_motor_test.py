import encoder_motor
import RPi.GPIO as GPIO
import time 

GPIO.setwarnings(False)
Motor1 = encoder_motor.motor(19,26,6,5,13)
Motor2 = encoder_motor.motor(20,21,27,22,17)
#Motor2 = motor.motor(20,21,12)

try:
    print("motor run") 
    Motor1.go(90)
    Motor2.go(90)
    #print("-------------speed60----------------")
    while True:
        Motor1.callback(19)
        Motor1.callback(26)
        Speed21=Motor2.callback(20)
        Speed22=Motor2.callback(21)
        #time.sleep(0.1)
    
    """
    Motor1.go(30)
    print("-------------speed30----------------")
    for i in range(1,91):
        Motor1.callback(19)
        Motor1.callback(26)
        time.sleep(0.1)
    """
    
    #Motor2.go(100)

    #Motor.back(100)
    #time.sleep(3)
    print("motor stop")
    Motor1.stop()
    print(0)
    Motor1.callback(5)
    #Motor2.stop()
    time.sleep(1)
except KeyboardInterrupt:
    Motor1.stop()
    #Motor2.stop()
    GPIO.cleanup()

GPIO.cleanup()


