##シャットダウンボタンを押したらシャットダウンコードが実行される
##ラズパイ側で起動時に自動実行の設定する必要有
##詳細1 https://www.raspberrypirulo.net/entry/systemd
##詳細2 https://qiita.com/K-Ponta/items/12127d7077d69a82693c
'''
etcの下にあるrc.local ファイルを編集して、起動時にプログラムを実行するようにしています。

pi@raspberrypi:~ $ sudo vi /etc/rc.local 

#exit 0 の前の1行が追加したコードになります。
/etc/rc.local内に

/home/pi/bin/shutdown.py（パス取得）
exit 0

を追加後、Rsapberry Piを再起動すると設定が反映されます。
'''
import time
import RPi.GPIO as GPIO
import os
import constant as ct

GPIO.setmode(GPIO.BCM)
GPIO.setup(25,GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        GPIO.wait_for_edge(25, GPIO.FALLING)
        sw_counter = 0

        while True:
            sw_status = GPIO.input(25)

            if sw_status == 0:
                sw_counter = sw_counter + 1
                if sw_counter >= 200: #2秒以上押し続けるとshutdownコマンド実行
                    os.system("sudo shutdown -h now")
                    break
            else:
                break

            time.sleep(0.01)

except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()