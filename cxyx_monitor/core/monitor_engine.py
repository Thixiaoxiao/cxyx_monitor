# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         monitor_engine
# Description:  
# Author:       Chenxiyuxiao
# Date:         2020/7/20
# -------------------------------------------------------------------------------
import datetime
import time

from cxyx_monitor.utils.timemk import trans2mk, trans2date

from cxyx_monitor.core import TIME_FORMATTER

import cxyx_monitor

from cxyx_monitor.core.base import Base

from cxyx_monitor.core.table import Parse
from flask import Flask, jsonify, request, render_template

oripath = cxyx_monitor.__file__
monitorapp = Flask(
    __name__,
    static_folder=oripath.replace("cxyx_monitor\__init__.py",
                                  r"front\static").replace(
        "cxyx_monitor/__init__.py", "front/static"),
    template_folder=oripath.replace("cxyx_monitor\__init__.py",
                                    r"front\templates").replace(
        "cxyx_monitor/__init__.py",
        r"front/templates")
)


@monitorapp.route("/hello")
def hello():
    return "hello!"


@monitorapp.route('/all')
def _all():
    parse = Parse()
    res = []
    for obj in parse.show_all():
        result = {
            "task_id": obj.task_id,
            "task_tpid": obj.task_tpid,
            "task_pid": obj.task_pid
        }
        res.append(result)

    return jsonify(res)


@monitorapp.route('/bar')
def bar():
    # 条形图 以日为单位 最近十天 的统计量
    time_now = datetime.datetime.now()
    time_now = datetime.datetime(year=time_now.year, month=time_now.month,
                                 day=time_now.day, hour=23, minute=59,
                                 second=59)
    time_before = time_now + datetime.timedelta(days=-10)
    time_now_stamp = trans2mk(time_now.strftime(TIME_FORMATTER))
    time_before_stamp = trans2mk(time_before.strftime(TIME_FORMATTER))
    x_array = list(range(time_before_stamp, time_now_stamp,
                         int((time_now_stamp - time_before_stamp) / 10)))
    parse = Parse()
    x_array.append(time_now_stamp)
    x_array = [(x_array[index], x_array[index + 1]) for index in
               range(len(x_array) - 1)]
    y_array = [parse.show_count("after", st=bf, et=ef) for bf, ef in x_array]
    x_array = [trans2date(item[1]) for item in x_array]
    x_array = ["%s月%s日" % (item.month, item.day) for item in x_array]
    y_max = max(y_array)
    name = "单位：个"
    if y_max > 10000:
        name = "单位：万"
        y_array = [item / 10000 for item in y_array]
        y_max = max(y_array)
    # TODO 需要设置 坐标显示 控制显示数量
    return jsonify({
        "dataAxis": x_array,
        "data": y_array,
        "yMax": y_max,
        "_name": name
    })


@monitorapp.route('/zhe')
def zhe():
    # 最近十二小时内的 每两小时成功与失败的折线图
    time_now = datetime.datetime.now()
    time_now = datetime.datetime(year=time_now.year, month=time_now.month,
                                 day=time_now.day, hour=time_now.hour + 1,
                                 minute=0, second=0)
    time_before = time_now + datetime.timedelta(hours=-12)
    time_now_stamp = trans2mk(time_now.strftime(TIME_FORMATTER))
    time_before_stamp = trans2mk(time_before.strftime(TIME_FORMATTER))
    x_array = list(range(time_before_stamp, time_now_stamp,
                         int((time_now_stamp - time_before_stamp) / 12)))
    parse = Parse()
    x_array.append(time_now_stamp)
    x_array = [(x_array[index], x_array[index + 1]) for index in
               range(len(x_array) - 1)]
    y_array_1 = [parse.show_count("success", st=bf, et=ef) for bf, ef in
                 x_array]
    y_array_2 = [parse.show_count("fail", st=bf, et=ef) for bf, ef in x_array]
    x_array = [trans2date(item[1]) for item in x_array]
    x_array = ["%02d:%02d" % (item.hour, item.minute) for item in x_array]

    return jsonify({
        "x": x_array,
        "y_success": y_array_1,
        "y_fail": y_array_2,
    })


