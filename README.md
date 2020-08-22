Cxyx-monitor
=======

*Installation*
------------

​        $ pip install cxyx_monitor


if want set sql config

as example :
    from cxyx import CXYX
    from cxyx_monitor import patch_all
    patch_all()
    app = CXYX(__name__)
    app.config_from_object({

        ...
        "mysql_url":      "sqlite:///test2.db?check_same_thread=False",
        ...
    })

