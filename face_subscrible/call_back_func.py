# -*- coding: utf-8 -*-
# Author : hejianxin
# Time : 2021/6/17 2:34 下午
import json


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("face subscrible Connect success")
        client.subscribe("face/response")
    else:
        print(f"Connect failed result code {str(rc)}")


# 收到消息的回调函数
def on_message(client, userdata, msg):
    message = str(msg.payload, encoding="utf-8")
    message = message.replace("\n", "").replace("\x00", "")
    json_message = json.loads(message)
    print(json_message)
    if json_message["type"] == "face_result":
        # face id verification successful result
        verification_face(json_message)


def verification_face(message):
    '''
    {"body": {
        "e_imgsize": 18627,
        "hat": 0,
        "idcard": "",
        "isurl": False,
        "mask": 0,
        "matched": 91,
        "name": "hejianxin",
         "name_base64": "aGVqaWFueGluAAAAAAAAAA==",
         "per_id": "123",
         "per_id_base64": "MTIzAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==",
         "role": 0,
         "sequence": 17466,
         "sn": "75b994c0-578b65a4",
         "tep": 0,
         "usec": 1623941081},
    "type": "face_result"}
    '''
    pass



