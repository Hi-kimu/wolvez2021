# -*- coding: utf-8 -*-
"""
Keio Wolve'Z cansat2021
mission function
Author Hikaru Kimura
last update:2021/8/04

"""

#ライブラリの読み込み
import time
import RPi.GPIO as GPIO
import sys
import numpy as np
import datetime
import os
import csv
import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import statistics


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
        GPIO.setwarnings(False)
        #オブジェクトの生成
        self.countstuck = 0
        self.accdata=list()
        self.accdata_x=list()
        self.accdata_y=list()
        
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
        self.startstate = 0
        self.back_escape = 0
        self.pre_motor_count = 0
        
        #変数
        #self.state = 0
        self.laststate = 0
        
        self.k = 20 #for run 0 < error < 1
        self.ka = 0.1 #for angle change 0 < error < 180 
        self.v_ref = 70
        
        
        #基準点のGPS情報を取得
        self.gpscount=0
        self.startgps_lon=list()
        self.startgps_lat=list()
        
        #スタート地点移動用の緯度経度
        #cansatGPS
        self.startlon=139.6560500
        self.startlat=35.5549650
        
        #google map
        #self.startlon=139.6559749
        #self.startlat=35.5549795
        
        #永久影の設定15×15
        self.startpoint=[[-ct.const.MAX_SHADOW_EDGE_LENGTH                             , ct.const.SHADOW_EDGE_LENGTH/2],#スタート地点の設定
                         [ct.const.SHADOW_EDGE_LENGTH/2                                , ct.const.SHADOW_EDGE_LENGTH + ct.const.MAX_SHADOW_EDGE_LENGTH],
                         [ct.const.SHADOW_EDGE_LENGTH + ct.const.MAX_SHADOW_EDGE_LENGTH, ct.const.SHADOW_EDGE_LENGTH/2],
                         [ct.const.SHADOW_EDGE_LENGTH/2                                , -ct.const.MAX_SHADOW_EDGE_LENGTH]]
        #スタート地点の許容範囲[- 5 - 0.5 < x < - 5 + 0.5...]
        self.startshadowTHRE_x=[[self.startpoint[0][0] - ct.const.START_CONST_SHORT, self.startpoint[0][0] + ct.const.START_CONST_SHORT],
                                [self.startpoint[1][0] - ct.const.START_CONST_LONG , self.startpoint[1][0] + ct.const.START_CONST_LONG],
                                [self.startpoint[2][0] - ct.const.START_CONST_SHORT, self.startpoint[2][0] + ct.const.START_CONST_SHORT],
                                [self.startpoint[3][0] - ct.const.START_CONST_LONG , self.startpoint[3][0] + ct.const.START_CONST_LONG]]
        #スタート地点の許容範囲[7.5 - 5 < y < 7.5 + 5...]
        self.startshadowTHRE_y=[[self.startpoint[0][1] - ct.const.START_CONST_LONG , self.startpoint[0][1] + ct.const.START_CONST_LONG],
                                [self.startpoint[1][1] - ct.const.START_CONST_SHORT, self.startpoint[1][1] + ct.const.START_CONST_SHORT],
                                [self.startpoint[2][1] - ct.const.START_CONST_LONG , self.startpoint[2][1] + ct.const.START_CONST_LONG],
                                [self.startpoint[3][1] - ct.const.START_CONST_SHORT, self.startpoint[3][1] + ct.const.START_CONST_SHORT]]
        self.close_startpoint=-1
        self.starttheta=0
        self.startpointdis=list()
        self.anglestate=0
        
        #オドメトリ用の変数
        self.x = 0
        self.y = 0
        self.q = 0
        self.t_new = 0
        self.t_old = 0
        self.azimuth = [90, 0, 270, 180]
        self.case = -1
     
        #n点測位用の変数
        self.measureringTimeLog=list()
        self.measuringcount=0#n点測量目をこの変数で管理
        self.meanCansatRSSI=0
        self.meanLostRSSI=0
        self.LogData = list()
        self.n_LogData = list()
#         self.n_LogData = [[0],[0,7.834751202079564,-5.432902521540001,13.922119594581348,0.4769696007084729,0.6403124237432849,-73.15,-74.3]]
        
#         self._all = list()
        self.LogCansatRSSI=list()
        self.LogLostRSSI=list()
        self.n_dis_LogCansatRSSI=list()
        self.n_dis_LogLostRSSI=list()
        self.n_dis_LogCansatRSSI_2=list()
        self.n_dis_LogLostRSSI_2=list()
        self.n_meandisLog=list()
        self.n_LogCansatRSSI=list()
        self.n_LogLostRSSI=list()
        self.hazure = 5
        
        #探査機推定時用の変数
        self.X, self.Y = np.meshgrid(np.arange(-30, 31, 1), np.arange(-30, 31, 1))
        self.n_pdf=list()
        self.positioning_count=0
     
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
        self.finishTime = 0
        
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
        
        #servomotor close
#         self.servomotor.servo_angle(90)
#         time.sleep(0.3)
#         self.servomotor.stop()
        
        
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
#         self.gps.Lat = 35.5549482
#         self.gps.Lon = 139.6560942
        self.bno055.bnoread()
        self.Ax=round(self.bno055.Ax,3)
        self.Ay=round(self.bno055.Ay,3)
        self.Az=round(self.bno055.Az,3)
        self.ex=round(self.bno055.ex,3)
        self.gz=round(self.bno055.gz,3)
