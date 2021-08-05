# -*- coding: utf-8 -*-
# Author : hejianxin
# Time : 2021/7/12 10:19 上午
from logger.logger import logger
import json
from models.models import db_session, Camera, MqttTask, Attachment
from sqlalchemy import or_
from conf.config import Config
from util.connecnt import ConnectBase
from io import BytesIO
from PIL import Image
import os
import uuid
import datetime
import time
import requests


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("business Connect success")
    else:
        logger.warn(f"Connect failed result code {str(rc)}")


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
        logger.warn(json_message)
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


def publish_scheduler(task_id):
    # 定时更新任务状态
    run_date = datetime.datetime.now() + datetime.timedelta(hours=2)
    # run_date = datetime.datetime.now() + datetime.timedelta(seconds=60)

    json_data = {
        "id": str(uuid.uuid4()),
        "func": "scheduler:check_task",
        "trigger": "date",
        "run_date": run_date.strftime("%Y-%m-%d %H:%M:%S"),
        "kwargs": {"task_id": task_id}
    }
    res = requests.post(f"http://{Config.SCHEDULER_HOST}:{Config.SCHEDULER_PORT}/scheduler/jobs", json=json_data)
    logger.info(f"scheduler publish success {res.content}")


def update_task(task_id, task_status, picture_status, **kwargs):
    # 成功后更新任务的状态
    task = db_session.query(MqttTask).filter(MqttTask.id == int(task_id)).first()
    task.task_status = task_status
    task.picture_status = picture_status
    for key, value in kwargs.items():
        setattr(task, key, value)
    db_session.add(task)
    db_session.commit()


def on_disconnect(client, userdata, rc):
    if rc == 0:
        logger.info("success disconnect")
    if rc != 0:
        logger.info("Unexpected disconnection %s" % rc)


def create_face(data_item):
    mqtt_task_id = data_item["cmd_id"]
    code = data_item["code"]
    if code == 0:
        update_task(mqtt_task_id, 1, 1)
        logger.info(f"create face success {data_item}")
    else:
        update_task(mqtt_task_id, 2, 1, operate_code=code, operate_remark=data_item["reply"])
        logger.error(f"create face failed {data_item}")


def update_face(data_item):
    mqtt_task_id = data_item["cmd_id"]
    code = data_item["code"]
    if code == 0:
        update_task(mqtt_task_id, 1, 2)
        logger.info(f"update face success {data_item}")
    else:
        update_task(mqtt_task_id, 2, 2, operate_code=code, operate_remark=data_item["reply"])
        logger.error(f"update face failed {data_item}")


def delete_face(data_item):
    # print(data_item)
    pass


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
    camera_obj = db_session.query(Camera).filter(Camera.device_no == device_no,
                                                 Camera.status == 1).first()
    if not camera_obj:
        logger.error("not find camera")
        return
    for task in db_session.query(MqttTask).filter(MqttTask.camera_id == camera_obj.resource_id,
                                                  MqttTask.project_id == project_id,
                                                  MqttTask.task_status == 0,
                                                  # or_(MqttTask.task_status == 0, MqttTask.task_status == 2),
                                                    ):
        attachment = db_session.query(Attachment.path).filter(Attachment.id == task.attachment_id).first()
        if not attachment:
            logger.warn("not find person picture")
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
            "client_id": camera_obj.device_no,
            "version": "0.2",
            "cmd_id": str(task.id)
        }
        print(push_message)
        client.publish(f"face/{camera_obj.device_no}/request", json.dumps(push_message))
        publish_scheduler(task.id)


class Connect(ConnectBase):
    DEFAULT_CALLBACK = {
        "on_connect": on_connect,
        "on_disconnect": on_disconnect,
        "on_message": on_message
    }


listen_camera_sn = []

if not os.path.exists(Config.REMOTE_FILE_DIR_PREFIX):
    os.makedirs(Config.REMOTE_FILE_DIR_PREFIX)

business = Connect(mqtt_host=Config.MQTT_HOST,
                   mqtt_port=Config.MQTT_PORT,
                   mqtt_username=Config.MQTT_USERNAME,
                   mqtt_password=Config.MQTT_PASSWORD)

while True:
    project_id_list = db_session.query(Camera.project_id).filter(Camera.status == 1).group_by(Camera.project_id)
    for project_id in project_id_list:
        camera_sn_list = db_session.query(Camera.device_no,
                                          Camera.project_id).filter(Camera.project_id == project_id[0],
                                                                    Camera.status == 1)
        for camera_sn_query in camera_sn_list:
            sn = camera_sn_query[0]
            project_id = camera_sn_query[1]
            if sn not in listen_camera_sn:
                listen_camera_sn.append(sn)
                # 监听设备
                business.mqtt_client.subscribe(f"face/{sn}/response", 0)

            topic = f"face/{sn}/request"

            for i in db_session.query(MqttTask).all():
                delete = {
                    "client_id": sn,
                    "version": "0.2",
                    "cmd": "delete_face",
                    "type": 0,
                    "per_id": i.delete_horizontal()
                }
                i.task_status = 0
                db_session.add(i)
                db_session.commit()
                business.mqtt_client.publish(topic, payload=json.dumps(delete))

            push_message = {
                'version': '0.2',
                'cmd': 'face_search',
                'client_id': sn,
                'cmd_id': project_id
            }
            # 查看设备是否在线
            business.mqtt_client.publish(topic, payload=json.dumps(push_message), qos=0)

        time.sleep(60)
