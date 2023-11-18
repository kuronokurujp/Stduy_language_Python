import app.controller
import app.model
import modules.log.logger
from pathlib import Path

if __name__ == "__main__":
    app_model = app.model.Model(ngrok_config_path=Path("data/config/ngrok.toml"))
    app_ctrl = app.controller.Controller(
        model=app_model, logger=modules.log.logger.PrintLogger()
    )
    app_ctrl.open()
