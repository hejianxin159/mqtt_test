# -*- coding: utf-8 -*-
# Author : hejianxin
# Time : 2021/6/17 2:32 下午

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("connect success")
    else:
        print(f"Connect failed result code {rc}")


def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection %s" % rc)
