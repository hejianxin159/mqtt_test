# -*- coding: utf-8 -*-
# Author : hejianxin
# Time : 2021/6/17 2:30 下午
import json


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connect success")
    else:
        print(f"Connect failed result code {str(rc)}")


# 收到消息的回调函数
def on_message(client, userdata, msg):
    message = str(msg.payload, encoding="utf-8")
    message = message.replace("\n", "").replace("\x00", "")
    json_message = json.loads(message)
    if json_message["cmd"] == "update_face":
        update_face(json_message)
    elif json_message["cmd"] == "create_face":
        create_face(json_message)
    elif json_message["cmd"] == "delete_face":
        delete_face(json_message)
    elif json_message["cmd"] == "get_person_info":
        all_user(json_message)
    else:
        print("not func")
        print(json_message)
    # 关闭连接
    client.disconnect()


def create_face(data_info):
    print(data_info)


def update_face(data_info):
    print(data_info)


def delete_face(data_info):
    print(data_info)


def all_user(data_info):
    print(data_info)
