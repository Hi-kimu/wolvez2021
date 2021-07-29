# -*- coding: utf-8 -*-
"""
Keio Wolve'Z cansat2021
mission function
Author Hikaru Kimura
last update:2021/6/30

"""

#ライブラリの読み込み
import time
import RPi.GPIO as GPIO
import sys
import numpy as np
import datetime
import os
import csv

#クラス読み込み
import constant as ct
import gps
import motor
import estimation
import radio
import bno055
import led
import servomotor



class Cansat(object):
    
    def __init__(self):
        #オブジェクトの生成
        self.rightmotor = motor.motor(ct.const.RIGHT_MOTOR_IN1_PIN,ct.const.RIGHT_MOTOR_IN2_PIN,ct.const.RIGHT_MOTOR_VREF_PIN)
        self.leftmotor = motor.motor(ct.const.LEFT_MOTOR_IN1_PIN,ct.const.LEFT_MOTOR_IN2_PIN,ct.const.LEFT_MOTOR_VREF_PIN)
        self.encoder = estimation.estimation(ct.const.RIGHT_MOTOR_ENCODER_A_PIN,ct.const.RIGHT_MOTOR_ENCODER_B_PIN,ct.const.LEFT_MOTOR_ENCODER_A_PIN,ct.const.LEFT_MOTOR_ENCODER_B_PIN)

        self.servomotor = servomotor.servomotor(ct.const.SERVOMOTOR_PIN)
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
        
        #オドメトリ用の変数
        self.x=0
        self.y=0
        self.q=0
        self.t1=0
        self.t2=0 
     
        #n点測位用の変数
        self.meanCansatRSSI=0
        self.meanLostRSSI=0
        self.LogCansatRSSI=list()
        self.LogLostRSSI=list()
        self.n_dis_LogCansatRSSI=list()
        self.n_dis_LogLostRSSI=list()
        self.n_meandisLog=list()
        self.n_LogCansatRSSI=list()
        self.n_LogLostRSSI=list()
     
        #stateに入っている時刻の初期化
        self.preparingTime = 0
        self.flyingTime = 0
        self.droppingTime = 0
        self.landingTime = 0
        self.pre_motorTime = 0
        self.startingTime = 0
        self.measureringTime = 0
        self.runningTime = 0
        self.positioningTime = 0
        
        #state管理用変数初期化
        self.countPreLoop = 0
        self.countFlyLoop = 0
        self.countDropLoop = 0
        self.countSwitchLoop=0
        self.countGoal = 0
        self.countgrass=0
        
        #GPIO設定
        GPIO.setmode(GPIO.BCM) #GPIOの設定
        GPIO.setup(ct.const.FLIGHTPIN_PIN,GPIO.IN) #フライトピン用
        
        date = datetime.datetime.now()
        self.filename = '{0:%Y%m%d}'.format(date)
        self.filename_hm = '{0:%Y%m%d%H%M}'.format(date)
        
        #csv
        self.cansatrssi=list()
        self.lostrssi=list()
        
        if not os.path.isdir('/home/pi/Desktop/wolvez2021/Testcode/Integration/%s' % (self.filename)):
            os.mkdir('/home/pi/Desktop/wolvez2021/Testcode/Integration/%s' % (self.filename))
            
  
    
    def setup(self):
        self.gps.setupGps()
        self.radio.setupRadio()
        self.bno055.setupBno()

        if self.bno055.begin() is not True:
            print("Error initializing device")
            exit()
   
    def sensor(self):
        self.timer = 1000*(time.time() - self.startTime) #経過時間 (ms)
        self.timer = int(self.timer)
        self.gps.gpsread()
        self.bno055.bnoread()
        
        self.t1=time.time()
        self.encoder.est_v_w(ct.const.RIGHT_MOTOR_ENCODER_A_PIN,ct.const.LEFT_MOTOR_ENCODER_A_PIN)#return self.encoder.cansat_speed, self.encoder.cansat_rad_speed
        self.t2=time.time()
        self.x,self.y,self.q=self.encoder.odometri(self.encoder.cansat_speed,self.encoder.cansat_rad_speed,self.t2-self.t1,self.x,self.y,self.q)
        
        self.writeData()#txtファイルへのログの保存
        
        
        if not self.state == 1: #preparingのときは電波を発しない
            #self.sendRadio()#LoRaでログを送信
            #self.switchRadio()
            pass

    def integ(self):#センサ統合用
        self.rightmotor.go(80)
        self.leftmotor.go(80)
              
    def keyboardinterrupt(self):
        self.RED_LED.led_on()
        self.BLUE_LED.led_off()
        self.GREEN_LED.led_off()
        self.rightmotor.stop()
        self.leftmotor.stop()

    def writeData(self):
        self.Ax=round(self.bno055.Ax,3)
        self.Ay=round(self.bno055.Ay,3)
        self.Az=round(self.bno055.Az,3)
        self.gx=round(self.bno055.gx,3)
        self.gy=round(self.bno055.gy,3)
        self.gz=round(self.bno055.gz,3)
        
        #ログデータ作成。\マークを入れることで改行してもコードを続けて書くことができる
        
        datalog = str(self.timer) + ","\
                  + str(self.rightmotor.velocity).rjust(6) + ","\
                  + str(self.leftmotor.velocity).rjust(6) + ","\
                  + str(self.encoder.cansat_speed).rjust(6) + ","\
                  + str(self.encoder.cansat_rad_speed).rjust(6) + ","\
                  + str(self.x).rjust(6) + ","\
                  + str(self.y).rjust(6) + ","\
                  + str(self.q).rjust(6) 
