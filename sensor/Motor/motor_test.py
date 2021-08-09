import motor
import RPi.GPIO as GPIO
import time 

GPIO.setwarnings(False)
Motor1 = motor.motor(5,6,13)
Motor2 = motor.motor(16,20,12)

try:
    print("motor run") 

    Motor1.go(85)
    Motor2.go(85)
 #   Motor1.back(85)
#   Motor2.back(85)

    time.sleep(20)

    #Motor.back(100)
    #time.sleep(3)
    print("motor stop")
    Motor1.stop()
    Motor2.stop()
    time.sleep(1)
except KeyboardInterrupt:
    Motor1.stop()
    Motor2.stop()
    GPIO.cleanup()

GPIO.cleanup()
