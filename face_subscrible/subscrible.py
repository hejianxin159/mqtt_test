# -*- coding: utf-8 -*-
# Author : hejianxin
# Time : 2021/6/17 2:28 下午
from util.connect_mqtt import SubscribleBase
from face_subscrible import call_back_func


class SubscribleAll(SubscribleBase):
    def __init__(self, **kwargs):
        super(SubscribleAll, self).__init__(**kwargs)


if __name__ == '__main__':
    subscrible_all = SubscribleAll(on_connect=call_back_func.on_connect, on_message=call_back_func.on_message)

