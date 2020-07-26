import time
from datetime import datetime
import os
import threading
import json
from cxyx import CXYX
from cxyx.core.config import Config

Config.MYSQL_URL = "sqlite:///test.db?check_same_thread=False"
from cxyx.core.add_feature import do_sth_before_task, do_sth_after_task, \
    do_sth_success_task, do_sth_fail_task
from cxyx.utils.redis_engine import RedisEngine

from cxyx_monitor.utils.timemk import trans2mk

from cxyx_monitor.core import TIME_FORMATTER
from cxyx_monitor.core.table import Parse


def get_info_now(task):
    tpid = threading.current_thread().ident
    pid = os.getpid()
    time_now = datetime.now().strftime(TIME_FORMATTER)
    return json.dumps({
        "function_name": task["func_name"],
        "args":          task["args"],
        "kwargs":        task["kwargs"],
        "task_id":       task["id_"],
        "tpid":          tpid,
        "pid":           pid,
        "time_now":      time_now,
    })


def do_before_task(self, real_func, task):
    self._broker.broker_engine.lpush(
        Config.task_before_key(), get_info_now(task)
    )
    # print(self._broker.broker_engine.lpop(
    #     Config.task_before_key()
    # ))
    do_sth_before_task(real_func, args=task["args"],
                       kwargs=task["kwargs"])


def do_after_task(self, real_func, task):
    self._broker.broker_engine.lpush(
        Config.task_after_key(), get_info_now(task)
    )
    do_sth_after_task(real_func, args=task["args"],
                      kwargs=task["kwargs"])


def success_task(self, real_func, task):
    self._broker.broker_engine.lpush(
        Config.task_success_key(), get_info_now(task)
    )
    do_sth_success_task(real_func, args=task["args"],
                        kwargs=task["kwargs"])


def fail_task(self, real_func, task):
    self._broker.broker_engine.lpush(
        Config.task_fail_key(), get_info_now(task)
    )
    do_sth_fail_task(real_func, args=task["args"],
                     kwargs=task["kwargs"])


def task_before_key(cls):
    return cls.BROKER_QUEUE_KEY + "before_key"


def task_after_key(cls):
    return cls.BROKER_QUEUE_KEY + "after_key"


def task_success_key(cls):
    return cls.BROKER_QUEUE_KEY + "success_key"


def task_fail_key(cls):
    return cls.BROKER_QUEUE_KEY + "fail_key"


def save_info_to_mysql(key, info, parse):
    info = json.loads(info)
    if parse.get_count(task_id=info.get("task_id")) > 0:
        parse.update(task_id=info.get("task_id"), update_dict={
            "%s_time" % key: trans2mk(info["time_now"]),
        })
    else:
        parse.insert(key=key, insert_dict=info)


def move_info_redis_to_mysql(self):
    self._init_broker_backend()

    def move():
        parse = Parse()
        count = 0
        while True:
            count += 1
            has_data = False
            for key in ["before", "success", "fail", "after"]:
                info = self._broker.broker_engine.lpop(
                    getattr(Config, "task_%s_key" % key)()
                )
                if info:
                    if count > 50:
                        del parse
                        parse = Parse()
                        count = 0
                    has_data = True
                    save_info_to_mysql(key, info, parse)
            if not has_data:
                time.sleep(5)

    thread = threading.Thread(target=move)
    thread.start()


def show_len(self, key):
    return self.redis_eng.llen(key)


def cxyx_show_len(self):
    return self._broker.broker_engine.show_len(Config.BROKER_QUEUE_KEY)


def patch_all():
    setattr(CXYX, "do_before_task", do_before_task)
    setattr(CXYX, "do_after_task", do_after_task)
    setattr(CXYX, "success_task", success_task)
    setattr(CXYX, "fail_task", fail_task)
    setattr(CXYX, "move_data", move_info_redis_to_mysql)

    setattr(Config, "task_fail_key", classmethod(task_fail_key))
    setattr(Config, "task_success_key", classmethod(task_success_key))
    setattr(Config, "task_after_key", classmethod(task_after_key))
    setattr(Config, "task_before_key", classmethod(task_before_key))

    setattr(RedisEngine, "show_len", show_len)
    setattr(CXYX, "show_len", cxyx_show_len)
