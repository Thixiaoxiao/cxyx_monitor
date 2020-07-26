# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         table
# Description:  
# Author:       Chenxiyuxiao
# Date:         2020/7/20
# -------------------------------------------------------------------------------
import time
import traceback
from cxyx_monitor.utils.timemk import trans2mk
from sqlalchemy import Column, String, Integer, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from cxyx_monitor.core.base import Base

Basedb = declarative_base()


def retry(count=3):
    def outer(func):
        def inner(*args, **kwargs):
            result = None
            for _ in range(count):
                try:
                    result = func(*args, **kwargs)
                    break
                except:
                    time.sleep(0.5)
                    traceback.print_exc()
            return result

        return inner

    return outer


class Task(Basedb):
    __tablename__ = "task_info"
    id = Column(Integer, primary_key=True)
    task_id = Column(String(64), nullable=False, unique=True)
    funcname = Column(String(64), nullable=False, unique=False)
    task_tpid = Column(Integer, nullable=False, index=True)
    task_pid = Column(Integer, nullable=False, index=True)

    success_time = Column(Integer, nullable=True, index=True)
    before_time = Column(Integer, nullable=True, index=True)
    after_time = Column(Integer, nullable=True, index=True)
    fail_time = Column(Integer, nullable=True, index=True)

    def __repr__(self):
        return '-'.join([
            str(self.task_id),
            str(self.after_time),
            str(self.task_pid),
            str(self.before_time),
            str(self.fail_time),
        ])


def create_table():
    Basedb.metadata.create_all(Base.get_engine())


class Parse:
    def __init__(self):
        obj_session = sessionmaker(Base.get_engine())
        self.db_session = obj_session()

    def init(self):
        self.close()
        obj_session = sessionmaker(Base.get_engine())
        self.db_session = obj_session()

    def show_count(self, key, st=1, et=int(time.time())):
        try:
            attr = getattr(Task, "%s_time" % key)
            return self.db_session.query(attr).filter(
                attr > st, attr <= et
            ).count()
        except:
            self.init()
            attr = getattr(Task, "%s_time" % key)
            return self.db_session.query(attr).filter(
                attr > st, attr <= et
            ).count()

    @retry(3)
    def get_count(self, task_id):
        try:
            return self.db_session.query(Task).filter(
                Task.task_id == task_id).count()
        except:
            self.init()
            return self.db_session.query(Task).filter(
                Task.task_id == task_id).count()

    @retry(3)
    def update(self, task_id, update_dict):
        try:
            self.db_session.query(Task).filter(Task.task_id == task_id).update(
                update_dict)
            self.db_session.commit()
        except:
            self.init()
            self.db_session.query(Task).filter(Task.task_id == task_id).update(
                update_dict)
            self.db_session.commit()

    @retry(3)
    def insert(self, key, insert_dict):
        obj = Task(**{
            "task_id":       insert_dict["task_id"],
            "task_tpid":     insert_dict["tpid"],
            "task_pid":      insert_dict["pid"],
            "funcname":      insert_dict["function_name"],
            "%s_time" % key: trans2mk(insert_dict["time_now"]),

        })
        try:
            self.db_session.add(obj)
            self.db_session.commit()
        except:
            self.init()
            self.db_session.add(obj)
            self.db_session.commit()

    def show_all(self):
        for obj in self.db_session.query(Task).all():
            yield obj

    def __del__(self):
        self.close()

    def close(self):
        try:
            self.db_session.close()
        except:
            pass

    def get_desc_obj(self, count):
        for obj in self.db_session.query(Task).order_by(desc(Task.id)).limit(
                count):
            yield obj
