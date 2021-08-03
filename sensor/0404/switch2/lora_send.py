# -*- coding: utf-8 -*-
import time
import lora_setting


# LoRa送信用クラス
class LoraSendClass:

    def __init__(self, lora_device, channel):
        self.sendDevice = lora_setting.LoraSettingClass(lora_device)
        self.channel = channel
        
#           try:  # インスタンス変数 serialDevice を生成
#             self.device = serial.Serial(lora_device, 9600)
#           except Exception as e:
#                 error_mes = '{0}'.format(e)
#                 print(error_mes)
#           self.cmd = None
#           self.reset_pin = 11
#           self.set_mode = None

    # ES920LRデータ送信メソッド
    def lora_send(self):
        # LoRa初期化
        self.sendDevice.reset_lora()
        # LoRa設定コマンド
        set_mode = ['1', 'd', self.channel, 'e', '0001', 'f', '0001', 'g', '0002',
                    'l', '2', 'n', '2', 'p', '1', 'y', 'z']
        # LoRa設定
        self.sendDevice.setup_lora(set_mode)
      #  self.recvDevice.setup_lora(set_mode)
        
        # LoRa(ES920LR)データ送信
        while True:
            try:
                # 送るデータ
                data = 'aaaa'
                print('<-- SEND -- [00010002 {} ]'.format(data))
                self.sendDevice.cmd_lora('00010002{}'.format(data))
                
                  # ES920LRモジュールから値を取得
                if self.sendDevice.device.inWaiting() > 0:
                    try:
                        line = self.sendDevice.device.readline()
                        line = line.decode("utf-8")
                    except Exception as e:
                        print(e)
                        continue
                    print(line)
                    if line.find('RSSI') >= 0 and line.find('information') == -1:
                        log = line
                        log_list = log.split('):Receive Data(')
                        # 受信電波強度
                        rssi = log_list[0][5:]
                        print(rssi)
                        # 受信フレーム
                        data = log_list[1][:-3]
                        print(data)
                
            except KeyboardInterrupt:
                self.sendDevice.close()
                
           
            # 0.5秒待機
            time.sleep(5)
