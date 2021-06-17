# -*- coding: utf-8 -*-
# Author : hejianxin
# Time : 2021/6/17 11:34 上午
from util.connect_mqtt import connect
from business.subscrible_business import call_back_func


class SubscribleBusiness:
    def __init__(self):
        mqtt_client = connect()
        mqtt_client.on_connect = call_back_func.on_connect
        mqtt_client.on_message = call_back_func.on_message
        self.mqtt_client = mqtt_client

    def add_listen(self, client_id):
        topic = f"face/{client_id}/response"
        self.mqtt_client.subscribe(topic)
        self.mqtt_client.loop_forever()


if __name__ == '__main__':
    client_id = "75b994c0-578b65a4"
    subscrible_business = SubscribleBusiness()
    subscrible_business.add_listen(client_id)
    subscrible_business.add_listen(client_id)
    subscrible_business.add_listen(client_id)
