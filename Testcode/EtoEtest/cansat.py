# -*- coding: utf-8 -*-
"""
Keio Wolve'Z cansat2020
mission function
Author Yuji Tanaka
last update:2020/10/22

"""

#ライブラリの読み込み
import time
import RPi.GPIO as GPIO
import sys
import cv2
import numpy as np
import datetime

#クラス読み込み
import constant as ct
import camera
import gps
import motor
import radio
import ultrasonic
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
        self.ultrasonic = ultrasonic.Ultrasonic()
        self.RED_LED = led.led(ct.const.RED_LED_PIN)
        self.BLUE_LED = led.led(ct.const.BLUE_LED_PIN)
        self.GREEN_LED = led.led(ct.const.GREEN_LED_PIN)
        self.camera=camera.Camera()
        
        #開始時間の記録
        self.startTime = time.time()
        self.timer = 0
        self.timestep=0#写真撮影用
        self.landstate = 0 #landing statenの中でモータを一定時間回すためにlandのなかでもステート管理するため
        self.v_right = 100
        self.v_left = 98
        
        #変数
        self.state = 0
        self.laststate = 0
        self.following = 0 # state1の中で、カメラによる検知中か追従中かを区別、どちらもカメラを回しながら行いたいため
        self.refollow = 0
        self.refollowstate = 0
        self.landstate = 0
        #終了判定
        self.num = 10
        self.distdata = [0]*self.num
        self.b = 0
        #超音波センサ用変数
        self.countUltrasonic = 0
        
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
        self.countDistanceLoopStart=0 # 距離による開始判定
        self.countDistanceLoopEnd=0 # 距離による終了判定
        self.countgrass=0
        
        #GPIO設定
        GPIO.setmode(GPIO.BCM) #GPIOの設定
        GPIO.setup(ct.const.FLIGHTPIN_PIN,GPIO.IN) #フライトピン用
        GPIO.setup(ct.const.RELEASING_PIN,GPIO.OUT) #焼き切り用のピンの設定
        
        date = datetime.datetime.now()
        self.filename = '{0:%Y%m%d}'.format(date)
    
    def setup(self):
        self.gps.setupGps()
        self.radio.setupRadio()
        self.bno055.setupBno()
        self.camera.setupCamera()#ガンマ補正のためのセットアップ
        if self.bno055.begin() is not True:
            print("Error initializing device")
            exit()
    
    def sensor(self):
        self.timer = 1000*(time.time() - self.startTime) #経過時間 (ms)
        self.timer = int(self.timer)
        #self.countUltrasonic+=1
        self.gps.gpsread()
        self.bno055.bnoread()
        #if self.countUltrasonic%10==0:
        self.ultrasonic.getDistance()
        self.writeData()#txtファイルへのログの保存
        if not self.state == 1: #preparingのときは電波を発しない
            self.sendRadio()#LoRaでログを送信
    
    def writeData(self):
        self.Ax=round(self.bno055.Ax,3)
        self.Ay=round(self.bno055.Ay,3)
        self.Az=round(self.bno055.Az,3)
        self.dist=round(self.ultrasonic.dist,2) 
        #if self.dist < ct.const.DISTANCE_THRE_END:
            #self.dist = "[" + str(self.dist) + "]"
        #ログデータ作成。\マークを入れることで改行してもコードを続けて書くことができる
        datalog = str(self.timer) + ","\
                  + str(self.state) + ","\
                  + str(self.gps.Time) + ","\
                  + str(self.gps.Lat).rjust(6) + ","\
                  + str(self.gps.Lon).rjust(6) + ","\
                  + str(self.Ax).rjust(6) + ","\
                  + str(self.Ay).rjust(6) + ","\
                  + str(self.Az).rjust(6) + ","\
                  + str(self.dist).rjust(6) + ","\
                  + str(self.rightmotor.velocity).rjust(6) + ","\
                  + str(self.leftmotor.velocity).rjust(6)
        print(datalog)
        with open('/home/pi/Desktop/WolveZ_CANSAT2020/EtoEtest/TestResult/%s/%s.txt' % (self.filename,self.filename),mode = 'a') as test: # [mode] x:ファイルの新規作成、r:ファイルの読み込み、w:ファイルへの書き込み、a:ファイルへの追記
            test.write(datalog + '\n')
    
    def sendRadio(self):
        datalog = str(self.state) + ","\
                  + str(self.gps.Time) + ","\
                  + str(self.gps.Lat) + ","\
                  + str(self.gps.Lon) + ","\
                  + str(self.dist) #+ ","\
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
        if self.preparingTime == 0:#時刻を取得してLEDをステートに合わせて光らせる
            self.preparingTime = time.time()
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
            self.RED_LED.led_off()
            self.BLUE_LED.led_off()
            self.GREEN_LED.led_on()         
            
            
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
            self.RED_LED.led_on()
            self.BLUE_LED.led_on()
            self.GREEN_LED.led_off()
        
        if not self.landingTime == 0:
            if self.landstate == 0:
                GPIO.output(ct.const.RELEASING_PIN,1) #電圧をHIGHにして焼き切りを行う
                if time.time()-self.landingTime > ct.const.RELEASING_TIME_THRE:
                    GPIO.output(ct.const.RELEASING_PIN,0) #焼き切りが危ないのでlowにしておく
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
        
        if self.refollow==1:
            self.refollowstate+=1
            if self.refollowstate<ct.const.REFOLLOW_THRE:
                self.rightmotor.go(100)
                self.leftmotor.back(100)
            else:
                self.rightmotor.stop()
                self.leftmotor.stop()
            if self.refollowstate > 100:
                self.refollowstate=0
        
        #以下に超音波センサによる動的物体発見プログラム
        #if self.ultrasonic.dist<ct.const.DISTANCE_THRE_START:
        if self.ultrasonic.dist!=500:
            self.countDistanceLoopStart+=1
            if self.countDistanceLoopStart>ct.const.COUNT_DISTANCE_LOOP_THRE_START:
                print("対象認知＆カメラ処理開始")
                self.state=5
                self.laststate=5
                self.countDistanceLoopStart=0
                self.refollow=0
                self.rightmotor.stop()
                self.leftmotor.stop()
        else:
            self.countDistanceLoopStart=0
    
    def running(self):
        if self.runningTime == 0:#時刻を取得してLEDをステートに合わせて光らせる
            self.runningTime = time.time()
            self.RED_LED.led_on()
            self.BLUE_LED.led_on()
            self.GREEN_LED.led_on()
        
        #以下に画像処理走行プログラム
        
        #写真撮影用
        self.timestep+=1
        
        _, frame = self.capture.read() # 動画の読み込み
        #frame=cv2.resize(frame, (640,480)) # プレビューサイズ（いじらなくてよい）
        
        '''
        #以下でガンマ補正
        gray=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mean, stddev=cv2.meanStdDev(gray)
        #if stddev>ct.const.BLACKLIGHT_SD_UP or stddev<ct.const.BLACKLIGHT_SD_DOWN:
        if stddev<ct.const.BLACKLIGHT_SD_DOWN:
            frame=cv2.LUT(frame,self.camera.gamma_cvt)
        
        #frame=cv2.LUT(frame,self.camera.gamma_cvt)
        #print(self.camera.gamma_cvt)
        '''
        
        rects = self.camera.find_rect_of_target_color(frame) # 矩形の情報作成
        
        if len(rects) > 0:
            rect = max(rects, key=(lambda x: x[2] * x[3]))  # 最大の矩形を探索
            
            #各パラメータの計算
            self.camera.find_center_of_gravity(rect) # 重心の計算
            self.camera.find_angle(self.camera.cgx) # 角度の計算、絶対値
            self.camera.find_direction(self.camera.cgx) # 進む方向
            self.camera.find_area(rect) # 矩形の面積算出
            
            #超音波センサを用いた終了判定
            #self.ultrasonic.getDistance()
            #超音波センサを用いた終了判定
            if self.following==1:
                self.distdata[1:self.num]=self.distdata[0:self.num-1]
                self.distdata[0]=self.dist

                print(self.distdata)
                a = np.array(self.distdata)
                #print(a)
                self.b = np.count_nonzero((1 < a) & (a < 80))
                
                if self.b > ct.const.DISTANCE_LIST_THRE:
                    print("追従終了")
                    #fin_Name='./TestResult/'+self.filename+'/'+'FINISH.jpg'
                    #cv2.imwrite(fin_Name,frame)
                    self.state=6
                    self.lastsate=6
            """
            if self.following==1 and self.ultrasonic.dist<ct.const.DISTANCE_THRE_END:
                self.countDistanceLoopEnd+=1
                #print(self.countDistanceLoopEnd)
                if self.countDistanceLoopEnd>ct.const.COUNT_DISTANCE_LOOP_THRE_END:
                    print("追従終了")
                    cv2.imwrite('finish.jpg',frame)
                    self.state=6
                    self.lastsate=6
            else:
                self.countDistanceLoopEnd=0
                """
            #矩形の面積を用いた終了判定
            """
            if self.camera.area>ct.const.AREA_THRE_END:
                self.countAreaLoopEnd+=1
                if self.countAreaLoopEnd>ct.const.COUNT_AREA_LOOP_THRE_END:
                    break
            else:
                self.countAreaLoopEnd=0
            """
            
            #追従開始判定
            if self.following==0 and self.camera.area>ct.const.AREA_THRE_START:
                self.countAreaLoopStart+=1
                if self.countAreaLoopStart==1:
                    self.camera.cgxs=self.camera.cgx
                    self.camera.cgys=self.camera.cgy
                if self.countAreaLoopStart>ct.const.COUNT_AREA_LOOP_THRE_START:
                    if pow(self.camera.cgx-self.camera.cgxs,2)+pow(self.camera.cgy-self.camera.cgys,2)>ct.const.COG_THRE_START:
                        print("追従開始")
                        self.following=1
                        self.countAreaLoopStart=0
            else:
                self.countAreaLoopStart=0
            '''
            #カメラ起動しても赤色見つからないときの見失い
            if self.following==0:
                self.countgrass+=1
                if self.countgrass>500:
                    self.state=4
                    self.laststate=4
                    self.countAreaLoopLose=0
                    print('見失った！3')
                    cv2.destroyAllWindows()
                    self.refollow=1
                    self.rightmotor.stop()
                    self.leftmotor.stop()
                    self.countgrass=0
            '''
            
            #モーターへの指示を行う
            if self.following==1:
                #print('モーターへの指示')
                if self.ultrasonic.dist<ct.const.DISTANCE_THRE_END:
                    self.countDistanceLoopEnd+=1
                    print(self.countDistanceLoopEnd)
                else:
                    self.countDistanceLoopEnd=0
                    
                if self.camera.direct==0:
                    if self.countDistanceLoopEnd >= 3: #ct.const.DISTANCE_COUNT_LIMIT:
                        self.rightmotor.stop()
                        self.leftmotor.stop()
                    else:
                        self.rightmotor.go(100)
                        self.leftmotor.go(90)
                
                if self.camera.direct==1:
                    if self.countDistanceLoopEnd >= 3:#ct.const.DISTANCE_COUNT_LIMIT:
                        self.rightmotor.stop()
                        self.leftmotor.stop()
                    else:
                        self.rightmotor.go(100)
                        #self.leftmotor.go(round(70*(1-ct.const.CAMERA_GAIN1*self.camera.angle/ct.const.MAX_CAMERA_ANGLE)))
                        self.leftmotor.go(round(100*(1-1.2*self.camera.angle/62.2)))
                        
                if self.camera.direct==-1:
                    if self.countDistanceLoopEnd >= 3:#ct.const.DISTANCE_COUNT_LIMIT:
                        self.rightmotor.stop()
                        self.leftmotor.stop()
                    else:
                        #self.rightmotor.go(round(100*(1-ct.const.CAMERA_GAIN2*self.camera.angle/ct.const.MAX_CAMERA_ANGLE)))
                        self.rightmotor.go(round(100*(1-1.2*self.camera.angle/62.2)))
                        self.leftmotor.go(100)
            #見失い判定
            if self.following==1 and self.camera.area<ct.const.AREA_THRE_LOSE:
                self.countAreaLoopLose+=1
                if self.countAreaLoopLose>ct.const.COUNT_AREA_LOOP_THRE_LOSE:
                    self.state=4
                    self.laststate=4
                    self.countAreaLoopLose=0
                    self.following=0
                    print('見失った！')
                    cv2.destroyAllWindows()
                    self.refollow=1
                    self.rightmotor.stop()
                    self.leftmotor.stop()
                    self.countDistanceLoopStart=0
            else:
                self.countAreaLoopLose=0
            
            cv2.rectangle(frame, tuple(rect[0:2]), tuple(rect[0:2] + rect[2:4]), (0, 0, 255), thickness=2) # フレームを生成
        cv2.drawMarker(frame,(self.camera.cgx,self.camera.cgy),(60,0,0))
        frame=cv2.rotate(frame,cv2.ROTATE_180)
        
        
        # 一定間隔で状況を撮影
        if self.timestep%20==0:
            imName='./TestResult/'+self.filename+'/'+self.filename+'_'+str(self.timer)+'image.jpg'
            cv2.imwrite(imName,frame)
        
        
        
        cv2.imshow('red', frame)
        cv2.waitKey(1)
        
        #画面に赤い要素が全くない場合の見失い判定
        if self.following==1 and len(rects)==0:
            self.countAreaLoopLose+=1
            if self.countAreaLoopLose>ct.const.COUNT_AREA_LOOP_THRE_LOSE:
                self.state=4
                self.laststate=4
                self.countAreaLoopLose=0
                self.following=0
                print('見失った2！')
                cv2.destroyAllWindows()
                self.refollow=1
                self.rightmotor.stop()
                self.leftmotor.stop()
                self.countDistanceLoopStart=0
    
    def goal(self):
        if self.goalTime == 0:#時刻を取得してLEDをステートに合わせて光らせる
            self.goalTime = time.time()
            self.capture.release()
            cv2.destroyAllWindows()
            self.RED_LED.led_off()
            self.BLUE_LED.led_off()
            self.GREEN_LED.led_off()
            
            self.rightmotor.stop()
            self.leftmotor.stop()
            """
        if self.countGoal < ct.const.COUNT_GOAL_LOOP_THRE:
            self.rightmotor.stopslowly()
            self.leftmotor.stopslowly()
        else:
            self.rightmotor.stop()
            self.leftmotor.stop()
        self.countGoal+= 1
        """
        
        #sys.exit()

if __name__ == "__main__":
    pass