#         self.ex -= 90
#         if self.ex < 0:
#             self.ex += 360
        
        self.writeData()#txtファイルへのログの保存
    
        if not self.state == 1: #preparingのときは電波を発しない
            
            if not self.state ==5:#self.sendRadio()#LoRaでログを送信
                self.sendRadio()
            else:
                self.rightmotor.stop()
                self.leftmotor.stop()
                #self.switchRadio()
            
    def odometri(self):
        if self.t_new==0:
            self.t_new=time.time()
            
        self.encoder.est_v_w(ct.const.RIGHT_MOTOR_ENCODER_A_PIN,ct.const.LEFT_MOTOR_ENCODER_A_PIN)#return self.encoder.cansat_speed, self.encoder.cansat_rad_speed
        self.q=math.radians(self.ex) #加速度センサの値を姿勢角に使用
        self.t_old=self.t_new
        self.t_new=time.time()
        self.x,self.y,self.q=self.encoder.odometri(self.encoder.cansat_speed,self.encoder.cansat_rad_speed,self.t_new-self.t_old,self.x,self.y,self.q)
        self.q=math.radians(self.ex)

    def integ(self):#センサ統合用
        self.rightmotor.go(60)
        self.leftmotor.go(60)
              
    def keyboardinterrupt(self):
        self.RED_LED.led_on()
        self.BLUE_LED.led_off()
        self.GREEN_LED.led_off()
        self.rightmotor.stop()
        self.leftmotor.stop()

    def writeData(self):
        #ログデータ作成。\マークを入れることで改行してもコードを続けて書くことができる
                 
        print_datalog = str(self.timer) + ","\
                  + str(self.state) + ","\
                  + str(self.gps.Time) + ","\
                  + str(self.gps.Lat).rjust(6) + ","\
                  + str(self.gps.Lon).rjust(6) + ","\
                  + "rV:" + str(round(self.rightmotor.velocity,2)).rjust(6) + ","\
                  + "lV:" + str(round(self.leftmotor.velocity,2)).rjust(6) + ","\
                  + "x:" + str(round(self.x,2)).rjust(6) + ","\
                  + "y:" + str(round(self.y,2)).rjust(6) + ","\
                  + "q:" + str(self.ex).rjust(6)
        
        print(print_datalog)
        
        datalog = str(self.timer) + ","\
                  + str(self.state) + ","\
                  + str(self.gps.Time).rjust(7) + ","\
                  + str(self.gps.Lat).rjust(11) + ","\
                  + str(self.gps.Lon).rjust(11) + ","\
                  + str(self.Ax).rjust(6) + ","\
                  + str(self.Ay).rjust(6) + ","\
                  + str(self.Az).rjust(6) + ","\
                  + str(round(self.rightmotor.velocity,3)).rjust(6) + ","\
                  + str(round(self.leftmotor.velocity,3)).rjust(6) + ","\
                  + str(round(self.encoder.cansat_speed,4)).rjust(6) + ","\
                  + str(round(self.encoder.cansat_rad_speed,4)).rjust(6) + ","\
                  + str(round(self.x,3)).rjust(6) + ","\
                  + str(round(self.y,3)).rjust(6) + ","\
                  + str(self.ex).rjust(6) + ","\
                  + str(self.close_startpoint)+ ","\
                  + str(self.case)
            
        with open('/home/pi/Desktop/wolvez2021/Testcode/Integration/%s/%s.txt' % (self.filename,self.filename_hm),mode = 'a') as test: # [mode] x:ファイルの新規作成、r:ファイルの読み込み、w:ファイルへの書き込み、a:ファイルへの追記
            test.write(datalog + '\n')

            
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
        elif self.state == 8:
            self.modified_positioning()
        elif self.state == 9:
            self.finish()
        else:
            self.state = self.laststate #どこにも引っかからない場合何かがおかしいのでlaststateに戻してあげる
    
    def preparing(self):#時間が立ったら移行
        if self.preparingTime == 0:
            self.preparingTime = time.time()#時刻を取得
            self.RED_LED.led_on()
            self.BLUE_LED.led_off()
            self.GREEN_LED.led_off()
            self.rightmotor.stop()
            self.leftmotor.stop()
        #self.countPreLoop+ = 1
        if not self.preparingTime == 0:
#             if self.gpscount <= ct.const.PREPARING_GPS_COUNT_THRE:
            if self.gpscount <= 50:
                self.startgps_lon.append(float(self.gps.Lon))
                self.startgps_lat.append(float(self.gps.Lat))
                print(f"GPS {self.gps.Lon},{self.gps.Lat}")
                self.gpscount+=1
                print(self.gpscount)
                time.sleep(1)
                with open('/home/pi/Desktop/wolvez2021/Testcode/Integration/%s/%s_gps_pre.txt' % (self.filename,self.filename_hm),mode = 'a') as f: # [mode] x:ファイルの新規作成、r:ファイルの読み込み、w:ファイルへの書き込み、a:ファイルへの追記
                    f.write(f"GPS_pre {self.gps.Lon},{self.gps.Lat}"+ '\n')
                
            else:
                print("GPS completed!!")
            
            if time.time() - self.preparingTime > ct.const.PREPARING_TIME_THRE:
                self.startlon=np.mean(self.startgps_lon)
                self.startlat=np.mean(self.startgps_lat)
                print(f"startlon:{self.startlon}, startlat:{self.startlat}")
                #self.startlon=139.6560590
                #self.startlat=35.5550240
                self.state = 1
                self.laststate = 1
    
    def flying(self):#フライトピンが外れたのを検知して次の状態へ以降
        if self.flyingTime == 0:#時刻print(f"GPS {self.gps.Lon},{self..gps.Lat}")を取得してLEDをステートに合わせて光らせる
            self.flyingTime = time.time()
            self.RED_LED.led_off()
            self.BLUE_LED.led_on()
            self.GREEN_LED.led_off()
            self.rightmotor.stop()
            self.leftmotor.stop()
                
#                     # change
#         print(" stop for writing")
#         aaaaa = input()
#         self.state = 4   
                
        if GPIO.input(ct.const.FLIGHTPIN_PIN) == GPIO.HIGH:#highかどうか＝フライトピンが外れているかチェック
            self.countFlyLoop+=1
#             print(self.countFlyLoop)
            

            
            
            if self.countFlyLoop > ct.const.FLYING_FLIGHTPIN_COUNT_THRE:#一定時間HIGHだったらステート移行
                self.state = 2
                self.laststate = 2
               
        else:
            self.countFlyLoop = 0 #何故かLOWだったときカウントをリセット
    
            
    def dropping(self):
