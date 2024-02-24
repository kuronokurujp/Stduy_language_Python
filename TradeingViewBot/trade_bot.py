#!/usr/bin/env python
import app.controller
import app.model
import modules.log.logger
from pathlib import Path

if __name__ == "__main__":
    model_config: app.model.ModelConfig = app.model.ModelConfig(
        ngrok_config_path=Path("data/config/ngrok.toml")
    )
    app_model = app.model.Model(config=model_config)
    app_ctrl = app.controller.Controller(
        model=app_model, logger=modules.log.logger.PrintLogger()
    )
    app_ctrl.open()
