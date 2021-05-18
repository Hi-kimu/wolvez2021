import servomotor
import RPi.GPIO as GPIO
import time 

GPIO.setwarnings(False)
servomotor = servomotor.servomotor(18)

while True:
    try:
        print("servomotor run")
        servomotor.servo_angle(-90)               #サーボモータ -90°
        #servomotor.servo_angle(-60)               #サーボモータ -60°
        #servomotor.servo_angle(-30)               #サーボモータ -30°
        servomotor.servo_angle(0)                 #サーボモータ  0°
        #servomotor.servo_angle(30)                #サーボモータ  30°
        #servomotor.servo_angle(60)                #サーボモータ  60°
        servomotor.servo_angle(90)
        '''
        servomotor.servo_angle()
        time.sleep(3)
        servomotor.mid()
        time.sleep(3)
        servomotor.left()
        '''
    except KeyboardInterrupt:
        GPIO.cleanup()
        servomotor.stop()
