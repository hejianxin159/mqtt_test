# -*- coding: utf-8 -*-
# Author : hejianxin
# Time : 2021/7/15 5:00 下午
import datetime
import uuid
from models.models import Attachment, db_session
import os
import base64
from PIL import Image
from io import BytesIO


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath('__file__')))
DATA_DIR = os.path.join(BASE_DIR, "/opt/rc-app/api/data/")
PROJECT_DIR = os.path.dirname(os.path.abspath('__file__'))
PROJECT_STORAGE_ROOT = os.path.join(DATA_DIR, 'project')


def format_time(_time, format_str):
    """ format time """
    return _time.strftime(format_str)


def format_time_ym(_time=None):
    """ return current time in format yyyy-MM """
    format_str = '%Y-%m'
    if _time is None:
        return format_time(datetime.datetime.now(), format_str)
    return format_time(_time, format_str)


def upload_base64_image(project_id, image_name, image_modul, image_data_base64):
    byte_data = base64.b64decode(image_data_base64)
    image_data2 = BytesIO(byte_data)
    img = Image.open(image_data2)
    upload_info = {
        'image': True,
        'is_netdisk': False,
        'modul': image_modul,
        'netdisk_parent_id': '',
        'w': img.size[0],
        'h': img.size[1],
        'size': img.size[0] * img.size[1],
        'src': str(b'data:image/.;base64,' + image_data_base64),
        "base_data": image_data_base64,
        'title': image_name + '.' + img.format,
        'waterprint': True
    }
    return handle_single_upload(project_id, None, upload_info)


def handle_single_upload(project_id, user_id, image):
    modul = image.get('modul', '')
    is_waterprint = image.get('waterprint', False)
    is_netdisk = image.get('is_netdisk', False)
    ym = format_time_ym(datetime.datetime.now())

    # 组织文件信息
    fileinfo = Attachment(is_dir=False, is_root=False, project_id=project_id, creator_id=user_id)
    fileinfo.id = uuid.uuid4()
    fileinfo.is_img = image.get('image', '')
    fileinfo.size = image.get('size', 0)
    fileinfo.pixel_w = image.get('w', 0)
    fileinfo.pixel_h = image.get('h', 0)
    fileinfo.name = image.get('title', '')
    fileinfo.file_type = fileinfo.name.split('.')[-1]
    uuid_file_name = '.'.join([str(fileinfo.id), fileinfo.file_type])
    fileinfo.path = os.path.join(project_id, ym, uuid_file_name)
    if not os.path.exists(PROJECT_STORAGE_ROOT + '/' + os.path.dirname(fileinfo.path)):
        os.makedirs(PROJECT_STORAGE_ROOT + '/' + os.path.dirname(fileinfo.path))

    file_path = os.path.join(PROJECT_STORAGE_ROOT, fileinfo.path)

    with open(file_path, 'wb') as f:
        f.write(base64.b64decode(image["base_data"]))

    db_session.add(fileinfo)
    db_session.commit()
    return fileinfo.path
    # path = project_id + ym+ file_id + file_type
    # ab_path = PROJECT_STORAGE_ROOT + path
    # if fileinfo.is_img == 1 and fileinfo.pixel_w == 0 and fileinfo.pixel_h == 0:
    # file_path = os.path.join(PROJECT_STORAGE_ROOT, fileinfo.path)
    # open_image = Image.open(file_path)
    # fileinfo.pixel_w = open_image.size[0]
    # fileinfo.pixel_h = open_image.size[1]
    # db_session.add(fileinfo)
    # db_session.commit()
    # return fileinfo.path
