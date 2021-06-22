# -*- coding: utf-8 -*-
# Author : hejianxin
# Time : 2021/6/16 4:39 下午

import paho.mqtt.client as mqtt
import json


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


class ConnectBase:
    def __init__(self, **kwargs):
        mqtt_client = connect()
        # 绑定事件函数
        if "on_connect" in kwargs:
            mqtt_client.on_connect = kwargs["on_connect"]
        if "on_disconnect" in kwargs:
            mqtt_client.on_disconnect = kwargs["on_disconnect"]
        if "on_message" in kwargs:
            mqtt_client.on_message = kwargs["on_message"]
        self.mqtt_client = mqtt_client


class PublishBase(ConnectBase):
    def __init__(self, client_id, **kwargs):
        self.client_id = client_id
        super(PublishBase, self).__init__(**kwargs)

    def push(self, data_info):
        base_data = {
            "client_id": self.client_id,
            "version": "0.2",
        }
        base_data.update(data_info)
        self.mqtt_client.publish(self.topic, payload=json.dumps(base_data), qos=0)

    def custom_com(self, cmd):
        self.push({"cmd": cmd})


class SubscribleBase(ConnectBase):
    def __init__(self, **kwargs):
        super(SubscribleBase, self).__init__(**kwargs)

