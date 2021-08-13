# -*- coding: utf-8 -*-
import lora_setting
import time

# LoRa送受信用クラス（受信したらRSSIを送り返す）
class LoraSwitClass:

    def __init__(self, lora_device, channel):
        self.switDevice = lora_setting.LoraSettingClass(lora_device)
        self.channel = channel

    # ES920LRデータ送受信メソッド
    def lora_swit(self):
        LogLostRSSI=list()
        lstate= 0 
        # LoRa初期化
        self.switDevice.reset_lora()
        # LoRa設定コマンド
        set_mode = ['1', 'd', self.channel, 'e', '0001', 'f', '0002', 'g', '0001',
                    'n', '2', 'l', '2', 'p', '1', 'y', 'z']
        # LoRa設定
        self.switDevice.setup_lora(set_mode)
        # LoRa(ES920LR)受信待機
        while True:
            try:
                if lstate == 0
                    isReceive,lost_rssi=self.recieveData()
                    LogLostrssi.append(lost_rssi)
                    if len(LogLostrssi) > 10:
                        lstate == 1
                        
                if  lstate == 1
                    mean = np.meanCansat 
                    self.SendData()
                    t_start=time.time()
                    
                    if time.time() - t_start > 20
                                        
                    
                if self.switDevice.device.inWaiting() > 0:
                    try:
#                         start=time.time()
                        line = self.switDevice.device.readline()
                        line = line.decode("utf-8")
                        
#                         print("line:"+str(line))
                        if line.find('RSSI') >= 0 and line.find('information') == -1:
                            print('Get')
#                             start=time.time()
                            log = line
                            log_list = log.split('dBm')                      
                            LogLostRSSI.append(float(log_list[0][5:]))
#                             LogLostRSSIa=list()
#                             for i in range(1):
#                                 LogLostRSSIa.append(-56.0)
#                             print(LogLostRSSIa)
                                                                                 

                        elif len(LogLostRSSI)>=7:
                             #cansat機側のconst.SWITCH_LOOP_THREとそろえるコード書く
                            for i in range 
                                self.switDevice.cmd_lora("")
                            
                            senddata = LogLostRSSI #strよりfloatの方がはやい
                            self.switDevice.cmd_lora(LogLostRSSI)
                            print('<-- SEND -- [ {} ]'.format(senddata))
                            
                            time.sleep(5)
                            
                            for i in range()
                                self.switDevice.cmd_lora("a")
                            
                            
#                             #cansat機側のconst.SWITCH_LOOP_THREとと同じ回数だけ送るコード書く
#                             for i in LogLostRSSI:
#                                 self.switDevice.cmd_lora(LogLostRSSI)
# #                                 print('<-- SEND -- [ {} ]'.format(float(i)))
#                                 time.sleep(1)
                                
                                #self.switDevice.cmd_lora('{}'.format(senddata))
                            
                            LogLostRSSI=list()
                            print('------------')
                            
                            
                    except Exception as e:
                        print(e)
                        continue

            except KeyboardInterrupt:
                self.switDevice.close()
                
