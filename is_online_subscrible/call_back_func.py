# -*- coding: utf-8 -*-
# Author : hejianxin
# Time : 2021/6/17 3:05 下午
import json


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("connect success")
    else:
        print(f"Connect failed result code {rc}")


# 收到消息的回调函数
def on_message(client, userdata, msg):
    message = str(msg.payload, encoding="utf-8")
    message = message.replace("\n", "").replace("\x00", "")
    json_message = json.loads(message)
    if json_message["cmd"] == "mqtt_lwt":
        device_offline(json_message)
    elif json_message["cmd"] == "mqtt_online":
        device_online(json_message)


def device_offline(message):
    print(message)


def device_online(message):
    '''
    {
        'cmd': 'mqtt_online',
         'result': 'mqtt is online',
         'sn': '75b994c0-578b65a4'
    }
    '''
    print(message)