#         self.gps.vincenty_inverse(self.startlat,self.startlon,self.gps.Lat,self.gps.Lon)
#         self.x = self.gps.gpsdis*math.cos(math.radians(self.gps.gpsdegrees))
#         self.y = self.gps.gpsdis*math.sin(math.radians(self.gps.gpsdegrees))
        if self.droppingTime == 0:#時刻を取得してLEDをステートに合わせて光らせる
            self.droppingTime = time.time()
            self.RED_LED.led_on()
            self.BLUE_LED.led_on()
            self.GREEN_LED.led_off()
            
        self.servomotor.servo_angle(100)
        #加速度が小さくなったら着地判定
        if (pow(self.bno055.Ax,2) + pow(self.bno055.Ay,2) + pow(self.bno055.Az,2)) < pow(ct.const.DROPPING_ACC_THRE,2):#加速度が閾値以下で着地判定
            self.countDropLoop+=1
#             self.servomotor.servo_angle(20)
            
            if self.countDropLoop > ct.const.DROPPING_ACC_COUNT_THRE:
                if self.gz < 1:
                    print("Back Escape!!")
                    self.back_escape = 1
                self.state = 3
                self.laststate = 3
        else:
            self.countDropLoop = 0 #初期化の必要あり
        
    def landing(self):
#         self.gps.vincenty_inverse(self.startlat,self.startlon,self.gps.Lat,self.gps.Lon)#距離:self.gps.gpsdis 方位角:self.gps.gpsdegrees
#         self.x = self.gps.gpsdis*mprint(f"GPS {self.gps.Lon},{self..gps.Lat}")ath.cos(math.radians(self.gps.gpsdegrees))
#         self.y = self.gps.gpsdis*math.sin(math.radians(self.gps.gpsdegrees))
        if self.landingTime == 0:#時刻を取得してLEDをステートに合わせて光らせる
            self.landingTime = time.time()
            self.RED_LED.led_off()
            self.BLUE_LED.led_off()
            self.GREEN_LED.led_on()
        
        if not self.landingTime == 0:
            if self.landstate == 0:
#                 for i in range(0,10):
#                     self.servomotor.servo_angle(-10-10*i)#サーボモータ動かしてパラ分離
#                     time.sleep(0.1)
                for i in range(5):
                    self.servomotor.servo_angle(0)#サーボモータ動かしてパラ分離
                    #time.sleep(0.05)
                    
                if time.time()-self.landingTime > ct.const.LANDING_RELEASING_TIME_THRE:
                    self.servomotor.stop()
                    self.pre_motorBackTime = time.time()
                    self.landstate = 1
            #一定時間モータを回してパラシュートから離れる
            elif self.landstate == 1:
                if self.back_escape == 1:
                    print("Back Escape!!")
                    if time.time() - self.pre_motorBackTime < ct.const.LANDING_PRE_MOTOR_TIME_THRE:
                        self.rightmotor.back(70)
                        self.leftmotor.back(100)
                    else:
                        self.rightmotor.go(25)
                        self.leftmotor.back(25)
                        time.sleep(1)
                        self.back_escape = 0
                
                elif self.back_escape == 0:
                    print("Go Escape!!")
                    if self.pre_motor_count < ct.const.LANDING_PRE_MOTOR_THRE:
                        self.rightmotor.go(100)
                        self.leftmotor.go(100)
                        self.pre_motor_count += 1
                    else:
                        self.rightmotor.stop()
                        self.leftmotor.stop()
                        
                        self.state = 4
                        self.laststate = 4
                            
                      
    def starting(self):
        if self.startingTime == 0:#時刻を取得してLEDをステートに合わせて光らせる
            self.startingTime = time.time()
            self.RED_LED.led_on()
            self.BLUE_LED.led_off()
            self.GREEN_LED.led_on()
            self.startpointdis=list()
            self.measuringgps_lon=list()
            self.measuringgps_lat=list()
            self.gpscount = 0
                
            self.t_new=0
            self.gpscount=0
            
        else:#4つのスタート地点から一番近い点へ移動
            #原点と着陸地点の距離と方位角を取得
            
            if self.gpscount <= ct.const.PREPARING_GPS_COUNT_THRE:
                self.startgps_lon.append(float(self.gps.Lon))
                self.startgps_lat.append(float(self.gps.Lat))
                print("GPS count is " + str(self.gpscount))
                print(f"GPS {self.gps.Lon},{self.gps.Lat}")
                self.gpscount+=1
#                 time.sleep(1)
                with open('/home/pi/Desktop/wolvez2021/Testcode/Integration/%s/%s_gps_sta.txt' % (self.filename,self.filename_hm),mode = 'a') as f: # [mode] x:ファイルの新規作成、r:ファイルの読み込み、w:ファイルへの書き込み、a:ファイルへの追記
                    f.write(f"GPS_sta {self.gps.Lon},{self.gps.Lat}"+ '\n')
            
            
            else:
                print("GPS completed!!")
                
                if self.startstate==0:                                           
