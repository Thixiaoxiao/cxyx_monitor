from cxyx_monitor.core.monitor_engine import monitorapp


def create_monitor():
    monitorapp.run(
        host="0.0.0.0",
        port=9999
    )
