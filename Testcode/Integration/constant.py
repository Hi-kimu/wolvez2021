#Last Update 2021/08/10
#Hikaru Kimura

import const

#Pin Number
const.LEFT_MOTOR_ENCODER_A_PIN = 8#7
const.LEFT_MOTOR_ENCODER_B_PIN = 7#8
const.LEFT_MOTOR_VREF_PIN = 12
const.LEFT_MOTOR_IN1_PIN = 16#20
const.LEFT_MOTOR_IN2_PIN = 20#16
const.RIGHT_MOTOR_ENCODER_A_PIN = 19#26
const.RIGHT_MOTOR_ENCODER_B_PIN = 26#19
const.RIGHT_MOTOR_VREF_PIN = 13
const.RIGHT_MOTOR_IN1_PIN = 5#6
const.RIGHT_MOTOR_IN2_PIN = 6#5
const.SERVOMOTOR_PIN = 25
const.RED_LED_PIN = 9
const.BLUE_LED_PIN = 10
const.GREEN_LED_PIN = 11
const.RELEASING_PIN = 26
const.FLIGHTPIN_PIN = 4

#Variable Threshold
const.ANGLE_THRE = 10
const.SHADOW_EDGE_LENGTH = 15
const.MEASURMENT_INTERVAL = 500000000000 #測位点間距離
const.MAX_SHADOW_EDGE_LENGTH = 5
const.CASE_DISCRIMINATION = 2 #Case判定における許容誤差
const.START_CONST_SHORT = 0.5 #Startingステートにおける帯の幅　±0.5
const.START_CONST_LONG = 5 #Startingステートにおける帯の幅　±5


#State Threshold
const.PREPARING_GPS_COUNT_THRE= 50
const.PREPARING_TIME_THRE = 60#150
const.FLYING_FLIGHTPIN_COUNT_THRE = 10#800
const.DROPPING_ACC_COUNT_THRE = 50
const.DROPPING_ACC_THRE = 1 #加速度の値
const.LANDING_RELEASING_TIME_THRE = 3
const.LANDING_PRE_MOTOR_THRE = 50
const.LANDING_PRE_MOTOR_TIME_THRE = 1
const.STARTING_TIME_THRE = 60
const.MEASURING_SWITCH_COUNT_THRE = 20#1地点での測位回数
const.MEASURING_MAX_MEASURING_COUNT_THRE = 6 #=最大測位点-1
const.RUNNiNG_STUCK_ACC_THRE = 0.005
const.ACC_COUNT = 7 #スタック判定する加速度の個数
const.ODOMETRI_BACK=5
