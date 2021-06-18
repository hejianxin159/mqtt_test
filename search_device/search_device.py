# -*- coding: utf-8 -*-
# Author : hejianxin
# Time : 2021/6/17 8:03 下午

from util.connect_mqtt import SubscribleBase
# from search_device import call_back_func
import call_back_func


class SearchDevice(SubscribleBase):
    def __init__(self, **kwargs):
        super(SearchDevice, self).__init__(**kwargs)
        self.mqtt_client.loop_forever()


if __name__ == '__main__':
    subscrible_all = SearchDevice(on_connect=call_back_func.on_connect, on_message=call_back_func.on_message)