#                     self.gps.vincenty_inverse(self.startlat,self.startlon,self.gps.Lat,self.gps.Lon)#距離:self.gps.gpsdis 方位角:self.gps.gpsdegrees
#                     self.startlat=35.55500310217821
#                     self.startlon=139.656020989901
                    self.startgps_lon_mean=np.mean(self.startgps_lon)
                    self.startgps_lat_mean=np.mean(self.startgps_lat)
                    self.gps.vincenty_inverse(self.startlat,self.startlon,self.startgps_lat_mean,self.startgps_lon_mean)
                    #self.gps.vincenty_inverse(self.startlat,self.startlon,35.55518333,139.65596167)
                    #極座標から直交座標へ変換
                    self.x = self.gps.gpsdis*math.cos(math.radians(self.gps.gpsdegrees))               
                    self.y = self.gps.gpsdis*math.sin(math.radians(self.gps.gpsdegrees))
                    print(f" x:{self.x},y:{self.y}")

    #                 self.gps.vincenty_inverse(self.startlat,self.startlon,self.gps.Lat,self.gps.Lon)#距離:self.gps.gpsdis 方位角:self.gps.gpsdegrees
    #                 #self.gps.vincenty_inverse(self.startlat,self.startlon,35.55518333,139.65596167)
    #                 #極座標から直交座標へ変換
    #                 self.x = self.gps.gpsdis*math.cos(math.radians(self.gps.gpsdegrees))
    #                 self.y = self.gps.gpsdis*math.sin(math.radians(self.gps.gpsdegrees))
    #                 
                    for i in range(4):
                        self.startpointdis.append(math.sqrt((self.x - self.startpoint[i][0])**2 + (self.y - self.startpoint[i][1])**2))
                    
                    self.close_startpoint=self.startpointdis.index(min(self.startpointdis))#0~3の中で一番近いスタート地点のインデックスを格納
                    self.startstate=1
                    
                    self.starttheta = math.degrees(math.atan2(self.startpoint[self.close_startpoint][1] - self.y, self.startpoint[self.close_startpoint][0] - self.x))#スタート地点までの角度を計算
                    if self.starttheta < 0:
                        self.starttheta += 360
                    error = self.starttheta - self.ex
                    
                    while abs(error) > 10:
                        self.sensor()
                        error = self.starttheta - self.ex
                        if error < -180:
                            error += 360
                        elif error > 180:
                            error -= 360
                        
                        if error > 0:
                            self.rightmotor.back(25)
                            self.leftmotor.go(25)
                        else:
                            self.rightmotor.go(25)
                            self.leftmotor.back(25)             
                    
                else:
                    print(f"now x:{self.x}, y:{self.y}")
                    self.starttheta = math.degrees(math.atan2(self.startpoint[self.close_startpoint][1] - self.y, self.startpoint[self.close_startpoint][0] - self.x))#スタート地点までの角度を計算
                    print(f"dist x:{self.startpoint[self.close_startpoint][0]}, y:{self.startpoint[self.close_startpoint][1]}")
                    if self.starttheta < 0:
                        self.starttheta += 360
                    
                    print("startpoint is "+ str(self.close_startpoint))
                    print("start angle is "+ str(self.starttheta))
                    
                    error = self.starttheta - self.ex
                    
                    if error < -180:
                        error += 360
                    elif error > 180:
                        error -= 360
                
                    ke = self.ka *error
                    
                    print("目標範囲:"+ \
                          str(self.startshadowTHRE_x[self.close_startpoint][0]) + "< x <" + str(self.startshadowTHRE_x[self.close_startpoint][1])+ " , " + \
                          str(self.startshadowTHRE_y[self.close_startpoint][0]) + "< y <" + str(self.startshadowTHRE_y[self.close_startpoint][1]))
                    
                    #選択したスタート地点に向かって直進し，大体近づいたら次のステートへ
                    if self.startshadowTHRE_x[self.close_startpoint][0] < self.x  and self.x < self.startshadowTHRE_x[self.close_startpoint][1] and \
                       self.startshadowTHRE_y[self.close_startpoint][0] < self.y  and self.y < self.startshadowTHRE_y[self.close_startpoint][1]:
                        
                        self.rightmotor.stop()
                        self.leftmotor.stop()
                        
                        if self.gpscount <= ct.const.PREPARING_GPS_COUNT_THRE and self.measuringcount == 0:
                            self.measuringgps_lon.append(float(self.gps.Lon))
                            self.measuringgps_lat.append(float(self.gps.Lat))
                            print(f"GPS is +{self.gpscount}")
                            print(f"GPS {self.gps.Lon},{self.gps.Lat}")
                            self.gpscount+=1
                            time.sleep(1)
                            if self.gpscount == ct.const.PREPARING_GPS_COUNT_THRE:
                                print("a")
                                self.measuringgps_lon_mean=np.mean(self.measuringgps_lon)
                                self.measuringgps_lat_mean=np.mean(self.measuringgps_lat)
                                self.gps.vincenty_inverse(self.startlat,self.startlon,self.gps.Lat,self.gps.Lon)#距離:self.gps.gpsdis 方位角:self.gps.gpsdegrees
                                self.x = self.gps.gpsdis*math.cos(math.radians(self.gps.gpsdegrees))
                                self.y = self.gps.gpsdis*math.sin(math.radians(self.gps.gpsdegrees))
                                    
                                self.state = 5
                                self.laststate = 5
                    
                    else:
                        self.rightmotor.go(self.v_ref - ke)
                        self.leftmotor.go(self.v_ref + ke)
                        self.odometri()

                    if time.time() - self.startingTime > ct.const.STARTING_TIME_THRE:#x秒経ってもスタート地点に着いてない場合は次のステートへ
                        print("b")
                        print(time.time() - self.startingTime)
                        self.state = 5
                        self.laststate = 5
                        #self.startstate=0
                        pass
                 
    """
    def starting(self):
        if self.startingTime == 0:#時刻を取得してLEDをステートに合わせて光らせる
            self.startingTime = time.time()
            self.RED_LED.led_on()
            self.BLUE_LED.led_off()
            self.GREEN_LED.led_on()
            self.startpointdis=list()
            self.t_new=0
        else:#4つのスタート地点から一番近い点へ移動
            #原点と着陸地点の距離と方位角を取得
            if self.startstate==0:
                self.gps.vincenty_inverse(self.startlat,self.startlon,self.gps.Lat,self.gps.Lon)#距離:self.gps.gpsdis 方位角:self.gps.gpsdegrees
                #self.gps.vincenty_inverse(self.startlat,self.startlon,35.55518333,139.65596167)
                #極座標から直交座標へ変換
                self.x = self.gps.gpsdis*math.cos(math.radians(self.gps.gpsdegrees))
                self.y = self.gps.gpsdis*math.sin(math.radians(self.gps.gpsdegrees))
                
                for i in range(4):
                    self.startpointdis.append(math.sqrt((self.x - self.startpoint[i][0])**2 + (self.y - self.startpoint[i][1])**2))
                
                self.close_startpoint=self.startpointdis.index(min(self.startpointdis))#0~3の中で一番近いスタート地点のインデックスを格納
                self.startstate=1
            else:
                self.gps.vincenty_inverse(self.startlat,self.startlon,self.gps.Lat,self.gps.Lon)#距離:self.gps.gpsdis 方位角:self.gps.gpsdegrees
                #self.gps.vincenty_inverse(self.startlat,self.startlon,35.55518333,139.65596167)
                #極座標から直交座標へ変換
                self.x = self.gps.gpsdis*math.cos(math.radians(self.gps.gpsdegrees))
                self.y = self.gps.gpsdis*math.sin(math.radians(self.gps.gpsdegrees))
                print(f"now x:{self.x}, y:{self.y}")
                self.starttheta = math.degrees(math.atan2(self.startpoint[self.close_startpoint][1] - self.y, self.startpoint[self.close_startpoint][0] - self.x))#スタート地点までの角度を計算
                print(f"dist x:{self.startpoint[self.close_startpoint][0]}, y:{self.startpoint[self.close_startpoint][1]}")
                if self.starttheta < 0:
                    self.starttheta += 360
                
                print("startpoint is "+ str(self.close_startpoint))
                print("start angle is "+ str(self.starttheta))
                
                error = self.starttheta - self.ex
                
                if error < -180:
                    error += 360
                elif error > 180:
                    error -= 360
                
                print(f"error: {error}")
                ke = self.ka *error
                
                print("目標範囲:"+ \
                      str(self.startshadowTHRE_x[self.close_startpoint][0]) + "< x <" + str(self.startshadowTHRE_x[self.close_startpoint][1])+ \
                      str(self.startshadowTHRE_y[self.close_startpoint][0]) + "< y <" + str(self.startshadowTHRE_y[self.close_startpoint][1]))
                
                #選択したスタート地点に向かって直進し，大体近づいたら次のステートへ
                if self.startshadowTHRE_x[self.close_startpoint][0] < self.x  and self.x < self.startshadowTHRE_x[self.close_startpoint][1] and \
                   self.startshadowTHRE_y[self.close_startpoint][0] < self.y  and self.y < self.startshadowTHRE_y[self.close_startpoint][1]:
                    
                    self.rightmotor.stop()
                    self.leftmotor.stop()
                                         
                    self.state = 5
                    self.laststate = 5
                
                else:
                    self.rightmotor.go(self.v_ref - ke)
                    self.leftmotor.go(self.v_ref + ke)

                if time.time() - self.startingTime > ct.const.STARTING_TIME_THRE:#x秒経ってもスタート地点に着いてない場合は次のステートへ
                    self.state = 5
                    self.laststate = 5
                    #self.startstate=0
                    pass
                
    """
    

    def measuring(self):
        print("measuring count is "+str(self.measuringcount))
     
        if self.measureringTimeLog == list():#時刻を取得してLEDをステートに合わせて光らせる
            self.measureringTimeLog.append(time.time())
            self.RED_LED.led_off()
            self.BLUE_LED.led_on()
            self.GREEN_LED.led_on()
            self.rightmotor.stop()
            self.leftmotor.stop()
            
        else:
            if self.countSwitchLoop < ct.const.MEASURING_SWITCH_COUNT_THRE:
                self.rightmotor.stop()
                self.leftmotor.stop()
                self.switchRadio()#LoRaでログを送信
                if self.radio.cansat_rssi==0:
                    pass
                else:
                    self.LogCansatRSSI.append(self.radio.cansat_rssi)
                    self.LogLostRSSI.append(self.radio.lost_rssi)
                    self.distanceCansat=self.radio.estimate_distance_Cansat(self.radio.cansat_rssi)
                    self.distanceLost=self.radio.estimate_distance_Lost(self.radio.lost_rssi)
                    self.distanceCansat_2=self.radio.estimate_distance_Cansat_2(self.radio.cansat_rssi)
                    self.distanceLost_2=self.radio.estimate_distance_Lost_2(self.radio.lost_rssi)
                    print(f"カンサット推定距離:{self.distanceCansat},ロスト機推定距離:{self.distanceLost}")
                    print(f"カンサット推定距離2:{self.distanceCansat_2},ロスト機推定距離2:{self.distanceLost_2}")
                    print(self.countSwitchLoop)

                    self.countSwitchLoop+=1
            else:
                print("RSSIのlist_before:",self.LogCansatRSSI)
