# -*- coding: utf-8 -*-

import time
import radio_setting
import re

# LoRa送信用クラス
class radio(object):
    
    def __init__(self):
        # ES920LRデバイス名
        # ラズパイ3で使うときはttySOFT0
        # ラズパイ4で使うときはttyAMA1
        self.lora_device = "/dev/ttyAMA1"
        self.cansat_rssi=0
        self.lost_rssi=0
        """
        #config設定
        self.channel = 15   #d
        self.panid = '0001' #e
        self.ownid = '0001' #f
        self.dstid = '0000' #g
        """
        
        self.sendDevice = radio_setting.LoraSettingClass(self.lora_device)
        
    def setupRadio(self):
        # LoRa設定
        self.sendDevice.setup_lora()
    
    # ES920LRデータ送信メソッド
    def sendData(self, datalog):        
        # LoRa(ES920LR)データ送信
        #print(datalog)
        self.sendDevice.cmd_lora(datalog)
        
    def recieveData(self):
            # ES920LRモジュールから値を取得
        isReceive=0
        mean=0
        std=0
        if self.sendDevice.device.inWaiting() > 0:
            
            line = self.sendDevice.device.readline()
            line = line.decode("utf-8")
            
            print(line)
            if line.find('RSSI') >= 0 and line.find('information') == -1:
                log = line
                print(line)                    
                log_list = log.split('dBm):PAN ID(0001):Src ID(0000):Receive Data(')            
              #karakanakamiarukasiraberuhensuu  
                cansat_rssi = float(log_list[0][5:])#0-4   
#                     self.lost_rssi = float(log_list[1][0:-3])
#                   
                lost_mean =log_list[1][0:-2] # lost mean [0:-2]change
                lost_std =log_list[1][0:-2] # lost std

                isReceive=1
        
    
        return isReceive,cansat_rssi,lost_mean,lost_std
    
    def switchData(self, datalog):
#         self.sendDevice.cmd_lora(datalog)
        lstate = 0
        lstart_time = time.time()
#         while True:
#             self.recieveData()
            
        while True:
            if lstate == 0:
                # send only
                if lstart_time - time.time() > 20:
                    lstate = 1
                else:
                    self.sendData("a")
                    time.sleep(0.5)
                
            elif lstate == 1:
                # send and recieve
                self.sendData("b")
                t_start=time.time()
                while time.time() - t_start < 2:
                    if self.sendDevice.device.inWaiting() > 0:
                        lstate = 2
                        break
                 
            elif lstate == 2:
                # recieve
                
                while True:
                    isReceive,cansat_rssi,lost_mean,lost_std=self.recieveData()
                    self.LogCansatRSSI.append(cansat_rssi)
                    
                    # store data
                    if len(self.LogCansatRSSI) > 10:                       
                        break
                                                                                   
            if self.sendDevice.device.inWaiting() <= 0:
                self.sendDevice.cmd_lora(datalog)
                print("sending")
#                 time.sleep(10)                
            elif self.sendDevice.device.inWaiting() > 0:
                start=time.time()

                line = self.sendDevice.device.readline()
                line = line.decode("utf-8")

                if line.find('RSSI') >= 0 and line.find('information') == -1:        

#                        
                    log = line
                    print(line)                    
                    log_list = log.split('dBm):PAN ID(0001):Src ID(0000):Receive Data(')

                    
                    self.cansat_rssi = float(log_list[0][5:])#0-4   
#                     self.lost_rssi = float(log_list[1][0:-3])
#                   
                    self.lost_rssi =log_list[1][0:-1]
                    
#                     time3=time.time()-time2_
#                     time3_=time.time()
#                     print("time3:"+str(time3))
#
                else:
                    log = line
                    print(line)                    
                    log_list = log.split('dBm):PAN ID(0001):Src ID(0000):Receive Data(')
#                     time2=time.time()-time1_
#                     time2_=time.time()
#                     print("time2:"+str(time2))
              
                    
                    self.cansat_rssi = float(log_list[0][5:])#0-4   
#                     self.lost_rssi = float(log_list[1][0:-3])
#                                                                          
                    print('-------------')
                    break

    def estimate_distance_Cansat(self,meanCansatRSSI):
        #定義式より推定 
        N_Cansat=2.933
        MP_Cansat=-37.43
       
        return 10**((MP_Cansat-meanCansatRSSI)/(10*N_Cansat))       
    
    def estimate_distance_Lost(self,meanLostRSSI):
        #定義式より推定
        N_Lost=2.933
        MP_Lost=-37.30

        return 10**((MP_Lost-meanLostRSSI)/(10*N_Lost))
        
  


        
        
