import servomotor
import RPi.GPIO as GPIO
import time 

GPIO.setwarnings(False)
servomotor = servomotor.servomotor(25)


try:
    #while True:
    print("servomotor run")
    #servomotor.servo_angle(-90)               #サーボモータ -90°
    #time.sleep(1)
    #servomotor.stop()
    #servomotor.servo_angle(10)                 #サーボモータ  0°
    #time.sleep(1)
    servomotor.servo_angle(90)
    servomotor.stop()
        
except KeyboardInterrupt:
    GPIO.cleanup()
    #servomotor.servo_angle(0) 
    servomotor.stop()
