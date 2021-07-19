# -*- coding: utf-8 -*-

import time
import radio_setting

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
        """
        # LoRa初期化
        self.sendDevice.reset_lora()
        """
        """
        # LoRa設定コマンド
        set_mode = ['1', 'd', self.channel, 'e', self.panid, 'f', self.ownid, 'g', self.dstid,
                    'l', '2', 'n', '1', 'p', '1', 'y', 'z']
                    #l:Ack(ON), n:転送モード(Payload), p:受信電波強度, y:show, z:start
        #os.system("sudo insmod soft_uart.ko")#os
                
        # LoRa設定
        self.sendDevice.setup_lora(set_mode)
        """
        # LoRa設定
        self.sendDevice.setup_lora()
    
    # ES920LRデータ送信メソッド
    def sendData(self, datalog):        
        # LoRa(ES920LR)データ送信
        #print(datalog)
        self.sendDevice.cmd_lora(datalog)
    
    def switchData(self, datalog):
        self.sendDevice.cmd_lora(datalog)
        while True:
            if self.sendDevice.device.inWaiting() > 0:
                
                line = self.sendDevice.device.readline()
                line = line.decode("utf-8")
                
                #print('wait lost...')
                
                if line.find('RSSI') >= 0 and line.find('information') == -1:
                    
                    log = line
                    log_list = log.split('):Receive Data(')
                    
                    #print(log_list)
                    # 受信電波強度

                    self.cansat_rssi = int(log_list[0][5:8])#0-4
                    #self.cansat_rssi = log_list[0][5:11]#0-4
                    #print(rssi)#自分が受けたRSSI
                    # 受信フレーム
                    self.lost_rssi = int(log_list[1][0:3])#1-最後から3番目の1個前まで
                    #print('Receive'+ data)
                    #print('-------------')
                    break
                  

        
        