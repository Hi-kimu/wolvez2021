import motor
import RPi.GPIO as GPIO
import time 

GPIO.setwarnings(False)
Motor1 = motor.motor(6,5,13)
Motor2 = motor.motor(20,16,12)

try:
    print("motor run")
#     while True:
#         
#         for i in range (30,100):
#             Motor1.go(i)
#             Motor2.go(i)
#             time.sleep(0.1)
#             
#         for i in reversed(range(30,100)):
#             Motor1.go(i)
#             Motor2.go(i)
#             time.sleep(0.1)
                
#     Motor1.back(100)
#     Motor2.back(70)
#     time.sleep(2)
    
    Motor1.go(80)
    Motor2.go(80)
    time.sleep(100)
    
#     
#  #   Motor1.back(85)
# #   Motor2.back(85)
# 
#     time.sleep(100)
# 
#     #Motor.back(100)
#     #time.sleep(3)
    print("motor stop")
    Motor1.stop()
    Motor2.stop()
    time.sleep(0.5)
except KeyboardInterrupt:
    print("motor stop")
    Motor1.stop()
    Motor2.stop()
    GPIO.cleanup()

GPIO.cleanup()