#                   + str(self.state) + ","\
#                   + str(self.gps.Time) + ","\
#                   + str(self.gps.Lat).rjust(6) + ","\
#                   + str(self.gps.Lon).rjust(6) + ","\
#                   + str(self.Ax).rjust(6) + ","\
#                   + str(self.Ay).rjust(6) + ","\
#                   + str(self.Az).rjust(6) + ","\
                  
#                   + str(self.gx).rjust(6) + ","\
#                   + str(self.gy).rjust(6) + ","\
#                   + str(self.gz).rjust(6) 
#         datalog = str(self.radio.cansat_rssi) + ","\
#                   + str(self.radio.lost_rssi)
        print(datalog)

        '''
        if self.countSwitchLoop > ct.const.SWITCH_LOOP_THRE-1:
            datalog = str(self.radio.cansat_rssi) + ","\
                      + str(self.radio.lost_rssi) + ","\
                      + str(np.mean(self.LogCansatRSSI)) + ","\
                      + str(np.mean(self.LogLostRSSI)) + ","\
                      + str(np.std(self.LogCansatRSSI)) + ","\
                      + str(np.std(self.LogLostRSSI))+","\
                      + "finish"
            print(self.meanCansatRSSI)
        

#         
#         if self.countSwitchLoop > ct.const.SWITCH_LOOP_THRE-1:
#             datalog = str(self.radio.cansat_rssi) + ","\
#                       + str(self.radio.lost_rssi) + ","\
#                       + str(np.mean(self.LogCansatRSSI)) + ","\
#                       + str(np.mean(self.LogLostRSSI)) + ","\
#                       + str(np.std(self.LogCansatRSSI)) + ","\
#                       + str(np.std(self.LogLostRSSI))+","\
#                       + "finish"
#             print(self.meanCansatRSSI)
#         

        
        with open('/home/pi/Desktop/wolvez2021/Testcode/Integration/%s/%s.txt' % (self.filename,self.filename_hm),mode = 'a') as test: # [mode] x:ファイルの新規作成、r:ファイルの読み込み、w:ファイルへの書き込み、a:ファイルへの追記
            test.write(datalog + '\n')
            
        '''
        self.cansatrssi.append(str(self.radio.cansat_rssi))
        self.lostrssi.append(str(self.radio.lost_rssi))
        
        if self.countSwitchLoop > ct.const.SWITCH_LOOP_THRE-1:
            
            self.cansatrssi.append(str(self.radio.cansat_rssi))
            self.lostrssi.append(str(self.radio.lost_rssi))
            
                       
            self.cansatrssi.insert(0,str(np.mean(self.LogCansatRSSI)))
            self.lostrssi.insert(0, str(np.mean(self.LogLostRSSI)))
            
            self.cansatrssi.insert(1,str(np.std(self.LogCansatRSSI)))
            self.lostrssi.insert(1,str(np.std(self.LogLostRSSI)))
            
                        #定義式より推定
