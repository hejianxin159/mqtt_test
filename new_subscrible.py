# -*- coding: utf-8 -*-
# Author : hejianxin
# Time : 2021/6/21 11:21 上午

import paho.mqtt.client as mqtt
import json
from models.models import db_session, Camera, PersonSync, PersonResource, Attachment


mqtt_host = "10.28.25.213"
mqtt_port = 1883
mqtt_username = "netmon"
mqtt_password = "netmon"


def connect(host=mqtt_host, port=mqtt_port, username=mqtt_username, password=mqtt_password):
    mqtt_client = mqtt.Client()
    if all([username, password]):
        mqtt_client.username_pw_set("netmon", "netmon")
    mqtt_client.connect(host=host, port=port)
    return mqtt_client


class ConnectBase:
    def __init__(self, **kwargs):
        self.mqtt_client = connect()
        # 绑定事件函数
        if "on_connect" in kwargs:
            self.mqtt_client.on_connect = kwargs["on_connect"]
        if "on_disconnect" in kwargs:
            self.mqtt_client.on_disconnect = kwargs["on_disconnect"]
        if "on_message" in kwargs:
            self.mqtt_client.on_message = kwargs["on_message"]
        self.mqtt_client.loop_start()


# class BusinessBase(ConnectBase):
#     def __init__(self, **kwargs):
#         super(BusinessBase, self).__init__(**kwargs)
#
#     def push(self, data_info):
#         base_data = {
#             "version": "0.2",
#         }
#         base_data.update(data_info)
#         self.mqtt_client.publish(self.topic, payload=json.dumps(base_data), qos=0)
#
#     def custom_com(self, client_id, cmd):
#         self.push({"cmd": cmd, "client_id": client_id})
#
#
# class Business(BusinessBase):
#     def __init__(self, **kwargs):
#         super(Business, self).__init__(**kwargs)
#         self.mqtt_client.loop_start()
#         self.mqtt_client.is_message = 0
#
#     def add_listen(self, topics):
#         self.mqtt_client.subscribe(topics)
#
#     def push_create_face(self, person_id, person_name, img_url, face_id=None, id_card=None):
#         # 新增人脸信息
#         push_face_info = {
#                 "cmd": "create_face",
#                 "per_id": person_id,
#                 "face_id": face_id if face_id else person_id,
#                 "per_name": person_name,
#                 "img_url": img_url,
#         }
#         if id_card:
#             push_face_info["idcardper"] = id_card
#         self.push(data_info=push_face_info)
#
#     def push_update_face(self, person_id, person_name, img_url):
#         # 更新人脸图片
#         self.push({"img_url": img_url, "cmd": "update_face", "per_id": person_id, "per_name": person_name})
#
#     def push_delete_face(self, person_id):
#         # 删除人脸信息
#         self.push({"cmd": "delete_face", "type": 0, "per_id": person_id})
#
#     def all_user(self):
#         self.push({"cmd": "get_person_info"})


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("business Connect success")
    else:
        print(f"Connect failed result code {str(rc)}")


# 收到消息的回调函数
def on_message(client, userdata, msg):
    message = str(msg.payload, encoding="utf-8")
    message = message.replace("\n", "").replace("\x00", "")
    json_message = json.loads(message)
    if json_message["cmd"] == "update_face":
        update_face(json_message)
    elif json_message["cmd"] == "create_face":
        create_face(json_message)
    elif json_message["cmd"] == "delete_face":
        delete_face(json_message)
    elif json_message["cmd"] == "get_person_info":
        all_user(json_message)
    elif json_message["cmd"] == "face_search":
        face_search(client, json_message)
    else:
        print("not func")
        print(json_message)
    # 关闭连接
    # client.disconnect()
    client.is_success = 1
    # client.loop_stop()


def on_disconnect(client, userdata, rc):
    if rc == 0:
        print("success disconnect")
    if rc != 0:
        print("Unexpected disconnection %s" % rc)


def is_synchronization(person_id, project_id):
    # 查看是否同步成功
    person_camera = []
    use_camera = []
    for camera in db_session.query(Camera.id, Camera.online).filter(Camera.project_id == project_id).all():
        # 找出当前这个人的所有摄像头
        camera_id = camera[0]
        person_camera.append(camera_id)
        use_person_sync = db_session.query(PersonSync).filter(PersonSync.camera_id == camera_id,
                                                              PersonSync.person_id == person_id).first()
        if camera[1] != 1 or use_person_sync.sync_status != 1:
            # 摄像头不在线, 或者未同步成功
            db_session.query(PersonResource).filter(PersonResource.person_id == person_id).update({
                "sync": 2
            })
            db_session.commit()
            return
        if not use_person_sync:
            return
        use_camera.append(camera_id)
    if len(person_camera) == len(use_camera):
        db_session.query(PersonResource).filter(PersonResource.person_id == person_id).update(
            {
                "status": 1,
                "sync": 1
            }
        )
        print(f"{person_id} synchronization succeeded")
        db_session.commit()


