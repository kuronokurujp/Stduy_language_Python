import modules.broker.demo.controller as demo_ctrl
import modules.broker.demo.model as demo_model
import modules.broker.demo.event as demo_event

import modules.log.logger as log
from pathlib import Path

def test_broker_demo_order_send():
    logger = log.AppLogger(
        config_json_filepath="data/config/log.json", log_dirpath=Path("data/log")
    )

    model: demo_model.Model()
    ctrl: demo_ctrl.Controller = demo_ctrl.Controller(model=model, logger=logger)

    ctrl.event_ordersend()

