#!/bin/sh
#シャットダウンボタンのセットアップ
#Last update 2020/07/25 Hikaru Kimura
#<<実行方法>>
#bash setup_shutdown.sh
#./setup_shutdown.sh
#上記２つのどちらかのコマンドをターミナルに打ち込む
#<<準備>>
#/home/piにshutdown.pyをおいておく

#serviceファイルの作成
#以下の項目追加
sudo bash -c "cat >> /lib/systemd/system/shutdown.service" <<EOF
[Unit]
Description = shutdown

[Service]
ExecStart=/usr/bin/python3 /home/pi/shutdown.py
Restart=always
Type=simple

[Install]
WantedBy=multi-user.target
EOF

#ラズパイ起動時にサービスを自動起動
sudo systemctl enable shutdown.service

#実行権限を与える
sudo chmod +x setup_shutdown.sh

#設定完了の喜びの舞
echo -e "<<設定完了のおしらせ>>\nおめでとう！設定完了だ！あとでrebootしてね。"