def create_face(data_info):
    print('create_face', data_info)
    person_sync = db_session.query(PersonSync).filter(PersonSync.id == data_info["cmd_id"]).first()
    if not person_sync:
        print("sync not find")
        return
    # 创建成功, 更新sync状态
    person_sync.sync_status = 1
    if data_info["code"] == 0:
        pass
    elif data_info["code"] == 402:
        # 人脸已经存在
        person_sync.sync_desc = data_info["reply"]
    else:
        # 创建失败
        person_sync.sync_status = 2
        person_sync.sync_desc = data_info["reply"]
    db_session.add(person_sync)
    db_session.commit()
    # 查询当前这个人是否同步完成了所有的摄像头
    is_synchronization(person_sync.person_id, person_sync.project_id)
    # person_camera = []
    # use_camera = []
    # for camera in db_session.query(Camera.id, Camera.online).filter(Camera.project_id == person_sync.project_id).all():
    #     # 找出当前这个人的所有摄像头
    #     camera_id = camera[0]
    #     person_camera.append(camera_id)
    #     use_person_sync = db_session.query(PersonSync).filter(PersonSync.camera_id == camera_id,
    #                                                           PersonSync.person_id == person_id).first()
    #     if camera[1] != 1:
    #         # 摄像头不在线
    #         db_session.query(PersonResource).filter(PersonResource.person_id == person_id).update({
    #             "sync": 2
    #         })
    #         db_session.commit()
    #         return
    #     if not use_person_sync:
    #         return
    #     if use_person_sync.sync_status != 1:
    #         return
    #     use_camera.append(camera_id)
    # if len(person_camera) == len(use_camera):
    #     db_session.query(PersonResource).filter(PersonResource.person_id == person_id).update(
    #         {
    #             "status": 1,
    #             "sync": 1
    #         }
    #     )
    #     print(f"{person_id} synchronization succeeded")
    #     db_session.commit()


def update_face(data_info):
    print(data_info)


def delete_face(data_info):
    print(data_info)


def all_user(data_info):
    print("all_user", data_info)
    body = data_info["body"]
    camera = db_session.query(Camera).filter(Camera.sn == data_info["sn"],
                                             Camera.project_id == data_info["cmd_id"]).first()
    if not body:
        # 当前相机找不到人
        if camera:
            db_session.query(PersonSync).filter(PersonSync.camera_id == camera.id,
                                                PersonSync.project_id == data_info["cmd_id"]).update(
                {
                    "sync_status": 3
                })
            db_session.commit()
        return

    now_camera_person = [i["per_id"] for i in body]
    db_session.query(PersonSync).filter(~PersonSync.person_id.in_(now_camera_person),
                                        PersonSync.camera_id == camera.id,
                                        PersonSync.project_id == data_info["cmd_id"]).update(
        {"sync_status": 3}
    )
    db_session.commit()


def search_picture_url(person_obj):
    attachment_id = person_obj.attachment_id
    if attachment_id:
        attachment = db_session.query(Attachment).filter(Attachment.id == attachment_id).first()
        if attachment:
            # 改成下发中
            person_obj.sync = 128
            db_session.add(person_obj)
            db_session.commit()
            return attachment.url
    return ''


def push_create_face(client, person_obj, picture_url, sn, sync_id):
    push_message = {
        "cmd": "create_face",
        "per_id": person_obj.person_id,
        "face_id": person_obj.person_id,
        "per_name": person_obj.name,
        "img_url": picture_url,
        "client_id": sn,
        "version": "0.2",
        "cmd_id": sync_id  # sync 的ID
    }
    client.publish(f"face/{sn}/request", payload=json.dumps(push_message))


def push_update_face(client, person_obj, picture_url, sn, sync_id):
    push_message = {
        "cmd": "update_face",
        "per_id": person_obj.person_id,
        "face_id": person_obj.person_id,
        "per_name": person_obj.name,
        "img_url": picture_url,
        "client_id": sn,
        "version": "0.2",
        "cmd_id": sync_id  # sync 的ID
    }
    client.publish(f"face/{sn}/request", payload=json.dumps(push_message))


def create_face_task(client, person_obj, sn, camera_id):
    # 新建同步
    picture_url = search_picture_url(person_obj)
    if picture_url:
        person_sync = db_session.query(PersonSync).filter(PersonSync.camera_id == camera_id,
                                                          PersonSync.project_id == person_obj.project_id,
                                                          PersonSync.person_id == person_obj.person_id).first()
        if not person_sync:
            person_sync = PersonSync(
                project_id=person_obj.project_id,
                camera_id=camera_id,
                sync_status=128,
                person_id=person_obj.person_id,
                attachment_id=person_obj.attachment_id
                                     )
        else:
            person_sync.attachment_id = person_obj.attachment_id
            person_sync.sync_status = 128
        db_session.add(person_sync)
        db_session.commit()
        # 下发新建任务
        push_create_face(client, person_obj, picture_url, sn, person_sync.id)


