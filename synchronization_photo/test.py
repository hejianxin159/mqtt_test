# -*- coding: utf-8 -*-
# Author : hejianxin
# Time : 2021/6/18 4:47 下午
from celery_task.celery_task import subscrible_all, is_online_subscrible, subscrible_business
from util.connect_mqtt import PublishBase
from models.models import Camera, db_session
from business.subscrible_business.upload_face import SubscribleBusiness



def start_listen_device(client_id):
    subscrible_business.delay(client_id)



def search_device(client_id):
    # 查看设备是否在线
    publish = PublishBase(client_id)
    publish.topic = "face/request"
    publish.custom_com("face_search")


if __name__ == '__main__':
    client_id = "75b994c0-578b65a4"
    start_listen_device(client_id)
    search_device(client_id)

