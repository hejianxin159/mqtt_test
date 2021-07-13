# -*- coding: utf-8 -*-
# Author : hejianxin
# Time : 2021/6/17 5:37 下午
import datetime
from conf.config import Config
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, SmallInteger, DateTime, func, Boolean
from sqlalchemy.orm import sessionmaker
import uuid
engine = create_engine(
    f"mysql+pymysql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.RESOURCE_DB_NAME}")
db_session = sessionmaker(bind=engine)
db_session = db_session()

callback_session = sessionmaker(bind=engine)
callback_session = callback_session()
Base = declarative_base()


def gen_id():
    return uuid.uuid4().hex


class Camera(Base):
    """相机"""
    __tablename__ = "camera_camera"

    id = Column(Integer, autoincrement=True, primary_key=True)
    resource_id = Column(String(36), default=gen_id)
    project_id = Column(String(36), nullable=True)
    name = Column(String(50), nullable=True)    # 设备名称
    device_no = Column(String(40), nullable=True)  # 设备编号（关联具体设备）
    camera_status = Column(SmallInteger)  # 0:未启用、1：启用、2：初始启用、待完全同步
    type = Column(SmallInteger, default=0)  # 0 施工区 1 办公区
    online = Column(SmallInteger, default=0)  # 0离线 1在线
    direction = Column(String(10), nullable=True)  # 业务数据 (IN：进场、OUT：出场)
    status = Column(SmallInteger, default=1)
    created_time = Column(DateTime, default=datetime.datetime.now)
    modified_time = Column(DateTime, default=datetime.datetime.now)


class PersonResource(Base):
    # person sync中如果两条sync_status 都是1就同步成功了
    # 如果只有一条就是同步失败
    # 下发图片的时候是同步中，如果超过某个时间就代表同步失败
    __tablename__ = "camera_personresource"

    id = Column(String(32), default=gen_id, primary_key=True)
    project_id = Column(String(32), nullable=True)

    business_id = Column(String(50), nullable=True)     # 业务编号
    person_id = Column(String(18), nullable=True)       # 人员代码编号（18位：T+TIME+RANDOM)
    name = Column(String(18), nullable=True)            # 人员姓名
    type = Column(String(18), nullable=True)            # 数据类型（LABOUR：劳务、STAFF：系统用户、VISITOR：临时用户）
    status = Column(SmallInteger, default=0)            # 数据状态（1：add、2：update、3：del)
    sync = Column(SmallInteger, default=0)              # 同步状态（0：待同步、1：成功同步(任务下发成功) 2：同步失败 128:同步中）
    sync_desc = Column(String(400), nullable=True)
    attachment_id = Column(String(32), nullable=True)                 # 图片
    from_date = Column(DateTime, server_default=func.now())
    update_date = Column(DateTime, server_default=func.now(), onupdate=func.now())


class PersonSync(Base):
    # 一个人员对应两条数据，如果只有一条或者没有代表同步失败，
    # 两条数据的sync_status 都是1的时候，图片同步成功
    __tablename__ = "camera_personsync"

    id = Column(String(32), default=gen_id, primary_key=True)
    project_id = Column(String(32), nullable=True)
    type = Column(String(18), nullable=True)            # 数据类型（LABOUR：劳务、STAFF：系统用户、TEMP：临时用户）
    business_id = Column(String(50), nullable=True)     # 业务编号
    person_id = Column(String(18), nullable=True)       # 人员代码编号（18位：T+TIME+RANDOM)
    camera_id = Column(String(32), nullable=True)       # 下发的相机
    sync_status = Column(SmallInteger, default=0)       # 操作状态 0: 未操作; 1: 操作成功; 2: 操作失败 3:照片被删除 128:同步中
    sync_desc = Column(String(400), nullable=True)
    attachment_id = Column(String(32), nullable=True)                 # 图片
    from_date = Column(DateTime, server_default=func.now())
    update_date = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Attachment(Base):
    __tablename__ = "attachment"

    id = Column(String(32), default=gen_id, primary_key=True)
    project_id = Column(String(32), nullable=True)

    top_parent_id = Column(String(32), nullable=True)  # 顶级父ID (顶级目录的top_parent_id为None)
    parent_id = Column(String(32), nullable=True)  # 直接父级ID (顶级目录的parent_id为None)
    creator_id = Column(String(32), nullable=True)  # 创建人ID
    name = Column(String(300), nullable=False, default='')  # 文件或目录名称
    path = Column(String(500), nullable=True)  # 文件或目录在磁盘上的路径(目录原则上没有path，即根目录)

    is_root = Column(Boolean, default=True)  # 是否是顶级目录(参与权限控制) 不需要是否可以删除的字段,顶级目录不可删除
    is_dir = Column(Boolean, default=False)  # 是否为文件夹(True: 文件夹; False: 文件)
    is_img = Column(Boolean, default=False)  # 是否为图片(True: 文件夹; False: 文件)
    file_type = Column(String(20), nullable=False, default='')  # 文件类型
    size = Column(String(20), nullable=False, default='')  # 文件大小
    pixel_w = Column(Integer, nullable=False, default=0)  # 像素(px), 宽
    pixel_h = Column(Integer, nullable=False, default=0)  # 像素(px), 高
    from_date = Column(DateTime, server_default=func.now())
    update_date = Column(DateTime, server_default=func.now(), onupdate=func.now())
    url = Column(String(300), nullable=False, default='')  # 备注
    remark = Column(String(300), nullable=False, default='')  # 备注


