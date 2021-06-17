# -*- coding: utf-8 -*-
# Author : hejianxin
# Time : 2021/6/17 11:50 上午
from business.publish_business.upload_face import PushFace
from business.publish_business import call_back_func

client_id = "75b994c0-578b65a4"
op_face = PushFace(client_id, on_connect=call_back_func.on_connect)
# op_face.all_user()
# op_face.push_delete_face("ff00ff1hjx")
# op_face.push_delete_face("ff00ff1dzq")
# op_face.push_create_face("123", "hejianxin", "http://10.28.25.213:8080/IMG_1227.jpeg")
op_face.push_update_face("123", "hejianxin", "http://10.28.25.213:8080/IMG_1227.jpeg")
# op_face.custom_com("reboot_cam")