#                 self.LogCansatRSSI_2 = []
#                 for i in self.LogCansatRSSI:
#                     self.LogCansatRSSI_2.append(self.LogCansatRSSI[i][0])
#                 self.LogCansatRSSI = self.LogCansatRSSI_2
#                 print("RSSIのlist_before_2:",self.LogCansatRSSI)
                #hazure
                self.LogCansatRSSI_median = statistics.median(self.LogCansatRSSI)
                self.LogCansatRSSI_low = self.LogCansatRSSI_median - self.hazure
                self.LogCansatRSSI_high = self.LogCansatRSSI_median + self.hazure
                self.LogCansatRSSI_rec = []

                for i in range(0, len(self.LogCansatRSSI)):
                    if self.LogCansatRSSI[i] < self.LogCansatRSSI_low or self.LogCansatRSSI[i] > self.LogCansatRSSI_high:
                        self.LogCansatRSSI_rec.append(i)
                for i in range(0, len(self.LogCansatRSSI_rec)):
                    del self.LogCansatRSSI[self.LogCansatRSSI_rec[i]-i]
                print("RSSIのlist_after:",self.LogCansatRSSI)

                #RSSIの平均取る
                self.meanCansatRSSI=np.mean(self.LogCansatRSSI)
                self.meanLostRSSI=np.mean(self.LogLostRSSI)

                #距離推定
                self.distanceCansatRSSI=self.radio.estimate_distance_Cansat(self.meanCansatRSSI)
                self.distanceLostRSSI=self.radio.estimate_distance_Lost(self.meanLostRSSI)
                self.distanceCansatRSSI_2=self.radio.estimate_distance_Cansat_2(self.meanCansatRSSI)
                self.distanceLostRSSI_2=self.radio.estimate_distance_Lost_2(self.meanLostRSSI)

                print('カンサット:定義式からの推定'+str(self.distanceCansatRSSI))
                print('ロスト機:定義式からの推定'+str(self.distanceLostRSSI))
                print('カンサット:近似式からの推定'+str(self.distanceCansatRSSI_2))
                print('ロスト機:近似式からの推定'+str(self.distanceLostRSSI_2))
                self.n_dis_LogCansatRSSI.append(self.distanceCansatRSSI)
                self.n_dis_LogLostRSSI.append(self.distanceLostRSSI)
                self.n_dis_LogCansatRSSI_2.append(self.distanceCansatRSSI_2)
                self.n_dis_LogLostRSSI_2.append(self.distanceLostRSSI_2)

                self.meandis=(self.distanceCansatRSSI+self.distanceLostRSSI)/2
                self.n_meandisLog.append(self.meandis)                

                #n点測量後に使用するデータを格納
                self.LogData = [self.measuringcount,self.x,self.y,self.meandis,np.std(self.LogCansatRSSI),np.std(self.LogLostRSSI),
                                self.meanCansatRSSI,self.meanLostRSSI,self.distanceCansatRSSI,self.distanceLostRSSI,self.distanceCansatRSSI_2,self.distanceLostRSSI_2]
                print(self.LogData)

                self.n_LogData.append(self.LogData)

                #RSSIのデータ保管
                self.n_LogCansatRSSI.append(self.LogCansatRSSI)
                self.n_LogLostRSSI.append(self.LogLostRSSI)

                with open("%s/%s.csv" % (self.filename,self.filename_hm), "a", encoding='utf-8') as f: # 文字コードをShift_JISに指定 'a':末尾に追加
                    writer = csv.writer(f, lineterminator='\n') # writerオブジェクトの作成 改行記号で行を区切る
                    writer.writerow(self.LogData) # csvファイルに書き込み
                    writer.writerow(self.LogCansatRSSI)
                    writer.writerow(self.LogLostRSSI)


                self.meanCansatRSSI=0
                self.meanLostRSSI=0
                self.mesureringTime = 0
                self.countSwitchLoop = 0
                self.LogCansatRSSI=[]
                self.LogLostRSSI=[]
                self.LogData=[]

                if self.measuringcount == ct.const.MEASURING_MAX_MEASURING_COUNT_THRE:
                    self.state = 8
                    self.laststate = 8

                else:
                    self.measuringcount+=1#n点測量目
                    self.state = 6
                    self.laststate = 6
                    print(self.measuringcount)
