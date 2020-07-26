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
def monitor(path):
    if ":" in path:
        file, obj = path.split(":")
        f = import_module(file)
        app = getattr(f, obj)

        app.move_data()
        setattr(Base, "app", app)
        # start server
        create_monitor()
    elif path == "create_table":
        create_table()
