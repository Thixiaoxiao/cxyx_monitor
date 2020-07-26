# -*- coding: utf-8 -*-#
# -----------------------------------------------------------------------------
# Name:         base
# Description:  
# Author:       Chenxiyuxiao
# Date:         2020/7/20
# -----------------------------------------------------------------------------
from sqlalchemy import create_engine
from cxyx.core.config import Config


class Base:

    @classmethod
    def get_engine(cls):
        return create_engine(Config.MYSQL_URL)
