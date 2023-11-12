#!/usr/bin/env python
import app.controller
import app.model
import modules.log.logger
from pathlib import Path


# TODO: アプリ開始テスト
def test_start_app():
    logger = modules.log.logger.AppLogger(
        config_json_filepath="data/config/log.json", log_dirpath=Path("data/log")
    )

    app_model = app.model.Model(ngrok_config_path=Path("data/config/ngrok.toml"))
    app_ctrl = app.controller.Controller(model=app_model, logger=logger)
    app_ctrl.open()
