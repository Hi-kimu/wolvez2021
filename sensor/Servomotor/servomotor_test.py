import servomotor
import RPi.GPIO as GPIO
import time 

GPIO.setwarnings(False)
servomotor = servomotor.servomotor(18)

while True:
    try:
        print("servomotor run")
        servomotor.servo_angle(-90)               #サーボモータ -90°
        servomotor.servo_angle(0)                 #サーボモータ  0°
        servomotor.servo_angle(90)
        
    except KeyboardInterrupt:
        GPIO.cleanup()
        servomotor.stop()
