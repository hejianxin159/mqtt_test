# -*- coding: utf-8 -*-
# Author : hejianxin
# Time : 2021/6/22 10:41 上午
import paho.mqtt.client as mqtt
import json
from models.models import db_session, Camera, PersonSync, PersonResource, Attachment
import datetime


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
        if camera[1] != 1 or not use_person_sync:
            # 摄像头不在线, 任务肯定创建失败
            db_session.query(PersonResource).filter(PersonResource.project_id == project_id,
                                                    PersonResource.person_id == person_id).update(
                {
                    "sync": 2,
                    "status": 1
                })

            db_session.commit()
            return

        if use_person_sync.sync_status == 2:
            db_session.query(PersonResource).filter(PersonResource.person_id == person_id).update({
                "sync": 2,
                "status": 1
            })
            db_session.commit()
            return
        if use_person_sync.sync_status == 1:
            use_camera.append(camera_id)
    if len(person_camera) == len(use_camera):
        db_session.query(PersonResource).filter(PersonResource.person_id == person_id).update(
            {
                "sync": 1,
                "status": 1
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
    # db_session.query(PersonResource).filter(PersonResource.person_id == person_sync.person_id,
    #                                         PersonResource.project_id == person_sync.project_id).update(
    #     {
    #         "status": 1     # 更新为新增状态
    #     }
    # )
    db_session.add(person_sync)
    db_session.commit()
    # 查询当前这个人是否同步完成了所有的摄像头
    is_synchronization(person_sync.person_id, person_sync.project_id)


def update_face(data_info):
    print('update face', data_info)
    person_sync = db_session.query(PersonSync).filter(PersonSync.id == data_info["cmd_id"]).first()
    person_resource = db_session.query(PersonResource).filter(
        PersonResource.person_id == person_sync.person_id,
        PersonResource.project_id == person_sync.project_id,
    ).first()
    person_resource.status = 2      # 更新为更新状态
    db_session.add(person_resource)
    db_session.commit()
    if data_info["code"] == 0:
        # update success
        person_sync.sync_status = 1
        db_session.commit()
        is_synchronization(person_sync.person_id, person_sync.project_id)
    else:
        person_sync.sync_status = 2
        person_sync.sync_desc = data_info["reply"]
        person_resource.sync = 2
        db_session.add(person_sync)
        db_session.commit()


def delete_face(data_info):
    print(data_info)


def all_user(data_info):
    # print("all_user", data_info)
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


def face_search(client, data_info):
    # 查找设备是否在线
    # camera = db_session.query(Camera).filter(Camera.sn == data_info["sn"],
    #                                          Camera.project_id == data_info["cmd_id"]).first()
    # if camera:
    for camera in db_session.query(Camera).filter(Camera.sn == data_info["sn"],
                                                  Camera.project_id == data_info["cmd_id"]).all():
        print(camera)
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
            print(person_resource)
            Collect(client, person_resource, camera.id)
        # 检测是否成功
        # client.publish(f'face/{data_info["sn"]}/request', json.dumps({
        #     "version": "0.2",
        #     "client_id": data_info["sn"],
        #     "cmd": "get_person_info"
        # }))

    # db_session.add(camera)
    # db_session.commit()


class Collect:
    def __init__(self, mqtt_client, person_obj, camera_id):
        self.mqtt_client = mqtt_client
        self.person_obj = person_obj
        camera = db_session.query(Camera).filter(Camera.id == camera_id).first()
        self.sn = camera.sn
        self.camera_id = camera_id
        if camera:
            if person_obj.status == 0 and person_obj.sync == 0:
                # 人员未操作, 且暂未同步 查询下发照片
                self.create_face_task()
            elif person_obj.status == 0 and person_obj.sync == 128:
                # 人员未操作，正在同步中
                self.create_face_sync()
            elif person_obj.status == 1 and person_obj.sync == 1:
                # 人员已经同步，查看照片是否一样， 不一样就更新
                self.update_face_task()
            elif person_obj.status == 1 and person_obj.sync == 128:
                # 人员已经同步, 且在更新照片
                self.update_face_sync()
            elif person_obj.status == 2 and person_obj.sync == 2:
                # 人员更新，同步失败
                pass
            elif person_obj.status == 2 and person_obj.sync == 1:
                # 人员更新完成，且同步成功
                self.update_face_task()

    def create_face_task(self):
        # 新建sync task 任务
        self.person_obj.sync = 128
        db_session.add(self.person_obj)
        db_session.commit()
        self.face_sync_task("add")

    def update_face_task(self):
        is_same, sync_status = self.comparison_picture(self.person_obj, self.camera_id)
        if not is_same and sync_status == 100:
            self.person_obj.sync = 128
            db_session.add(self.person_obj)
            db_session.commit()
            self.face_sync_task("update")

    def update_face_sync(self):
        pass

    def face_sync_task(self, action):
        # 新建或者更新sync
        picture_url = self.search_picture_url(self.person_obj.attachment_id)
        person_sync = db_session.query(PersonSync).filter(
                PersonSync.camera_id == self.camera_id,
                PersonSync.project_id == self.person_obj.project_id,
                PersonSync.person_id == self.person_obj.person_id).first()
        if picture_url:
            if not person_sync:
                person_sync = PersonSync(
                    project_id=self.person_obj.project_id,
                    camera_id=self.camera_id,
                    sync_status=128,
                    person_id=self.person_obj.person_id,
                    attachment_id=self.person_obj.attachment_id
                )
            else:
                person_sync.attachment_id = self.person_obj.attachment_id
                person_sync.sync_status = 128
            db_session.add(person_sync)
            db_session.commit()
            if action == "add":
                # 下发新建任务
                self.push_face_message(picture_url, person_sync.id, "add")
            elif action == "update":
                # 下发更新任务
                self.push_face_message(picture_url, person_sync.id, "update")
        else:
            self.person_obj.sync = 2
            self.person_obj.status = 2
            if person_sync:
                person_sync.attachment_id = self.person_obj.attachment_id
                person_sync.sync_status = 2
                person_sync.sync_desc = "not find attachment"
                db_session.add(person_sync)
            db_session.add(self.person_obj)
            db_session.commit()

    def create_again(self):
        for exist_task in db_session.query(PersonSync).filter(
                PersonSync.project_id == self.person_obj.project_id,
                PersonSync.camera_id == self.camera_id,
                PersonSync.person_id == self.person_obj.person_id,
                PersonSync.attachment_id != self.person_obj.attachment_id).all():
            print(exist_task)

    def create_face_sync(self):
        # 正在同步中
        is_same, sync_status = self.comparison_picture(self.person_obj, self.camera_id)
        if not is_same:
            if sync_status == 0:
                # 任务不存在, 新建一个任务
                self.create_face_task()
            elif sync_status == 100:
                # 任务存在且照片不一样
                # 找出之前的任务，重新下发任务
                self.create_again()

    def search_picture_url(self, attachment_id):
        if attachment_id:
            attachment = db_session.query(Attachment).filter(Attachment.id == attachment_id).first()
            if attachment:
                # 改成下发中
                return attachment.url
        return ''

    def comparison_picture(self, person_obj, camera_id):
        # 对比照片是否一样，不一样就更新
        picture_url = self.search_picture_url(self.person_obj.attachment_id)
        # 查看历史照片和当前照片一样吗
        exist_sync = db_session.query(PersonSync).filter(
            PersonSync.camera_id == camera_id,
            PersonSync.person_id == person_obj.person_id,
            PersonSync.project_id == person_obj.project_id
        ).first()
        if exist_sync:
            if picture_url == self.search_picture_url(exist_sync.attachment_id):
                return True, exist_sync.sync_status
            else:
                # 照片不同，做更新操作
                return False, 100
        return False, 0

    def push_face_message(self, picture_url, sync_id, action):
        push_message = {
            "cmd": "create_face" if action == "add" else "update_face",
            "per_id": self.person_obj.person_id,
            "face_id": self.person_obj.person_id,
            "per_name": self.person_obj.name,
            "img_url": picture_url,
            "client_id": self.sn,
            "version": "0.2",
            "cmd_id": sync_id  # sync 的ID
        }
        self.mqtt_client.publish(f"face/{self.sn}/request", payload=json.dumps(push_message))


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
        break
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
