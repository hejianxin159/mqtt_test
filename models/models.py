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
Base = declarative_base()


def gen_id():
    return uuid.uuid4().hex


class Camera(Base):
    """相机"""
    __tablename__ = "camera_camera"

    id = Column(String(32), default=gen_id, primary_key=True)
    project_id = Column(String(32), nullable=True)
    name = Column(String(50), nullable=True)    # 设备名称
    sn = Column(String(40), nullable=True)  # 设备编号（关联具体设备）
    status = Column(SmallInteger)  # 0:未启用、1：启用、2：初始启用、待完全同步

    online = Column(SmallInteger, default=0)  # 0离线 1在线
    direction = Column(String(10), nullable=True)  # 业务数据 (IN：进场、OUT：出场)
    single_dev = Column(SmallInteger, default=0)  # 0:多用设备、1:单一设备（10分钟间隔内，进出式打卡）
    supplier = Column(String(32), default=uuid.uuid4().hex, nullable=True)   #供应商
    author = Column(String(32), default=uuid.uuid4().hex, nullable=True)    #创建者

    from_date = Column(DateTime, default=datetime.datetime.now)
    update_date = Column(DateTime, server_default=func.now(), onupdate=func.now())


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


if __name__ == '__main__':
    Camera.__table__.drop(engine)
    Camera.__table__.create(engine)
    PersonResource.__table__.drop(engine)
    PersonResource.__table__.create(engine)
    PersonSync.__table__.drop(engine)
    PersonSync.__table__.create(engine)
    Attachment.__table__.drop(engine)
    Attachment.__table__.create(engine)

    project_id = 'a33b141fd48646a8a6cc1716d3fc108a'
    camera1 = Camera(name='test01', sn="75b994c0-578b65a4", status=0, online=0, direction="IN", project_id=project_id)
    camera2 = Camera(name='test02', sn="75b994c0-578b65a4", status=0, online=0, direction="OUT", project_id=project_id)
    camera3 = Camera(name='test02', sn="75b994c0-578b65a4", status=0, online=0, direction="OUT", project_id=project_id)
    camera4 = Camera(name='test02', sn="75b994c0-578b65a4", status=0, online=0, direction="OUT", project_id=project_id)
    db_session.add(camera1)
    db_session.add(camera2)
    db_session.add(camera3)
    db_session.add(camera4)

    picture1 = Attachment(name="hejx", url="http://10.28.25.213:8080/IMG_1227.jpeg", project_id=project_id)
    picture2 = Attachment(name="hejx", url="http://10.28.25.213:8080/IMG_2559.jpeg", project_id=project_id)
    picture3 = Attachment(name="hejx", url="http://10.28.25.213:8080/IMG_2560.jpeg", project_id=project_id)
    db_session.add(picture1)
    db_session.add(picture2)
    db_session.add(picture3)
    db_session.commit()
    person1 = PersonResource(person_id="hejx", name="hejx", project_id=project_id, attachment_id=picture1.id)
    # person2 = PersonResource(person_id="hejx2", name="hejx2", project_id=project_id, attachment_id=picture2.id)
    # person2 = PersonResource(person_id="hejx2", name="hejx", project_id=project_id)
    db_session.add(person1)
    # db_session.add(person2)
    db_session.commit()
