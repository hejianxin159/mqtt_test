# -*- coding: utf-8 -*-
# Author : hejianxin
# Time : 2021/7/13 1:57 下午
from logger.logger import logger
import paho.mqtt.client as mqtt


def connect(host, port, username, password):
    mqtt_client = mqtt.Client()
    if all([username, password]):
        mqtt_client.username_pw_set("netmon", "netmon")
    mqtt_client.connect(host=host, port=port)
    return mqtt_client


def on_disconnect(client, userdata, rc):
    if rc == 0:
        logger.info("success disconnect")
    if rc != 0:
        logger.warn("Unexpected disconnection %s" % rc)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("business Connect success")
    else:
        logger.warn(f"Connect failed result code {str(rc)}")


def on_message(client, userdata, msg):
    logger.info(f"accept message {str(msg)}")


class ConnectBase:
    DEFAULT_CALLBACK = {
        "on_connect": on_connect,
        "on_disconnect": on_disconnect,
        "on_message": on_message
    }

    def __init__(self, **kwargs):
        self.mqtt_client = connect(*[kwargs.get(i) for i in ("mqtt_host",
                                                             "mqtt_port",
                                                             "mqtt_username",
                                                             "mqtt_password")])
        # 绑定事件函数
        call_back_method = ("on_connect", "on_disconnect", "on_message")
        for call_back in call_back_method:
            if call_back in kwargs:
                setattr(self.mqtt_client, call_back, kwargs[call_back])
            else:
                setattr(self.mqtt_client, call_back, self.DEFAULT_CALLBACK[call_back])
        # 开启事件循环
        self.mqtt_client.loop_start()
