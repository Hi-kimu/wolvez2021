# -*- coding: utf-8 -*-
import lora_setting
import time
import numpy as np
import math

# LoRa送受信用クラス（受信したらRSSIを送り返す）
class LoraSwitClass:

    def __init__(self, lora_device, channel):
        self.lora_device = lora_device
        self.switDevice = lora_setting.LoraSettingClass(self.lora_device)
        self.channel = channel
        self.sendDevice = lora_setting.LoraSettingClass(self.lora_device)
        

    def sendData(self,lost_meanstd):
        self.sendDevice.cmd_lora(lost_meanstd)
    
    def receiveData(self):
        # ES920LRモジュールから値を取得
        isReceive=0
        lost_rssi = 0

        if self.sendDevice.device.inWaiting() > 0:
            
            line = self.sendDevice.device.readline()
            line = line.decode("utf-8")
            
           # print(line)
            if line.find('RSSI') >= 0 and line.find('information') == -1:
                log = line
              #  print(line)                    
                log_list = log.split('dBm):PAN ID(0001):Src ID(0001):Receive Data(')            
              #karakanakamiarukasiraberu hensuu  
                lost_rssi = float(log_list[0][5:])#0-4   
    #                     self.lost_rssi = float(log_list[1][0:-3])
                isReceive=1       

        return isReceive,lost_rssi

    
    
    # ES920LRデータ送受信メソッド
    def lora_swit(self):
        LogLostRSSI=list()
        lstate= 0 
        # LoRa初期化
        self.switDevice.reset_lora()
        # LoRa設定コマンド
        set_mode = ['1', 'd', self.channel, 'e', '0001', 'f', '0000', 'g', '0001',
                    'n', '2', 'l', '2', 'p', '1', 'y', 'z']
        
        # LoRa設定
        self.switDevice.setup_lora(set_mode)
        # LoRa(ES920LR)受信待機
        while True:
            try:
                if lstate == 0:
#                     print("state:"+str(lstate))
                    isReceive,lost_rssi=self.receiveData()
                    if isReceive == 1:
                        LogLostRSSI.append(lost_rssi)
                        print(LogLostRSSI)
                        
                        if len(LogLostRSSI) > 3:
                            t_start=time.time()
                            lstate = 1                            
                        
                elif lstate == 1:
                    print("state:"+str(lstate))
                    lost_mean = round((np.mean(LogLostRSSI)),3)
                    lost_std = round(np.std(LogLostRSSI),4)
                    lost_meanstd= [lost_mean,lost_std]
                    print(lost_meanstd)
                    self.sendData(lost_meanstd)
                                       
                    if time.time() - t_start > 10:
                        lstate = 2
                        
                elif lstate == 2:
                    print("state:"+str(lstate))
                    isReceive,lost_rssi=self.receiveData()
                    if isReceive == 1:
                        LogLostRSSI = 0
                        lstate == 0
                                            
                    else:
                        self.sendData(lost_meanstd)
                        
                        
                        
                
#                     
#                 if self.switDevice.device.inWaiting() > 0:
#                     try:
# #                         start=time.time()
#                         line = self.switDevice.device.readline()
#                         line = line.decode("utf-8")
#                         
# #                         print("line:"+str(line))
#                         if line.find('RSSI') >= 0 and line.find('information') == -1:
#                             print('Get')
# #                             start=time.time()
#                             log = line
#                             log_list = log.split('dBm')                      
#                             LogLostRSSI.append(float(log_list[0][5:]))
# #                             LogLostRSSIa=list()
# #                             for i in range(1):
# #                                 LogLostRSSIa.append(-56.0)
# #                             print(LogLostRSSIa)
#                                                                                  
# 
#                         elif len(LogLostRSSI)>=7:
#                              #cansat機側のconst.SWITCH_LOOP_THREとそろえるコード書く
#                             for i in range 
#                                 self.switDevice.cmd_lora("")
#                             
#                             senddata = LogLostRSSI #strよりfloatの方がはやい
#                             self.switDevice.cmd_lora(LogLostRSSI)
#                             print('<-- SEND -- [ {} ]'.format(senddata))
#                             
#                             time.sleep(5)
#                             
#                             for i in range():
#                                 self.switDevice.cmd_lora("a")
#                             
#                             
# #                             #cansat機側のconst.SWITCH_LOOP_THREとと同じ回数だけ送るコード書く
# #                             for i in LogLostRSSI:
# #                                 self.switDevice.cmd_lora(LogLostRSSI)
# # #                                 print('<-- SEND -- [ {} ]'.format(float(i)))
# #                                 time.sleep(1)
#                                 
#                                 #self.switDevice.cmd_lora('{}'.format(senddata))
#                             
#                             LogLostRSSI=list()
#                             print('------------')
#                             
#                             
#                     except Exception as e:
#                         print(e)
#                         continue
# 
            except KeyboardInterrupt:
                self.switDevice.close()
                
