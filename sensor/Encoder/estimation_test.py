import encoder_motor
import motor
import estimation2
import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
Motor1 = motor.motor(6,5,13)
Motor2 = motor.motor(27,22,17)
Encoder = estimation2.estimation(19,26)
Encoder2 = estimation2.estimation(20,21)
#Motor2 = motor.motor(20,21,12)

try:
    print("motor run") 
    Motor1.go(90)
    Motor2.go(60)
    #print("-------------speed60----------------")
    while True:
        #Encoder.callback(19)
        v1=Encoder.callback(19)
        v2=Encoder2.callback(27)
        print(v1)
        print(v2)
        """
        Motor1.callback(19)
        Motor1.callback(26)
        Motor2.callback(20)
        Motor2.callback(21)
        """
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



