# -*- coding: utf-8 -*-
# Author : hejianxin
# Time : 2021/6/17 3:01 下午
from util.connect_mqtt import SubscribleBase
from is_online_subscrible import call_back_func


class IsOnlineSubscruble(SubscribleBase):
    def __init__(self, **kwargs):
        super(IsOnlineSubscruble, self).__init__(**kwargs)

    def add_listen(self, client_list):
        for client_id in client_list:
            self.mqtt_client.subscribe(f"will/{client_id}/response")
        self.mqtt_client.loop_forever()


if __name__ == '__main__':
    client_id = "75b994c0-578b65a4"
    is_online_subscruble = IsOnlineSubscruble(on_connect=call_back_func.on_connect,
                                              on_message=call_back_func.on_message)
    is_online_subscruble.add_listen([client_id])
