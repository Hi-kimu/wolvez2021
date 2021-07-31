#Last Update 2021/06/30
#Hikaru Kimura

import const

#ピン番号の指定
const.LEFT_MOTOR_ENCODER_A_PIN = 19
const.LEFT_MOTOR_ENCODER_B_PIN = 26
const.LEFT_MOTOR_VREF_PIN = 13
const.LEFT_MOTOR_IN1_PIN = 5
const.LEFT_MOTOR_IN2_PIN = 6
const.RIGHT_MOTOR_ENCODER_A_PIN = 8
const.RIGHT_MOTOR_ENCODER_B_PIN = 7
const.RIGHT_MOTOR_VREF_PIN = 12
const.RIGHT_MOTOR_IN1_PIN = 16
const.RIGHT_MOTOR_IN2_PIN = 20
const.SERVOMOTOR_PIN = 25
const.RED_LED_PIN = 9
const.BLUE_LED_PIN = 10
const.GREEN_LED_PIN = 11
const.RELEASING_PIN = 26
const.FLIGHTPIN_PIN = 4

#閾値
const.PREPARING_TIME_THRE = 10
const.FLYING_TIME_THRE = 10
const.ACC_THRE = 1 #加速度の値
const.COUNT_ACC_LOOP_THRE = 200
const.COUNT_FLIGHTPIN_THRE = 10
const.LANDING_TIME_THRE = 5
const.RELEASING_TIME_THRE = 30
const.PRE_MOTOR_TIME_THRE = 5
const.SWITCH_LOOP_THRE = 3 #1地点での測位回数
const.COUNT_GOAL_LOOP_THRE = 50
const.ANGLE_THRE = 10
const.ANGLE_COUNT_THRE = 10 

const.SHADOW_EDGE_LENGTH = 15
const.MEASURMENT_INTERVAL = 5
const.MAX_SHADOW_EDGE_LENGTH = 5

const.MAX_MEASURING_COUNT = 10
