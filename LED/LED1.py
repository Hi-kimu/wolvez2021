import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)
GPIO.setup(2, GPIO.OUT)

try:
    while True:
        GPIO.output(2, GPIO.HIGH)
        sleep(0.5)
        GPIO.output(2, GPIO.LOW)
        sleep(0.5)
        
except KeyboardInterrupt:
    GPIO.output(2, GPIO.LOW)
    GPIO.cleanup()
    pass