#                     time.sleep(15)

                    self.t_new=0 #オドメトリで必要な初期化

    def caseDiscrimination(self):
        if self.x < - ct.const.CASE_DISCRIMINATION and self.y < ct.const.SHADOW_EDGE_LENGTH + ct.const.CASE_DISCRIMINATION:
            self.case=0
        elif self.x < ct.const.SHADOW_EDGE_LENGTH + ct.const.CASE_DISCRIMINATION and self.y > ct.const.SHADOW_EDGE_LENGTH + ct.const.CASE_DISCRIMINATION :
            self.case=1
        elif self.x > ct.const.SHADOW_EDGE_LENGTH + ct.const.CASE_DISCRIMINATION and self.y > - ct.const.CASE_DISCRIMINATION:
            self.case=2
        elif self.x > - ct.const.CASE_DISCRIMINATION and self.y < -ct.const.CASE_DISCRIMINATION:
            self.case=3
        else:#永久影に入っちゃっている場合
            self.case=4
    
    def motor_run(self):
        if self.case==1:        
            error=math.sin(math.radians(self.azimuth[self.case])) - math.sin(math.radians(self.bno055.ex))
            ke=self.k*error

            self.leftmotor.go(self.v_ref+ke)
            self.rightmotor.go(self.v_ref)

        elif self.case==2:
            error=math.cos(math.radians(self.azimuth[self.case])) - math.cos(math.radians(self.bno055.ex))
            ke=self.k*error
            self.leftmotor.go(self.v_ref+ke)
            self.rightmotor.go(self.v_ref)
        
        elif self.case==3:
            error=math.sin(math.radians(self.azimuth[self.case])) - math.sin(math.radians(self.bno055.ex))
            ke=self.k*error
            self.leftmotor.go(self.v_ref)
            self.rightmotor.go(self.v_ref+ke)
         
        elif self.case==0:
            error=math.cos(math.radians(self.azimuth[self.case])) - math.cos(math.radians(self.bno055.ex))
            ke=self.k*error
            self.leftmotor.go(self.v_ref)
            self.rightmotor.go(self.v_ref+ke)
    
            
     
    def stuck_detection(self):#スタック検知
        print("Acceleration:"+str( self.Az**2))
        if len(self.accdata)< ct.const.ACC_COUNT:
            self.accdata.append(float(self.Az**2))
            self.accdata_x.append(float(self.x))
            self.accdata_y.append(float(self.y))
            print(self.accdata)
            print("X:",self.accdata_x)
            print("Y:",self.accdata_y)
            self.odometri()
           
        else:
#             self.accdata.sort()
#             print(self.accdata)
#             print(f"5:{self.accdata[4]}")
#             print(f"accmean:{np.mean(self.accdata)}")
#             print(f"accmedian:{np.median(self.accdata)}")
            self.accdata[0:ct.const.ACC_COUNT-1]= self.accdata[1:ct.const.ACC_COUNT]
            self.accdata.append(float(self.Az**2))
#             self.accdata_x[0:ct.const.ACC_COUNT-1]= self.accdata_x[1:ct.const.ACC_COUNT]
#             self.accdata_x.append((float(self.x)))
#             self.accdata_y[0:ct.const.ACC_COUNT-1]= self.accdata_y[1:ct.const.ACC_COUNT]
#             self.accdata_y.append(float(self.y))
            self.accdata_x.append((float(self.x)))
            self.accdata_y.append(float(self.y))
            
            print("X:",self.accdata_x)
            print("Y:",self.accdata_y)
            
            acc=np.array(self.accdata)
