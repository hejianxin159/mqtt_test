# -*- coding: utf-8 -*-
# Author : hejianxin
# Time : 2021/6/16 5:46 下午

from util.connect_mqtt import connect
import json


client_id = "75b994c0-578b65a4"


# 连接的回调函数
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {str(rc)}")
    client.subscribe(f"face/{client_id}/response")
    # client.subscribe(f"face/response")


# 收到消息的回调函数
def on_message(client, userdata, msg):
    message = str(msg.payload, encoding="utf-8")
    message = message.replace("\n", "").replace("\x00", "")
    print(json.loads(message))


# client = mqtt.Client()
# client.on_connect = on_connect
# client.on_message = on_message
# client.username_pw_set("netmon", "netmon")
# client.connect("10.28.25.213", 1883, 60)
client = connect()
client.on_connect = on_connect
client.on_message = on_message

client.loop_forever()
