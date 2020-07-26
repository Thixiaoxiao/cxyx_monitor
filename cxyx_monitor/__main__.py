# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         __main__
# Description:  
# Author:       Chenxiyuxiao
# Date:         2020/7/20
# -------------------------------------------------------------------------------
from importlib import import_module
import sys
import click
from cxyx_monitor.core.table import create_table

from cxyx_monitor.core.base import Base

from cxyx_monitor.utils.crete_monitor import create_monitor

sys.path.append("./")


@click.command()
@click.argument('path')
@click.argument('task')
def monitor(path,task):
    if ":" in path:
        file, obj = path.split(":")
        f = import_module(file)
        app = getattr(f, obj)

        setattr(Base, "app", app)
        # start server
        if task == "start":
            app.move_data()
            create_monitor()
        elif task == "create_table":
            create_table()
            return 0