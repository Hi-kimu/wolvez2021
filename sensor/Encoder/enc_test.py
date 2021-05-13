import RPi.GPIO as GPIO
import RPi.GPIO as GPIO
import time
import math

pin_a=19
pin_b=26
 
pin_pwm=13
pin_m1=6
pin_m2=5
pwm=None
 
prev_data=0
angle=0.
prev_angle=0.
delta=360/15

 
 
def main():
    init()
 
    try:
        while(True):
            motor_cntl()
            time.sleep(0.1)
    except KeyboardInterrupt:
        print ("break")
        GPIO.remove_event_detect(pin_a)
        GPIO.remove_event_detect(pin_b)
        GPIO.cleanup()
 
def init():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin_a, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(pin_b, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    GPIO.setup(pin_pwm, GPIO.OUT)
    GPIO.setup(pin_m1, GPIO.OUT)
    GPIO.setup(pin_m2, GPIO.OUT)
    global pwm, prev_a, prev_b
    pwm=GPIO.PWM(pin_pwm, 100)
    pwm.start(100)
 
    GPIO.add_event_detect(pin_a, GPIO.BOTH, callback=callback)
    GPIO.add_event_detect(pin_b, GPIO.BOTH, callback=callback)
 
    GPIO.output(pin_m1, GPIO.LOW)
    GPIO.output(pin_m2, GPIO.HIGH)
    
def motor_cntl():
    global angle
 
    if angle>180:
        GPIO.output(pin_m1, GPIO.HIGH)
        GPIO.output(pin_m2, GPIO.LOW)
    elif angle<-180:
        GPIO.output(pin_m1, GPIO.LOW)
        GPIO.output(pin_m2, GPIO.HIGH)   
    
def callback(gpio_pin):
    global angle, prev_data, prev_angle
 
    current_a=GPIO.input(pin_a)
    current_b=GPIO.input(pin_b)
 
    encoded=(current_a<<1)|current_b
    #print("EEEEEEEE",bin(encoded))
    sum=(prev_data<<2)|encoded
    
    print(bin(sum))
    if (sum==0b0010 or sum==0b1011 or sum==0b1101 or sum==0b0100):
        angle+=delta
        print ("plus", gpio_pin, angle)
    elif(sum==0b0001 or sum==0b0111 or sum==0b1110 or sum==0b1000):
        angle-=delta
        print ("minus", gpio_pin, angle)
    
    
    w_r=(angle-prev_angle)/0.1
    print("-----w_speed------",w_r)
    
    prev_data=encoded
    prev_angle = angle
 
if __name__ == "__main__":   
    main()