@monitorapp.route('/totalCount')
def _total_count():
    result = {}
    st = request.args.get("st") or 1
    et = request.args.get("et") or int(time.time())
    st = int(st)
    et = int(et)
    for key in ["after", "success", "fail", "before"]:
        p = Parse()
        result[key] = p.show_count(key, st=st, et=et)
    result["wait"] = Base.app.show_len()
    return jsonify(result)


@monitorapp.route("/")
def _index():
    #
    parse = Parse()
    table_key = ["id", "函数名", "处理线程", "创建时间", "状态"]
    array = []

    for obj in parse.get_desc_obj(10):
        try:
            status = "running"
            if obj.success_time:
                status = "success"
            elif obj.fail_time:
                status = "fail"

            array.append({
                "id": obj.task_id[:3] + "…",
                "funcname": obj.funcname,
                "thred": obj.task_tpid,
                "status": status,
                "beforetime": trans2date(obj.before_time).strftime(
                    "%m.%d %H:%M")
            })
        except Exception:
            pass

    time_now = datetime.datetime.now()
    time_now_stamp = trans2mk(time_now.strftime(TIME_FORMATTER))
    today = (
        trans2mk(datetime.datetime(year=time_now.year, month=time_now.month,
                                   day=time_now.day, hour=0, minute=0,
                                   second=0).strftime(TIME_FORMATTER)),
        time_now_stamp
    )
    week = (
        trans2mk((time_now + datetime.timedelta(weeks=-1)).strftime(
            TIME_FORMATTER)),
        time_now_stamp
    )
    month = (
        trans2mk((time_now + datetime.timedelta(days=-30)).strftime(
            TIME_FORMATTER)),
        time_now_stamp
    )
    count = {}
    for k in ["success", "fail"]:
        count[k] = {
            "today": parse.show_count(k, today[0], today[1]),
            "week": parse.show_count(k, week[0], week[1]),
            "month": parse.show_count(k, month[0], month[1]),
        }

    sucbili = {
        "today": {"name": "今天",
                  "value": get_bili(parse, datetime.datetime.now())[0]},
        "yest": {"name": "昨天", "value": get_bili(parse,
                                                 datetime.datetime.now() + datetime.timedelta(
                                                     days=-1))[0]},
        "qst": {"name": "前天", "value": get_bili(parse,
                                                datetime.datetime.now() + datetime.timedelta(
                                                    days=-2))[0]},
    }
    k4, v4 = get_bili(parse,
                      datetime.datetime.now() + datetime.timedelta(
                          days=-3))
    k5, v5 = get_bili(
        parse,
        datetime.datetime.now() + datetime.timedelta(
            days=-4)
    )
    k6, v6 = get_bili(
        parse,
        datetime.datetime.now() + datetime.timedelta(
            days=-5)
    )

    sucbili["kv4"] = {"name": v4, "value": k4}
    sucbili["kv5"] = {"name": v5, "value": k5}
    sucbili["kv6"] = {"name": v6, "value": k6}
    return render_template("index.html", table_key=table_key, array=array,
                           count=count, sucbili=sucbili)


def get_bili(parse: Parse, day: datetime.datetime):
    res = 0
    forstr = day.strftime("%m-%d")
    st = datetime.datetime(year=day.year, month=day.month, day=day.day)
    et = datetime.datetime(year=day.year, month=day.month, day=day.day,
                           hour=23, minute=59, second=59)
    st = trans2mk(st.strftime(TIME_FORMATTER))
    et = trans2mk(et.strftime(TIME_FORMATTER))
    suc = parse.show_count("success", st, et)
    total = parse.show_count("before", st, et)
    if total == 0:
        res = 0
    else:
        res = round(100 * suc / total,2)
    return res, forstr
