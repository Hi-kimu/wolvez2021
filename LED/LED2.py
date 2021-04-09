import RPi.GPIO as GPIO
from time import sleep

class LED_light:
    def __init__(self, pin):
        self.pin = pin
    
    def set_GPIO(self):        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)

    def run_GPIO(self):
        try:
            while True:
                GPIO.output(self.pin, GPIO.HIGH)
                sleep(0.5)
                GPIO.output(self.pin, GPIO.LOW)
                sleep(0.5)
                
        except KeyboardInterrupt:
            GPIO.output(self.pin, GPIO.LOW)
            GPIO.cleanup()
            pass
p1 = LED_light(2)
p1.set_GPIO()
p1.run_GPIO()



