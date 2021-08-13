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
        # LoRa初期化
        self.switDevice.reset_lora()
        # LoRa設定コマンド
        set_mode = ['1', 'd', self.channel, 'e', '0001', 'f', '0002', 'g', '0001',
                    'n', '2', 'l', '2', 'p', '1', 'y', 'z']
        # LoRa設定
        self.switDevice.setup_lora(set_mode)
        # LoRa(ES920LR)受信待機
        while True:
#             print("enter the loop")
            try:
                # ES920LRモジュールから値を取得
                if self.switDevice.device.inWaiting() > 0:
                    try:
                        start=time.time()
                        line = self.switDevice.device.readline()
                        line = line.decode("utf-8")
                        
#                         print("line:"+str(line))
                        if line.find('RSSI') >= 0 and line.find('information') == -1:
                            
                            start=time.time()
                            log = line
                            log_list = log.split('dBm')
                            
                            # 受信電波強度
                            
# #                             rssi = float(log_list[0][5:])
                            rssi = log_list[0][5:]
#                             print(rssi)
                            time1=time.time()-start
                            time1_=time.time()
                            print("time1:"+str(time1))

                            #senddata
                            senddata = rssi #strよりfloatの方がはやい
#                             senddata=str(rssi)
                            time2=time.time()-time1_
                            time3=time.time()-start
                            print("time2:"+str(time2))
                            print("time3:"+str(time3))
                            
                            print('<-- SEND -- [ {} ]'.format(senddata))
                            self.switDevice.cmd_lora('{}'.format(senddata))
                            print('------------')
                    except Exception as e:
                        print(e)
                        continue   
            except KeyboardInterrupt:
                self.switDevice.close()
# print("hello")
# 
# def say_hello():
#     print("hello")
#     
# if __name__ == '__main__':
#     say_hello()
#     