#             print(acc)
            self.countstuck=np.count_nonzero( acc < ct.const.RUNNiNG_STUCK_ACC_THRE)
            print(self.countstuck)
            
            if self.countstuck > 4:
                print("stuck!!!!!")
                back = False #バックでスタックから脱出したい場合True,トルネードならFalse

                self.rightmotor.stop()
                self.leftmotor.stop()

                if back:#バックで脱出
                    print("back")
                    self.rightmotor.back(100)
                    self.leftmotor.back(100) 
                    time.sleep(1)
                    self.rightmotor.back(30)
                    self.leftmotor.back(80)
                    time.sleep(1)

                else:#トルネードで脱出
                    self.rightmotor.back(100)
                    self.leftmotor.go(100)
                    time.sleep(0.5)
                    if len(self.accdata_x) < ct.const.ODOMETRI_BACK:
                        self.x=self.accdata_x[0]
                        self.y=self.accdata_y[0] 
                               
                    else:
                        self.x=self.accdata_x[-ct.const.ODOMETRI_BACK]
                        self.y=self.accdata_y[-ct.const.ODOMETRI_BACK]
                        
                    self.rightmotor.go(self.v_ref)
                    self.leftmotor.go(self.v_ref)
                    print(f"X:{self.x},Y:{self.y}")
                    self.odometri()
                 
                    time.sleep(1)
                    self.accdata=list()
                    self.accdata_x=list()
                    self.accdata_y=list()
        
    
    def running(self):
#         print("Acceleration:"+str(self.Ax**2 + self.Ay**2 + self.Az**2))
        print("Acceleration:"+str(self.Az**2 ))
        if self.runningTime == 0:#時刻を取得してLEDをステートに合わせて光らせる
            self.runningTime = time.time()
            self.RED_LED.led_on()
            self.BLUE_LED.led_on()
            self.GREEN_LED.led_on()
            self.t_new=time.time()
        
        else:#Case判定  
            self.caseDiscrimination()#Case判定
#             self.case=0
            print("case is "+str(self.case))
            
            if self.case == 4:#永久影からの脱出
                self.rightmotor.go(70)
                self.leftmotor.go(80)
                self.odometri()
                print("case is "+str(self.case))
                
            else:
                print(f"measuringcount-1 :{self.measuringcount-1}")
                print(f"n_LogData :{self.n_LogData}")
                print(f"n_LogData01: {self.n_LogData[0][1]}")
                if math.sqrt((self.x - self.n_LogData[self.measuringcount-1][1])**2 + (self.y - self.n_LogData[self.measuringcount-1][2])**2) > ct.const.MEASURMENT_INTERVAL:#前回の測量地点から閾値以上動いたらmeasurring stateへ
                        self.rightmotor.stop()
                        self.leftmotor.stop()
                        self.state = 5
                        self.laststate = 5
                else:
                    self.motor_run()
                    self.odometri()
                    
