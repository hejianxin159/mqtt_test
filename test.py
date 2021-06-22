# -*- coding: utf-8 -*-
# Author : hejianxin
# Time : 2021/6/21 9:08 上午
from util.connect_mqtt import SubscribleBase
from face_subscrible import call_back_func


class SubscribleFace(SubscribleBase):
    def __init__(self, **kwargs):
        super(SubscribleFace, self).__init__(**kwargs)
        self.mqtt_client.loop_start()

    def add_listen(self, client_id):
        self.mqtt_client.subscribe(client_id)
        print("add listen topic success")

    

if __name__ == '__main__':
    sub_face = SubscribleFace(on_connect=call_back_func.on_connect,
                              on_message=call_back_func.on_message)
    sub_face.add_listen("123")
    sub_face.add_listen("123")
    sub_face.add_listen("123")
    sub_face.add_listen("123")

