import servomotor
import RPi.GPIO as GPIO
import time 

GPIO.setwarnings(False)
servomotor = servomotor.servomotor(12)

try:
    print("servomotor run")
    servomotor.right()
    time.sleep(3)
    servomotor.mid()
    time.sleep(3)
    servomotor.left()
    
except KeyboardInterrupt:
    GPIO.cleanup()