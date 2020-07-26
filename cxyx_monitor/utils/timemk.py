# -*- coding: utf-8 -*-#
# -----------------------------------------------------------------------------
# Name:         timemk
# Description:  
# Author:       chenxiyuxiao
# Date:         2020/7/20
# -----------------------------------------------------------------------------
import time
import datetime

from cxyx_monitor.core import TIME_FORMATTER


def trans2mk(timestr):
    timeArray = time.strptime(timestr, TIME_FORMATTER)
    timeStamp = int(time.mktime(timeArray))
    return timeStamp


def trans2date(timestamp):
    return datetime.datetime.fromtimestamp(timestamp)


if __name__ == '__main__':
    print(trans2mk("2020-07-20 09:31"))
    print(trans2date(1595208660))
