# -*- coding: utf-8 -*-
# Author : hejianxin
# Time : 2021/6/17 10:48 上午
import json
from util.connect_mqtt import PublishBase
from business.publish_business import call_back_func


class PushFace(PublishBase):
    def __init__(self, client_id, **kwargs):
        self.topic = f"face/{client_id}/request"
        super(PushFace, self).__init__(client_id, **kwargs)

    def push_create_face(self, person_id, person_name, img_url, face_id=None, id_card=None):
        # 新增人脸信息
        push_face_info = {
                "cmd": "create_face",
                "per_id": person_id,
                "face_id": face_id if face_id else person_id,
                "per_name": person_name,
                "img_url": img_url,
        }
        if id_card:
            push_face_info["idcardper"] = id_card
        self.push(data_info=push_face_info)

    def push_update_face(self, person_id, person_name, img_url):
        # 更新人脸图片
        self.push({"img_url": img_url, "cmd": "update_face", "per_id": person_id, "per_name": person_name})

    def push_delete_face(self, person_id):
        # 删除人脸信息
        self.push({"cmd": "delete_face", "type": 0, "per_id": person_id})

    def all_user(self):
        self.push({"cmd": "get_person_info"})


if __name__ == '__main__':

    client_id = "75b994c0-578b65a4"
    op_face = PushFace(client_id, on_connect=call_back_func.on_connect)
    op_face.all_user()
    # op_face.push_delete_face("ff00ff1hjx")
    # op_face.push_delete_face("ff00ff1dzq")
    # op_face.push_create_face("123", "hejianxin", "http://10.28.25.213:8080/IMG_1227.jpeg")
    op_face.push_update_face("123", "hejianxin", "http://10.28.25.213:8080/IMG_1227.jpeg")
