# -*- coding: utf-8 -*-
# Author : hejianxin
# Time : 2021/6/16 4:39 下午

import paho.mqtt.client as mqtt


mqtt_host = "10.28.25.213"
mqtt_port = 1883
mqtt_username = "netmon"
mqtt_password = "netmon"


def connect(host=mqtt_host, port=mqtt_port, username=mqtt_username, password=mqtt_password):
    mqtt_client = mqtt.Client()
    if all([username, password]):
        mqtt_client.username_pw_set("netmon", "netmon")
    mqtt_client.connect(host=host, port=port)
    return mqtt_client


