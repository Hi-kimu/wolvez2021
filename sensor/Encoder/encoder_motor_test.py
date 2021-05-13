import encoder_motor
import RPi.GPIO as GPIO
import time 

GPIO.setwarnings(False)
Motor1 = encoder_motor.motor(19,26,5,6,13)
#Motor2 = motor.motor(20,21,12)

try:
    print("motor run") 
    Motor1.go(90)
    print("speed90")
    Motor1.callback(5)
    Motor1.callback(6)
    #Motor2.go(100)
    time.sleep(3)
    print("speed90")
    Motor1.callback(5)
    Motor1.callback(6)
    
    time.sleep(3)
    Motor1.go(40)
    print("speed40")
    Motor1.callback(5)
    Motor1.callback(6)
    time.sleep(3)
    
    Motor1.go(10)
    print("speed10")
    Motor1.callback(5)
    Motor1.callback(6)
    time.sleep(3)

    #Motor.back(100)
    #time.sleep(3)
    print("motor stop")
    Motor1.stop()
    print(0)
    Motor1.callback(5)
    Motor1.callback(6)
    #Motor2.stop()
    time.sleep(1)
except KeyboardInterrupt:
    Motor1.stop()
    #Motor2.stop()
    GPIO.cleanup()

GPIO.cleanup()


