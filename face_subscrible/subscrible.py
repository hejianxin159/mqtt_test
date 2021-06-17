# -*- coding: utf-8 -*-
# Author : hejianxin
# Time : 2021/6/17 2:28 下午
from util.connect_mqtt import connect
from face_subscrible import call_back_func


def subscrible_all():
    mqtt_client = connect()
    mqtt_client.on_connect = call_back_func.on_connect
    mqtt_client.on_message = call_back_func.on_message
    mqtt_client.loop_forever()


if __name__ == '__main__':
    subscrible_all()


