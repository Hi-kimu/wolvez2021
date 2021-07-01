# -*- coding: utf-8 -*-
import lora_setting


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
            try:
                # ES920LRモジュールから値を取得
                if self.switDevice.device.inWaiting() > 0:
                    try:
                        line = self.switDevice.device.readline()
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
                        #senddata
                        senddata = rssi #ここの型をstringにする必要あるかも
                        #print('<-- SEND -- [00010002 {} ]'.format(senddata))
                        print('<-- SEND -- [ {} ]'.format(senddata))
                        #self.switDevice.cmd_lora('00010002{}'.format(senddata))
                        self.switDevice.cmd_lora('{}'.format(senddata))
            except KeyboardInterrupt:
                self.recvDevice.close()
                
