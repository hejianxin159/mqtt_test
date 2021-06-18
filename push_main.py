# -*- coding: utf-8 -*-
# Author : hejianxin
# Time : 2021/6/17 11:50 上午
from business.publish_business.upload_face import PushFace
from business.publish_business import call_back_func
from celery_task.celery_task import subscrible_all, is_online_subscrible, subscrible_business

client_id = "75b994c0-578b65a4"
op_face = PushFace(client_id, on_connect=call_back_func.on_connect)
# op_face.all_user()
# op_face.push_delete_face("ff00ff1hjx")
# op_face.push_delete_face("ff00ff1dzq")
subscrible_business.delay(client_id)
op_face.push_create_face("123", "hejianxin", "http://10.28.25.213:8080/IMG_1227.jpeg")
# op_face.push_update_face("123", "hejianxin", "http://10.28.25.213:8080/IMG_1227.jpeg")
# op_face.topic = f"face/{client_id}/response"
# op_face.custom_com("update_face")
# op_face.topic = 'face/request'
# op_face.custom_com("face_search")
