# -*- coding: utf-8 -*-

import lora_swit

def main():
    #lora_device = "/dev/ttyS0"  # ES920LRデバイス名
    lora_device = "/dev/ttyAMA1" # ES920LRデバイス名
    channel=15

    # 送信側の場合
    try:
        while True:
            lr_swit = lora_swit.LoraSwitClass(lora_device, channel)
            lr_swit.lora_swit()
        
    except KeyboardInterrupt:
        print('finished')
        pass

main()
    
# if __name__ == '__main__':
#     main(len(sys.argv), sys.argv)
#     sys.exit()

