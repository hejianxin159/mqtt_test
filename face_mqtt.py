# -*- coding: utf-8 -*-
# Author : hejianxin
# Time : 2021/7/12 10:19 上午
from logger.logger import logger
import paho.mqtt.client as mqtt
import json
from models.models import db_session, Camera, MqttTask, Attachment
from sqlalchemy import or_
from conf.config import Config
from io import BytesIO
from PIL import Image
import os


mqtt_host = "10.28.25.213"
mqtt_port = 1883
mqtt_username = "netmon"
mqtt_password = "netmon"


def connect(host, port, username, password):
    mqtt_client = mqtt.Client()
    if all([username, password]):
        mqtt_client.username_pw_set("netmon", "netmon")
    mqtt_client.connect(host=host, port=port)
    return mqtt_client


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("business Connect success")
    else:
        print(f"Connect failed result code {str(rc)}")


def on_message(client, userdata, msg):
    message = str(msg.payload, encoding="utf-8")
    message = message.replace("\n", "").replace("\x00", "")
    json_message = json.loads(message)
    if json_message["cmd"] == "create_face":
        create_face(json_message)
    elif json_message["cmd"] == "update_face":
        update_face(json_message)
    elif json_message["cmd"] == "delete_face":
        delete_face(json_message)
    elif json_message["cmd"] == "face_search":
        face_search(client, json_message)
    else:
        print("not func")
        print(json_message)
    # 关闭连接
    # client.disconnect()
    # client.loop_stop()


def transformation_image(photo_path):
    photo_image = Image.open(photo_path)
    photo_image = photo_image.convert("RGB")  # 将图片强制改成jpg
    width, height = 480, 620
    new_photo_image = photo_image.resize((width, height), Image.ANTIALIAS)
    out_buf = BytesIO()
    new_photo_image.save(out_buf, format='JPEG')
    file, ext = os.path.splitext(photo_path)
    filename = os.path.split(file)[1] + '.jpeg'
    save_path = os.path.join(Config.REMOTE_FILE_DIR_PREFIX, filename)
    with open(save_path, 'wb') as f:
        f.write(out_buf.getvalue())
    return filename


def on_disconnect(client, userdata, rc):
    if rc == 0:
        logger.info("success disconnect")
    if rc != 0:
        logger.info("Unexpected disconnection %s" % rc)


def update_task(task_id, picture_status):
    task = db_session.query(MqttTask).filter(MqttTask.id == int(task_id)).first()
    task.task_status = 1
    task.picture_status = picture_status
    db_session.add(task)
    db_session.commit()


def create_face(data_item):
    if data_item["code"] != 0:
        return
    mqtt_task_id = data_item["cmd_id"]
    update_task(mqtt_task_id, 1)
    logger.info(f"create face success {data_item}")


def update_face(data_item):
    if data_item["code"] != 0:
        return
    mqtt_task_id = data_item["cmd_id"]
    update_task(mqtt_task_id, 2)
    logger.info(f"update face success {data_item}")


def delete_face(data_item):
    print(data_item)


def face_search(client, data_item):
    # 查找摄像头
    device_no = data_item["sn"]
    project_id = data_item["cmd_id"]
    camera = db_session.query(Camera).filter(Camera.device_no == device_no,
                                             Camera.project_id == project_id).first()
    # 修改摄像头状态
    camera.online = 1
    db_session.add(camera)
    db_session.commit()
    logger.info(f"search camera sn {device_no} project_id {project_id}")
    # 找出当前摄像头的任务并下发
    for task in db_session.query(MqttTask).filter(MqttTask.project_id == project_id,
                                                  MqttTask.camera_sn == device_no,
                                                  MqttTask.task_status == 0,
                                                  # or_(MqttTask.task_status == 0, MqttTask.task_status == 2),
                                                    ):
        attachment = db_session.query(Attachment.path).filter(Attachment.id == task.attachment_id).first()
        if not attachment:
            continue
        # 修改成下发中
        task.task_status = 3
        if task.picture_status == 0:
            # 如果是未操作就是新增
            task.picture_status = 1
        db_session.add(task)
        db_session.commit()
        # 修改分辨率
        path, filename = os.path.split(attachment.path)
        img_path = os.path.join(Config.SOURCE_FILE_DIR_PREFIX, filename)
        transformation_img_path = transformation_image(img_path)
        img_url = Config.IMAGE_PREFIX + transformation_img_path
        # img_url = 'http://10.28.25.213:8080/IMG_1227.jpeg'

        person_id = task.delete_horizontal()
        push_message = {
            "cmd": "update_face" if task.picture_status == 2 else "create_face",
            "per_id": person_id,
            "face_id": person_id,
            "per_name": task.person_name,
            "img_url": img_url,
            "client_id": task.camera_sn,
            "version": "0.2",
            "cmd_id": str(task.id)
        }
        client.publish(f"face/{task.camera_sn}/request", json.dumps(push_message))


class ConnectBase:
    DEFAULT_CALLBACK = {
        "on_connect": on_connect,
        "on_disconnect": on_disconnect,
        "on_message": on_message
    }

    def __init__(self, **kwargs):
        self.mqtt_client = connect(*[kwargs.get(i) for i in ("mqtt_host",
                                                             "mqtt_port",
                                                             "mqtt_username",
                                                             "mqtt_password")])
        # 绑定事件函数
        call_back_method = ("on_connect", "on_disconnect", "on_message")
        for call_back in call_back_method:
            if call_back in kwargs:
                setattr(self.mqtt_client, call_back, kwargs[call_back])
            else:
                setattr(self.mqtt_client, call_back, self.DEFAULT_CALLBACK[call_back])
        # 开启事件循环
        self.mqtt_client.loop_start()


listen_camera_sn = []

if not os.path.exists(Config.REMOTE_FILE_DIR_PREFIX):
    os.makedirs(Config.REMOTE_FILE_DIR_PREFIX)

business = ConnectBase(mqtt_host=mqtt_host,
                       mqtt_port=mqtt_port,
                       mqtt_username=mqtt_username,
                       mqtt_password=mqtt_password)


while True:
    camera_sn_list = db_session.query(Camera.device_no, Camera.project_id).all()
    for camera_sn_query in camera_sn_list:
        sn = camera_sn_query[0]
        project_id = camera_sn_query[1]
        if sn not in listen_camera_sn:
            listen_camera_sn.append(sn)
            # 监听设备
            business.mqtt_client.subscribe(f"face/{sn}/response", 0)

        topic = f"face/{sn}/request"
        #
        # for i in db_session.query(MqttTask).all():
        #     delete = {
        #         "client_id": sn,
        #         "version": "0.2",
        #         "cmd": "delete_face",
        #         "type": 0,
        #         "per_id": i.delete_horizontal()
        #     }
        #     i.task_status = 0
        #     db_session.add(i)
        #     db_session.commit()
        #     business.mqtt_client.publish(topic, payload=json.dumps(delete))
        # time.sleep(3)

        push_message = {
            'version': '0.2',
            'cmd': 'face_search',
            'client_id': sn,
            'cmd_id': project_id
        }
        # 查看设备是否在线
        business.mqtt_client.publish(topic, payload=json.dumps(push_message), qos=0)

    while True:
        pass

# print(update_image(Config.SOURCE_FILE_DIR_PREFIX + '/' + '00948613-12b1-4d2b-ac46-fe1950b3b629.JPEG'))
