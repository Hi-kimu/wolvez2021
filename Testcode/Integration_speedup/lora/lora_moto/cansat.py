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


#クラス読み込み
import constant as ct
import radio


class Cansat(object):
    
    def __init__(self):
        GPIO.setwarnings(False)
        #オブジェクトの生成

        self.radio = radio.radio()
        
        #開始時間の記録
        self.startTime = time.time()
        self.timer = 0
        self.landstate = 0 #landing stateの中でモータを一定時間回すためにlandのなかでもステート管理するため
        self.startstate = 0
        self.v_right = 100
        self.v_left = 100
        
        #変数
        self.state = 5
        self.laststate = 0
        self.landstate = 0
        self.k = 20
        self.v_ref = 90

     
        #n点測位用の変数
        self.measureringTimeLog=list()
        self.measuringcount=0#n点測量目をこの変数で管理
        self.meanCansatRSSI=0
        self.meanLostRSSI=0
        self.LogData = list()
        self.n_LogData = list()
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
        self.finishTime = 0
        
        #state管理用変数初期化
        self.countPreLoop = 0
        self.countFlyLoop = 0
        self.countDropLoop = 0
        self.countSwitchLoop=0
        self.countGoal = 0
        self.countgrass=0
        
        #GPIO設定
 
        
 
    def setup(self):
        self.radio.setupRadio()
    
   
    def sensor(self):
        self.timer = 1000*(time.time() - self.startTime) #経過時間 (ms)
        self.timer = int(self.timer)

        self.switchRadio()
            
        
        #ログデータ作成。\マークを入れることで改行してもコードを続けて書くことができる
        datalog = str(self.timer) 
     
    def switchRadio(self):
        datalog = str(self.state)
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
            self.finish()
        else:
            self.state = self.laststate #どこにも引っかからない場合何かがおかしいのでlaststateに戻してあげる

            
    def measuring(self):
        print("measuring count is "+str(self.measuringcount))
        if self.measureringTimeLog == list():#時刻を取得してLEDをステートに合わせて光らせる
            self.measureringTimeLog.append(time.time())
          
                
        else:
            if self.countSwitchLoop < ct.const.SWITCH_LOOP_THRE:
                #self.switchRadio()#LoRaでログを送信
                self.LogCansatRSSI.append([self.radio.cansat_rssi])
                self.LogLostRSSI.append([self.radio.lost_rssi])
                #print(self.countSwitchLoop)
                self.countSwitchLoop+=1
            else:
                #RSSIの平均取る
                self.meanCansatRSSI=np.mean(self.LogCansatRSSI)
                self.meanLostRSSI=np.mean(self.LogLostRSSI)
               
                #距離推定
                self.distanceCansatRSSI=self.radio.estimate_distance_Cansat(self.meanCansatRSSI)
                self.distanceLostRSSI=self.radio.estimate_distance_Lost(self.meanLostRSSI)
                print('カンサット:定義式からの推定'+str(self.distanceCansatRSSI))
                print('ロスト機:定義式からの推定'+str(self.distanceLostRSSI))
                self.n_dis_LogCansatRSSI.append(self.distanceCansatRSSI)
                self.n_dis_LogLostRSSI.append(self.distanceLostRSSI)
                self.meandis=(self.distanceCansatRSSI+self.distanceLostRSSI)/2
                self.n_meandisLog.append(self.meandis)                
                
                #n点測量後に使用するデータを格納
                self.LogData = [self.measuringcount,self.x,self.y,self.meandis,np.std(self.LogCansatRSSI),np.std(self.LogLostRSSI)]
                self.n_LogData.append(self.LogData)
                #RSSIのデータ保管
                self.n_LogCansatRSSI.append(self.LogCansatRSSI)
                self.n_LogCansatRSSI.append(self.LogLostRSSI)
                
                self.meanCansatRSSI=0
                self.meanLostRSSI=0
                self.mesureringTime = 0
                self.countSwitchLoop = 0
                self.LogCansatRSSI=[]
                self.LogLostRSSI=[]
                self.LogData=[]
                
                if self.measuringcount == ct.const.MAX_MEASURING_COUNT:
                    self.state = 7
                    self.laststate = 7
                
                else:
                    self.measuringcount+=1#n点測量目
                    self.state = 6
                    self.laststate = 6
 

if __name__ == "__main__":
    pass