#                     self.stuck_detection()
                        
    def positioning(self):
        if self.positioningTime == 0:#時刻を取得してLEDをステートに合わせて光らせる
            self.positioningTime = time.time()
            self.RED_LED.led_on()
            self.BLUE_LED.led_off()
            self.GREEN_LED.led_off()
            self.rightmotor.stop()
            self.leftmotor.stop()
        else:
            if self.positioning_count >= len(self.n_LogData):
                self.n_pdf_sum=sum(self.n_pdf)
                Estimation_Result_x, Estimation_Result_y=self.graph(self.n_pdf_sum)
                #絶対座標
                print("絶対座標(x,y):" +"(" + str(Estimation_Result_x)+","+str(Estimation_Result_y)+")")
                
                #最終地点との相対座標
                Rel_Estimation_Result_r = math.sqrt((Estimation_Result_x - self.x)**2 + (Estimation_Result_y - self.y)**2)
                Rel_Estimation_Result_q = math.degrees(math.atan2(Estimation_Result_y - self.y, Estimation_Result_x - self.x))
                if Rel_Estimation_Result_q < 0:
                    Rel_Estimation_Result_q += 360
                elif Rel_Estimation_Result_q > 360:
                    Rel_Estimation_Result_q -= 360
                print("相対距離(r,q):" +"(" + str(Rel_Estimation_Result_r)+","+str(Rel_Estimation_Result_q)+")")
                
                lastdata =  "#CanSat定義式からの推定結果:"+str(self.n_dis_LogCansatRSSI)+ '\n' \
                    + "#Lost定義式からの推定結果:"+str(self.n_dis_LogLostRSSI)+ '\n' \
                    + "#CanSat近似式からの推定結果:"+str(self.n_dis_LogCansatRSSI_2)+ '\n' \
                    + "#Lost近似式からの推定結果:"+str(self.n_dis_LogLostRSSI_2)+ '\n' \
                    + "#絶対座標(x,y):" + "(" + str(Estimation_Result_x) + "," + str(Estimation_Result_y) + ")" + '\n'\
                    + "#相対距離(r,q):" + "(" + str(Rel_Estimation_Result_r) + "," + str(Rel_Estimation_Result_q) + ")" + '\n'
                    
                with open('/home/pi/Desktop/wolvez2021/Testcode/Integration/%s/%s_lastdata.txt' % (self.filename,self.filename_hm),mode = 'a') as test: # [mode] x:ファイルの新規作成、r:ファイルの読み込み、w:ファイルへの書き込み、a:ファイルへの追記
                    test.write(lastdata)
                
                self.state = 9
                self.laststate = 9
                
            else:
                if self.n_LogData[self.positioning_count][4]>3  or self.n_LogData[self.positioning_count][5] >3 :
                    self.positioning_count +=1
                    
                else:
                    self.n_pdf.append(self.pdf(self.n_LogData[self.positioning_count][1],
                                          self.n_LogData[self.positioning_count][2],
                                          self.n_LogData[self.positioning_count][3]))
                    self.positioning_count +=1
                    
    def modified_positioning(self):
        if self.positioningTime == 0:#時刻を取得してLEDをステートに合わせて光らせる
            self.positioningTime = time.time()
            self.RED_LED.led_on()
            self.BLUE_LED.led_off()
            self.GREEN_LED.led_off()
            self.rightmotor.stop()
            self.leftmotor.stop()
            
            self.FirstMeasuring_r = float(input("1回目測位地点：基準点からの距離を入力"))
            self.FirstMeasuring_q = float(input("1回目測位地点：基準点からCanSatを見たときの方位角を入力"))
            
            self.FirstMeasuring_x = self.FirstMeasuring_r * math.cos(math.radians(self.FirstMeasuring_q))
            self.FirstMeasuring_y = self.FirstMeasuring_r * math.sin(math.radians(self.FirstMeasuring_q))
            
            self.error_x = self.FirstMeasuring_x - self.n_LogData[0][1]
            self.error_y = self.FirstMeasuring_y - self.n_LogData[0][2]
        else:
            if self.positioning_count >= len(self.n_LogData):
                self.n_pdf_sum=sum(self.n_pdf)
                Estimation_Result_x, Estimation_Result_y=self.graph(self.n_pdf_sum)
                #絶対座標
                print("絶対座標(x,y):" +"(" + str(Estimation_Result_x)+","+str(Estimation_Result_y)+")")
                World_Estimation_Error = math.sqrt((Estimation_Result_x - 7 )**2 + (Estimation_Result_y - 6 )**2) #探索機が(x,y)の場合
                print("絶対測位誤差:" + str(World_Estimation_Error))
                
                #最終地点との相対座標
                Rel_Estimation_Result_r = math.sqrt((Estimation_Result_x - self.x)**2 + (Estimation_Result_y - self.y)**2)
                Rel_Estimation_Result_q = math.degrees(math.atan2(Estimation_Result_y - self.y, Estimation_Result_x - self.x))
                if Rel_Estimation_Result_q < 0:
                    Rel_Estimation_Result_q += 360
                elif Rel_Estimation_Result_q > 360:
                    Rel_Estimation_Result_q -= 360
                print("相対距離(r,q):" +"(" + str(Rel_Estimation_Result_r)+","+str(Rel_Estimation_Result_q)+")")
                
                Rel_Real_r = float(input("相対距離を入力"))
                Rel_Real_q = float(input("CanSatから探査機を見たときの方位角を入力"))
                
                Rel_Estimation_Error = math.sqrt(Rel_Estimation_Result_r**2 + Rel_Real_r**2 - 2 * Rel_Estimation_Result_r * Rel_Real_r * math.cos(math.radians(Rel_Estimation_Result_q - Rel_Real_q)))
                
                print("相対測位誤差:" + str(Rel_Estimation_Error))
                
                lastdata =  "#CanSat定義式からの推定結果:"+str(self.n_dis_LogCansatRSSI)+ '\n' \
                    + "#Lost定義式からの推定結果:"+str(self.n_dis_LogLostRSSI)+ '\n' \
                    + "#CanSat近似式からの推定結果:"+str(self.n_dis_LogCansatRSSI_2)+ '\n' \
                    + "#Lost近似式からの推定結果:"+str(self.n_dis_LogLostRSSI_2)+ '\n' \
                    + "#絶対座標(x,y):" + "(" + str(Estimation_Result_x) + "," + str(Estimation_Result_y) + ")" + '\n'\
                    + "絶対測位誤差:" + str(World_Estimation_Error) + '\n' \
                    + "#相対距離(r,q):" + "(" + str(Rel_Estimation_Result_r) + "," + str(Rel_Estimation_Result_q) + ")" + '\n' \
                    + "相対測位誤差:" + str(Rel_Estimation_Error) + '\n'
                    
                with open('/home/pi/Desktop/wolvez2021/Testcode/Integration/%s/%s_lastdata.txt' % (self.filename,self.filename_hm),mode = 'a') as test: # [mode] x:ファイルの新規作成、r:ファイルの読み込み、w:ファイルへの書き込み、a:ファイルへの追記
                    test.write(lastdata)
                
                self.state = 9
                self.laststate = 9
                
            else:
                self.n_LogData[self.positioning_count][1] += self.error_x
                self.n_LogData[self.positioning_count][2] += self.error_y
                
                if self.n_LogData[self.positioning_count][4]>3  or self.n_LogData[self.positioning_count][5] >3 :
                    pass
                    
                else:
                    self.n_pdf.append(self.pdf(self.n_LogData[self.positioning_count][1],
                                          self.n_LogData[self.positioning_count][2],
                                          self.n_LogData[self.positioning_count][3]))
                self.positioning_count +=1
        
    def finish(self):
        if self.finishTime == 0:#時刻を取得してLEDをステートに合わせて光らせる
            self.finishTime = time.time()
            self.RED_LED.led_off()
            self.BLUE_LED.led_off()
            self.GREEN_LED.led_off()
            
            sys.exit()
        
    def pdf(self,xc,yc,r):
        w=1
        ww=3
        return 1*np.exp(-1*ww*((w*self.X-xc)**2+(w*self.Y-yc)**2)/(2*r**2))*((w*self.X-xc)**2+(w*self.Y-yc)**2)/(2*math.pi*r**2)
    
    def graph(self,Z):
        x = np.arange(-30, 31, 1)
        y = np.arange(-30, 31, 1)
        Zc=np.unravel_index(np.argmax(Z), Z.shape)
        x_est=x[Zc[1]]
        y_est=y[Zc[0]]
        fig = plt.figure()
        ax = fig.add_subplot(111,projection="3d")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")
        surf=ax.plot_surface(self.X, self.Y, Z, cmap=plt.cm.jet,linewidth=0, antialiased=False)
        ax.scatter(x[Zc[1]], y[Zc[0]], np.max(Z),s = 40,c='k',)
        ax.set_xlim(-30.01, 30.01)
        ax.set_ylim(-30.01, 30.01)
        #ax.set_zlim(0.0, 0.5)
        ax.view_init(30, 30)
        fig.colorbar(surf, shrink=0.5, aspect=5)
        #plt.show()
        name = str(self.filename_hm)
        my_path = os.path.abspath('/home/pi/Desktop/wolvez2021/Testcode/Integration/%s' % (self.filename))
        my_file = name + ".pdf"
        fig.savefig(os.path.join(my_path, my_file))
        
        return x_est, y_est

if __name__ == "__main__":
    pass