class MqttTask(Base):
    __tablename__ = "mqtt_task"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String(36), nullable=True)
    person_resource = Column(String(36))                # 关联花名册人
    person_type = Column(SmallInteger, default=0)       # 0 roster 1 staff
    person_name = Column(String(32), nullable=True)     # 人员名字
    attachment_id = Column(String(36), nullable=True)   # 图片的id
    camera_sn = Column(String(36), nullable=True)       # 相机的sn
    task_status = Column(SmallInteger, default=0)       # 0未操作 1 成功 2 失败 3 操作中
    picture_status = Column(SmallInteger, default=0)    # 0 未操作 1 新增 2 更新
    status = Column(SmallInteger, default=1)            # 数据状态
    create_time = Column(DateTime, default=datetime.datetime.now)   # 创建时间

    def format_person_resource(self):
        return self.person_resource.replace('-', '')

    def delete_horizontal(self):
        return self.person_resource.replace('-', '')


if __name__ == '__main__':
    # MqttTask.__table__.drop(engine)
    # MqttTask.__table__.create(engine)
    # Camera.__table__.drop(engine)
    # Camera.__table__.create(engine)
    # PersonResource.__table__.drop(engine)
    # PersonResource.__table__.create(engine)
    # PersonSync.__table__.drop(engine)
    # PersonSync.__table__.create(engine)
    # Attachment.__table__.drop(engine)
    # Attachment.__table__.create(engine)
    # #
    project_id = 'ecabe97c-84ae-480a-baaa-59970617873e'
    # camera1 = Camera(name='test01', device_no="75b994c0-578b65a4", camera_status=0, online=0, direction="IN", project_id=project_id)
    # camera2 = Camera(name='test02', device_no="b1da57e8-7fb982c4", camera_status=0, online=0, direction="OUT", project_id=project_id)
    # db_session.add(camera1)
    # db_session.add(camera2)
    person_resource = 'd0dd27b7-fe5f-41c5-9179-2e71d8b0d7e1'
    attachment_id = '00948613-12b1-4d2b-ac46-fe1950b3b629'
    task1 = MqttTask(project_id=project_id, person_resource=person_resource, person_name='贺建鑫',
                     attachment_id=attachment_id, camera_sn='b1da57e8-7fb982c4')
    task2 = MqttTask(project_id=project_id, person_resource=person_resource, person_name='贺建鑫',
                     attachment_id=attachment_id, camera_sn='b1da57e8-7fb982c4')
    db_session.add(task1)
    db_session.add(task2)
    db_session.commit()

    #
    # picture1 = Attachment(name="hejx", url="http://10.28.25.213:8080/IMG_1227.jpeg", project_id=project_id)
    # # picture2 = Attachment(name="hejx", url="http://10.28.25.213:8080/IMG_1227.JPG", project_id=project_id)
    # # picture3 = Attachment(name="hejx", url="http://10.28.25.213:8080/IMG_2559.jpeg", project_id=project_id)
    # picture4 = Attachment(name="hejx", url="http://10.28.25.213:8080/IMG_2560.jpeg", project_id=project_id)
    # db_session.add(picture1)
    # # db_session.add(picture2)
    # # db_session.add(picture3)
    # db_session.add(picture4)
    # db_session.commit()
    # person1 = PersonResource(person_id="hejx", name="hejx", project_id=project_id, attachment_id=picture1.id)
    # # person2 = PersonResource(person_id="hejx2", name="hejx2", project_id=project_id, attachment_id=picture2.id)
    # # person2 = PersonResource(person_id="hejx2", name="hejx", project_id=project_id)
    # db_session.add(person1)
    # # db_session.add(person2)
    # db_session.commit()




