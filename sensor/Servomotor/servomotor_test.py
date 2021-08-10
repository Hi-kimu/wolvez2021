import servomotor
import RPi.GPIO as GPIO
import time 

GPIO.setwarnings(False)
servomotor = servomotor.servomotor(25)


try:
    #while True:
    print("servomotor run")
    servomotor.servo_angle(90)#CLOSE
    time.sleep(3)
    servomotor.servo_angle(0)#OPEN
    time.sleep(3)    
    servomotor.stop()
    
except KeyboardInterrupt:
    GPIO.cleanup()
    #servomotor.servo_angle(0) 
    servomotor.stop()