#             N=2
#             MP=-45
#             cansatestimate_definition=10**((MP-meancansatrssi)/(10*N))
#             lostestimate_definition=10**((MP-meanlostrssi)/(10*N))
#             
#             self.cansatrssi.insert(2,str(cansatestimate_definition))
#             self.lostrssi.insert(2,str(lostestimate_definition))
#             print('カンサット:定義式からの推定'+cansatestimate_definition)
#             print('ロスト機:定義式からの推定'+lostestimate_definition)
            
            
            position = input("position(m):")
            self.cansatrssi.insert(0, position + "m")
            self.lostrssi.insert(0, position + "m")
            self.cansatrssi.insert(0, "cansat")
            self.lostrssi.insert(0, "lost")    
            
            
            with open("%s/%s.csv" % (self.filename,self.filename_hm), "a", encoding='utf-8') as f: # 文字コードをShift_JISに指定 'a':末尾に追加
                writer = csv.writer(f, lineterminator='\n') # writerオブジェクトの作成 改行記号で行を区切る
                writer.writerow(self.cansatrssi) # csvファイルに書き込み
                writer.writerow(self.lostrssi)  
            
            self.cansatrssi=list()
            self.lostrssi=list()
#         ------------------------------------------------------------------------------------------
    
    
    def sendRadio(self):
        datalog = str(self.state) + ","\
                  + str(self.gps.Time) + ","\
                  + str(self.gps.Lat) + ","\
                  + str(self.gps.Lon) + ","\
                  #+ str(self.rightmotor.velocity) + ","\
                  #+ str(self.leftmotor.velocity)
        self.radio.sendData(datalog) #データを送信
        
    def switchRadio(self):
        datalog = str(self.state) + ","\
                  + str(self.gps.Time) + ","\
                  + str(self.gps.Lat) + ","\
                  + str(self.gps.Lon) + ","\
                  #+ str(self.rightmotor.velocity) + ","\
                  #+ str(self.leftmotor.velocity)
        self.radio.switchData(datalog) #データを送信    
    
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
            self.starting()
        elif self.state == 5:
            self.measuring()
        elif self.state == 6:
            self.running()
        elif self.state == 7:
            self.positioning()
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
        
        
        if GPIO.input(ct.const.FLIGHTPIN_PIN) == GPIO.HIGH:#highかどうか＝フライトピンが外れているかチェック
            self.countFlyLoop+=1
            if self.countFlyLoop > ct.const.COUNT_FLIGHTPIN_THRE:#一定時間HIGHだったらステート移行
                self.state = 2
                self.laststate = 2
                
        else:
            self.countFlyLoop = 0 #何故かLOWだったときカウントをリセット
    
            
    def dropping(self):
        if self.droppingTime == 0:#時刻を取得してLEDをステートに合わせて光らせる
            self.droppingTime = time.time()
            self.RED_LED.led_on()
            self.BLUE_LED.led_on()
            self.GREEN_LED.led_off()         
            
            
        #加速度が小さくなったら着地判定
        if (pow(self.bno055.Ax,2) + pow(self.bno055.Ay,2) + pow(self.bno055.Az,2)) < pow(ct.const.ACC_THRE,2):#加速度が閾値以下で着地判定
            self.countDropLoop+=1
            if self.countDropLoop > ct.const.COUNT_ACC_LOOP_THRE:
                self.state = 3
                self.laststate = 3
        else:
            self.countDropLoop = 0 #初期化の必要あり
            
            
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
            self.RED_LED.led_off()
            self.BLUE_LED.led_off()
            self.GREEN_LED.led_on()
        
        if not self.landingTime == 0:
            if self.landstate == 0:
                self.servomotor.servo_angle(90)#サーボモータ動かしてパラ分離
                self.servomotor.stop()
                if time.time()-self.landingTime > ct.const.RELEASING_TIME_THRE:
                    #self.servomotor.servo_angle(0)
                    self.pre_motorTime = time.time()
                    self.landstate = 1
            #一定時間モータを回してパラシュートから離れる
            elif self.landstate == 1:
                self.rightmotor.go(80)
                self.leftmotor.go(80)
                
                if time.time()-self.pre_motorTime > ct.const.PRE_MOTOR_TIME_THRE:
                    self.rightmotor.stop()
                    self.leftmotor.stop()
                    self.state = 4
                    self.laststate = 4
                else:
                    pass
    
    def starting(self):
        if self.startingTime == 0:#時刻を取得してLEDをステートに合わせて光らせる
            self.waitingTime = time.time()
            self.RED_LED.led_on()
            self.BLUE_LED.led_off()
            self.GREEN_LED.led_on()
        else:
            self.countDistanceLoopStart=0
            
    def measuring(self):
        if self.measureringTime == 0:#時刻を取得してLEDをステートに合わせて光らせる
            self.measureringTime = time.time()
            self.RED_LED.led_off()
            self.BLUE_LED.led_on()
            self.GREEN_LED.led_on()
        else:
            if self.countSwitchLoop < ct.const.SWITCH_LOOP_THRE:
                #self.switchRadio()#LoRaでログを送信
                self.LogCansatRSSI += [self.radio.cansat_rssi]
                self.LogLostRSSI += [self.radio.lost_rssi]
                self.countSwitchLoop+=1
            else:
                #RSSIの平均とって距離計算
                self.meanCansatRSSI=np.mean(self.LogCansatRSSI)
                self.meanLostRSSI=np.mean(self.LogLostRSSI)
                '''
                self.distanceCansatRSSI=self.radio.----(self.meanCansatRSSI)
                self.distanceLostRSSI=self.radio.----(self.meanLostRSSI)
                self.n_dis_LogCansatRSSI.append(self.distanceCansatRSSI)
                self.n_dis_LogLostRSSI.append(self.distanceLostRSSI)
                self.meandis=(self.distanceCansatRSSI+self.distanceLostRSSI)/2
                self.n_meandisLog.append(self.meandis)
                
                '''
                
                #RSSIのデータ保管
                self.n_LogCansatRSSI.append(self.LogCansatRSSI)
                self.n_LogCansatRSSI.append(self.LogLostRSSI)
                
                self.meanCansatRSSI=0
                self.meanLostRSSI=0
                self.mesureringTime = 0
                self.countSwitchLoop = 0
                self.LogCansatRSSI=[]
                self.LogLostRSSI=[]
                self.state = 5
                self.laststate = 5
            
        
    
    def running(self):
        if self.runningTime == 0:#時刻を取得してLEDをステートに合わせて光らせる
            self.runningTime = time.time()
            self.RED_LED.led_on()
            self.BLUE_LED.led_on()
            self.GREEN_LED.led_on()
        
        
    def positioning(self):
        if self.positioningTime == 0:#時刻を取得してLEDをステートに合わせて光らせる
            self.goalTime = time.time()
            self.RED_LED.led_on()
            self.BLUE_LED.led_off()
            self.GREEN_LED.led_off()
            
            self.rightmotor.stop()
            self.leftmotor.stop()
           

if __name__ == "__main__":
    pass
