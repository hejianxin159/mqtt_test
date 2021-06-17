# -*- coding: utf-8 -*-
# Author : hejianxin
# Time : 2021/6/17 3:01 下午
from util.connect_mqtt import connect
from is_online_subscrible import call_back_func


def is_online_subscruble(client_list):
    mqtt_client = connect()
    mqtt_client.on_connect = call_back_func.on_connect
    mqtt_client.on_message = call_back_func.on_message
    mqtt_client.subscribe("online/response")
    for client_id in client_list:
        mqtt_client.subscribe(f"will/{client_id}/response")
    mqtt_client.loop_forever()


if __name__ == '__main__':
    client_id = "75b994c0-578b65a4"
    is_online_subscruble([client_id])
