import cansat
import RPi.GPIO as GPIO
can=cansat.Cansat()
#can.setup()
GPIO.setwarnings(False)
try:
    while True:
        #can.integ()
        print("motor run")
        can.motor_run()
        can.odometri()
        can.stuck_detection()
                        

except KeyboardInterrupt:
    print('finished')
    can.keyboardinterrupt()
    can.rightmotor.stop()
    can.leftmotor.stop()
    GPIO.cleanup()
    pass