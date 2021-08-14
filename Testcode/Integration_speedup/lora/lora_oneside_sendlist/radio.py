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
        
    def receiveData(self):
            # ES920LRモジュールから値を取得
        isReceive=0
        cansat_rssi = 0
        log_meanstd=0
        lost_mean= 0
        lost_std=0
        if self.sendDevice.device.inWaiting() > 0:
            
            line = self.sendDevice.device.readline()
            line = line.decode("utf-8")
            
           # print(line)
            if line.find('RSSI') >= 0 and line.find('information') == -1:
                log = line
             #   print(line)                    
                log_list = log.split('dBm):PAN ID(0001):Src ID(0000):Receive Data(')            
              #karakanakamiarukasiraberuhensuu  
                cansat_rssi = float(log_list[0][5:])#0-4   
#                     self.lost_rssi = float(log_list[1][0:-3])
#                   
                lost_meanstd =log_list[1][0:-2]
                lost_meanstd_list = lost_meanstd.split(',')
                lost_mean = lost_meanstd_list[0][0:]
                lost_std = lost_meanstd_list[1][0:]
                print(lost_meanstd)
                print(lost_mean)
                print(lost_std)
                
                isReceive=1
        
    
        return isReceive,cansat_rssi,lost_mean,lost_std
    
    def switchData(self, datalog):
#         self.sendDevice.cmd_lora(datalog)
        lstate = 0
        lstart_time = time.time()
        lost_mean=0
        lost_std=0
#         while True:
#             self.receiveData()
            
        while True:
            
            if lstate == 0:
                # send only
#                 print('state:'+str(lstate))
                if  time.time()-lstart_time  > 10:
                    lstate = 1
                else:
                    self.sendData(datalog)
#                     time.sleep(0.5)
                
            elif lstate == 1:
                print('state:'+str(lstate))
                # send and receive
              
#                     t_start=time.time()
                isReceive,cansat_rssi,lost_mean,lost_std = self.receiveData()
                print(isReceive)
                if isReceive ==1:
                    lstate=2
                    
                else:
                    self.sendData(datalog)
                    
                    
#                     while time.time() - t_start < 1:
#                         if isReceive ==1:
#                             lstate = 2
#                             break
                 
            elif lstate == 2:
                print('state:'+str(lstate))
                # receive
                isReceive,cansat_rssi,lost_mean,lost_std=self.receiveData()
                if isReceive==1:                       
                    self.LogCansatRSSI.append(cansat_rssi)
                    
                    # store data
                elif len(self.LogCansatRSSI) > 30:                       
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
        
  


        
        
