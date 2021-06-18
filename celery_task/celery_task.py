# -*- coding: utf-8 -*-
# Author : hejianxin
# Time : 2021/6/17 4:34 下午

from celery import Celery, Task
from face_subscrible.subscrible import SubscribleAll
from face_subscrible import call_back_func as face_call_back
from is_online_subscrible.is_onfine_subscrible import IsOnlineSubscruble
from is_online_subscrible import call_back_func as is_online_call_back
from business.subscrible_business.upload_face import SubscribleBusiness
from business.subscrible_business import call_back_func as business_call_back


broker = 'redis://10.28.25.213:6379/5'
backend = 'redis://10.28.25.213:6379/6'
worker = Celery('tasks', broker=broker, backend=backend)


class CustomTask(Task):
    def on_success(self, retval, task_id, args, kwargs):
        print('异步任务成功')
        return super(CustomTask, self).on_success(retval, task_id, args, kwargs)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print('异步任务失败', exc)
        return super(CustomTask, self).on_failure(exc, task_id, args, kwargs, einfo)

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        print(retval)
        return super(CustomTask, self).after_return(status, retval, task_id, args, kwargs, einfo)


@worker.task(base=CustomTask)
def subscrible_all():
    # 订阅机器主动推送人脸信息
    SubscribleAll(on_connect=face_call_back.on_connect,
                  on_message=face_call_back.on_message)


@worker.task(base=CustomTask)
def is_online_subscrible(client_list):
    # 订阅设备上下线信息
    IsOnlineSubscruble(on_message=is_online_call_back.on_message,
                       on_connect=is_online_call_back.on_connect).add_listen(client_list)


@worker.task(base=CustomTask)
def subscrible_business(sn):
    # 订阅业务topic, 需要超时关闭
    client = SubscribleBusiness(on_connect=business_call_back.on_connect,
                                on_message=business_call_back.on_message,
                                on_disconnect=business_call_back.on_disconnect)
    close_business.delay(client.mqtt_client)
    client.add_listen(sn)


@worker.task(base=CustomTask)
def close_business(client):
    # 关闭未响应的business
    print(client, "wait close")
    import time
    time.sleep(10)
    client.disconnect()
