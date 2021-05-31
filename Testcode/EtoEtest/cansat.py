# -*- coding: utf-8 -*-
"""
Keio Wolve'Z cansat2021
mission function
Author Hikaru Kimura
last update:2021/5/31

"""

#ライブラリの読み込み
import time
import RPi.GPIO as GPIO
import sys
import numpy as np
import datetime

#クラス読み込み
import constant as ct
import gps
import motor
import radio
import bno055
import led

class Cansat(object):
    
    def __init__(self):
        #オブジェクトの生成
        self.rightmotor = motor.motor(ct.const.RIGHT_MOTOR_IN1_PIN,ct.const.RIGHT_MOTOR_IN2_PIN,ct.const.RIGHT_MOTOR_VREF_PIN)
        self.leftmotor = motor.motor(ct.const.LEFT_MOTOR_IN1_PIN,ct.const.LEFT_MOTOR_IN2_PIN,ct.const.LEFT_MOTOR_VREF_PIN)
        self.gps = gps.GPS()
        self.bno055 = bno055.BNO055()
        self.radio = radio.radio()
        self.RED_LED = led.led(ct.const.RED_LED_PIN)
        self.BLUE_LED = led.led(ct.const.BLUE_LED_PIN)
        self.GREEN_LED = led.led(ct.const.GREEN_LED_PIN)
        
        #開始時間の記録
        self.startTime = time.time()
        self.timer = 0
        self.landstate = 0 #landing stateの中でモータを一定時間回すためにlandのなかでもステート管理するため
        self.v_right = 100
        self.v_left = 100
        
        #変数
        self.state = 0
        self.laststate = 0
        self.landstate = 0
     
        #stateに入っている時刻の初期化
        self.preparingTime = 0
        self.flyingTime = 0
        self.droppingTime = 0
        self.landingTime = 0
        self.pre_motorTime = 0
        self.waitingTime = 0
        self.runningTime = 0
        self.goalTime = 0
        
        #state管理用変数初期化
        self.countPreLoop = 0
        self.countFlyLoop = 0
        self.countDropLoop = 0
        self.countGoal = 0
        self.countAreaLoopEnd=0 # 終了判定用
        self.countAreaLoopStart=0 # 開始判定用
        self.countAreaLoopLose=0 # 見失い判定用
        self.countgrass=0
        
        #GPIO設定
        GPIO.setmode(GPIO.BCM) #GPIOの設定
        GPIO.setup(ct.const.FLIGHTPIN_PIN,GPIO.IN) #フライトピン用
        
        date = datetime.datetime.now()
        self.filename = '{0:%Y%m%d}'.format(date)
    
    def setup(self):
        #self.gps.setupGps()
        #self.radio.setupRadio()
        '''
        self.bno055.setupBno()

        if self.bno055.begin() is not True:
            print("Error initializing device")
            exit()
   '''
    def sensor(self):
        self.timer = 1000*(time.time() - self.startTime) #経過時間 (ms)
        self.timer = int(self.timer)
        #self.gps.gpsread()
        #self.bno055.bnoread()
        self.writeData()#txtファイルへのログの保存
        '''
        if not self.state == 1: #preparingのときは電波を発しない
            self.sendRadio()#LoRaでログを送信
            '''
    
    def writeData(self):
        '''
        self.Ax=round(self.bno055.Ax,3)
        self.Ay=round(self.bno055.Ay,3)
        self.Az=round(self.bno055.Az,3)
        
        #ログデータ作成。\マークを入れることで改行してもコードを続けて書くことができる
        datalog = str(self.timer) + ","\
                  + str(self.state) + ","\
                  + str(self.gps.Time) + ","\
                  + str(self.gps.Lat).rjust(6) + ","\
                  + str(self.gps.Lon).rjust(6) + ","\
                  + str(self.Ax).rjust(6) + ","\
                  + str(self.Ay).rjust(6) + ","\
                  + str(self.Az).rjust(6) + ","\
                  + str(self.rightmotor.velocity).rjust(6) + ","\
                  + str(self.leftmotor.velocity).rjust(6)
        '''
        datalog=str(self.timer) + ","\
                  + str(self.state)
        print(datalog)
        
        '''
        with open('/home/pi/Desktop/wolvez2021/Testcode/EtoEtest/%s/%s.txt' % (self.filename,self.filename),mode = 'a') as test: # [mode] x:ファイルの新規作成、r:ファイルの読み込み、w:ファイルへの書き込み、a:ファイルへの追記
            test.write(datalog + '\n')
            '''
    
    
    def sendRadio(self):
        datalog = str(self.state) + ","\
                  + str(self.gps.Time) + ","\
                  + str(self.gps.Lat) + ","\
                  + str(self.gps.Lon) + ","\
                  #+ str(self.rightmotor.velocity) + ","\
                  #+ str(self.leftmotor.velocity)
        self.radio.sendData(datalog) #データを送信
    
    def sequence(self):
        if self.state == 0:
            self.preparing()
        elif self.state == 1:
            self.flying()
        elif self.state == 2:
            self.dropping()
        elif self.state == 3:
            self.landing()
        elif self.state == 4:
            self.waiting()
        elif self.state == 5:
            self.running()
        elif self.state == 6:
            self.goal()
        else:
            self.state = self.laststate #どこにも引っかからない場合何かがおかしいのでlaststateに戻してあげる
    
    def preparing(self):#フライトピンを使う場合はいらないかも（暫定：時間が立ったら移行）
        if self.preparingTime == 0:
            self.preparingTime = time.time()#時刻を取得
            self.RED_LED.led_on()
            self.BLUE_LED.led_off()
            self.GREEN_LED.led_off()
            self.rightmotor.stop()
            self.leftmotor.stop()
        #self.countPreLoop+ = 1
        if not self.preparingTime == 0:
            if time.time() - self.preparingTime > ct.const.PREPARING_TIME_THRE:
                self.state = 1
                self.laststate = 1
    
    def flying(self):#フライトピンが外れたのを検知して次の状態へ以降
        if self.flyingTime == 0:#時刻を取得してLEDをステートに合わせて光らせる
            self.flyingTime = time.time()
            self.RED_LED.led_off()
            self.BLUE_LED.led_on()
            self.GREEN_LED.led_off()
            self.rightmotor.stop()
            self.leftmotor.stop()
        
        '''
        if GPIO.input(ct.const.FLIGHTPIN_PIN) == GPIO.HIGH:#highかどうか＝フライトピンが外れているかチェック
            self.countFlyLoop+=1
            if self.countFlyLoop > ct.const.COUNT_FLIGHTPIN_THRE:#一定時間HIGHだったらステート移行
                self.state = 2
                self.laststate = 2
                
        else:
            self.countFlyLoop = 0 #何故かLOWだったときカウントをリセット
    '''
        if not self.flyingTime == 0:#センサ統合試験用
            if time.time() - self.flyingTime > ct.const.PREPARING_TIME_THRE:
                self.state = 2
                self.laststate = 2
            
    def dropping(self):
        if self.droppingTime == 0:#時刻を取得してLEDをステートに合わせて光らせる
            self.droppingTime = time.time()
            self.RED_LED.led_off()
            self.BLUE_LED.led_off()
            self.GREEN_LED.led_on()         
            
        if not self.droppingTime == 0:#センサ統合試験用
            if time.time() - self.droppingTime > ct.const.PREPARING_TIME_THRE:
                self.state = 6
                self.laststate = 6
            '''
        #加速度が小さくなったら着地判定
        if (pow(self.bno055.Ax,2) + pow(self.bno055.Ay,2) + pow(self.bno055.Az,2)) < pow(ct.const.ACC_THRE,2):#加速度が閾値以下で着地判定
            self.countDropLoop+=1
            if self.countDropLoop > ct.const.COUNT_ACC_LOOP_THRE:
                self.state = 3
                self.laststate = 3
        else:
            self.countDropLoop = 0 #初期化の必要あり
            '''
        """
        #（予備）時間で着地判定
        if not self.droppingTime == 0:
            if time.time() - self.droppingTime > ct.const.LANDING_TIME_THRE:
                self.state = 3
                self.laststate = 3
        """
        
    def landing(self):
        if self.landingTime == 0:#時刻を取得してLEDをステートに合わせて光らせる
            self.landingTime = time.time()
            self.RED_LED.led_on()
            self.BLUE_LED.led_on()
            self.GREEN_LED.led_off()
        
        if not self.landingTime == 0:
            if self.landstate == 0:
                #GPIO.output(ct.const.RELEASING_PIN,1) #電圧をHIGHにして焼き切りを行う
                if time.time()-self.landingTime > ct.const.RELEASING_TIME_THRE:
                    #GPIO.output(ct.const.RELEASING_PIN,0) #焼き切りが危ないのでlowにしておく
                    self.pre_motorTime = time.time()
                    self.landstate = 1
            #焼き切りが終わったあと一定時間モータを回して分離シートから脱出
            elif self.landstate == 1:
                self.rightmotor.go(100)
                self.leftmotor.go(100)
                
                if time.time()-self.pre_motorTime > ct.const.PRE_MOTOR_TIME_THRE:
                    self.rightmotor.stop()
                    self.leftmotor.stop()
                    self.state = 4
                    self.laststate = 4
                else:
                    pass
    
    def waiting(self):
        if self.waitingTime == 0:#時刻を取得してLEDをステートに合わせて光らせる
            GPIO.output(ct.const.RELEASING_PIN,0) #焼き切りしっぱなしでは怖いので保険
            self.waitingTime = time.time()
            self.RED_LED.led_off()
            self.BLUE_LED.led_on()
            self.GREEN_LED.led_on()
        else:
            self.countDistanceLoopStart=0
    
    def running(self):
        if self.runningTime == 0:#時刻を取得してLEDをステートに合わせて光らせる
            self.runningTime = time.time()
            self.RED_LED.led_on()
            self.BLUE_LED.led_on()
            self.GREEN_LED.led_on()
        
        #以下に画像処理走行プログラム
        
    def goal(self):
        if self.goalTime == 0:#時刻を取得してLEDをステートに合わせて光らせる
            self.goalTime = time.time()
            self.RED_LED.led_off()
            self.BLUE_LED.led_off()
            self.GREEN_LED.led_off()
            
            self.rightmotor.stop()
            self.leftmotor.stop()
           

if __name__ == "__main__":
    pass
