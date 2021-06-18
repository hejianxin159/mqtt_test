# -*- coding: utf-8 -*-
# Author : hejianxin
# Time : 2021/6/17 8:03 下午
import json


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connect success")
        client.subscribe("face/75b994c0-578b65a4/response")
    else:
        print(f"Connect failed result code {str(rc)}")


# 收到消息的回调函数
def on_message(client, userdata, msg):
    message = str(msg.payload, encoding="utf-8")
    message = message.replace("\n", "").replace("\x00", "")
    json_message = json.loads(message)
    print(json_message)
