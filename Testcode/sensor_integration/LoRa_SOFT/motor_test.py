import motor_class
import RPi.GPIO as GPIO
import time 

GPIO.setwarnings(False)
Motor = motor_class.motor(5,6,13)

print("motor run")
Motor.go(100)
time.sleep(3)
print("motor stop")
Motor.stop()
time.sleep(3)

GPIO.cleanup()
