# -*- coding: utf-8 -*-
# Author : hejianxin
# Time : 2021/6/17 11:34 上午
from util.connect_mqtt import SubscribleBase
from business.subscrible_business import call_back_func


class SubscribleBusiness(SubscribleBase):
    def __init__(self, **kwargs):
        super(SubscribleBusiness, self).__init__(**kwargs)

    def add_listen(self, client_id):
        topic = f"face/{client_id}/response"
        self.mqtt_client.subscribe(topic)
        self.mqtt_client.loop_forever()


if __name__ == '__main__':
    client_id = ["75b994c0-578b65a4"]
    subscrible_business = SubscribleBusiness(on_connect=call_back_func.on_connect, on_message=call_back_func.on_message)
    subscrible_business.add_listen(client_id)