def create_face_sync(client, person_obj, sn, camera_id):
    # 正在同步中
    is_same, sync_status = comparison_picture(person_obj, camera_id)
    if is_same:
        # 照片一样，不修改
        if sync_status != 1:
            # 状态不等于1就重新同步
            create_face_task(client, person_obj, sn, camera_id)
        else:
            # 照片不一样就更新所有, 且更新完成后 person resource 的 status 为 0
            camera = db_session.query(Camera).filter(Camera.id == camera_id).first()
            # create_face_task(client, person_obj, sn, camera.id)
    else:
        # 找不到任务就新建一个任务
        create_face_task(client, person_obj, sn, camera_id)


def update_face_task(client, person_obj, sn, camera_id):
    is_same, sync_status = comparison_picture(person_obj, camera_id)



def update_face_sync(client, person_obj, sn, camera_id):
    pass


def comparison_picture(person_obj, camera_id):
    # 对比照片是否一样，不一样就更新
    picture_url = search_picture_url(person_obj)
    # 查看历史照片和当前照片一样吗
    exist_sync = db_session.query(PersonSync).filter(
        PersonSync.camera_id == camera_id,
        PersonSync.person_id == person_obj.person_id,
        PersonSync.project_id == person_obj.project_id
    ).first()
    if exist_sync:
        if picture_url == search_picture_url(exist_sync):
            return True, exist_sync.sync_status
    return False, 0


def face_search(client, data_info):
    # 查找设备是否在线
    # camera = db_session.query(Camera).filter(Camera.sn == data_info["sn"],
    #                                          Camera.project_id == data_info["cmd_id"]).first()
    # if camera:
    for camera in db_session.query(Camera).filter(Camera.sn == data_info["sn"],
                                                  Camera.project_id == data_info["cmd_id"]).all():
        camera.online = 1
        db_session.add(camera)
        db_session.commit()
        # 查看当前摄像头下面的人，默认所有人都要下发
        person_resource_all = db_session.query(PersonResource).filter(PersonResource.project_id == camera.project_id)
        # 检测设备中的所有人
        client.publish(f'face/{data_info["sn"]}/request', json.dumps({
            "version": "0.2",
            "client_id": data_info["sn"],
            "cmd": "get_person_info",
            "cmd_id": camera.project_id
        }))
        for person_resource in person_resource_all:
            if person_resource.status == 0 and person_resource.sync == 0:
                # 人员未操作, 且暂未同步 查询下发照片
                create_face_task(client, person_resource, camera.sn, camera.id)
            elif person_resource.status == 0 and person_resource.sync == 128:
                # 人员未操作，且正在同步
                create_face_sync(client, person_resource, camera.sn, camera.id)
            elif person_resource.status == 1 and person_resource.sync == 1:
                # 人员已经同步，查看照片是否一样， 不一样就更新
                update_face_task(client, person_resource, camera.sn, camera.id)
            elif person_resource.status == 1 and person_resource.sync == 128:
                # 人员已经同步, 且在更新照片
                update_face_sync(client, person_resource, camera.sn, camera.id)

        # 检测是否成功
        # client.publish(f'face/{data_info["sn"]}/request', json.dumps({
        #     "version": "0.2",
        #     "client_id": data_info["sn"],
        #     "cmd": "get_person_info"
        # }))

    # db_session.add(camera)
    # db_session.commit()


def main():
    camera_sn_list = db_session.query(Camera.sn, Camera.project_id).all()
    business = ConnectBase(on_message=on_message, on_connect=on_connect, on_disconnect=on_disconnect)
    # 监听设备
    business.mqtt_client.subscribe([(f"face/{client_sn[0]}/response", 0) for client_sn in camera_sn_list])

    for camera_sn in camera_sn_list:
        topic = "face/request"
        push_message = {
            'version': '0.2',
            'cmd': 'face_search',
            'client_id': camera_sn[0],
            'cmd_id': camera_sn[1]
        }
        # 查看设备是否在线
        business.mqtt_client.publish(topic, payload=json.dumps(push_message), qos=0)

    while True:
        pass


# def search_device():
#     camera_sn_list = db_session.query(Camera.sn).all()
#     business = Business(on_message=on_message, on_connect=on_connect, on_disconnect=on_disconnect)
#     # 监听设备
#     business.add_listen([(f"face/{client_sn[0]}/response", 0) for client_sn in camera_sn_list])
#     for camera_sn in camera_sn_list:
#         # business.topic = f"face/{camera_sn[0]}/request"
#         business.topic = f"face/request"
#         business.custom_com(camera_sn[0], "face_search")
#
#     while True:
#         pass


if __name__ == '__main__':
    main()
