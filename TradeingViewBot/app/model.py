#!/usr/bin/env python
import modules.ui.model
import modules.ngrok.model
from pathlib import Path

class Model(object):
    __ui_model: modules.ui.model.Model = None
    __ngrok_model: modules.ngrok.model.Model = None

    @property
    def ui_model(self) -> modules.ui.model.Model:
        return self.__ui_model

    @property
    def ngrok_model(self) -> modules.ngrok.model.Model:
        return self.__ngrok_model

    def __init__(self, ngrok_config_path: Path) -> None:
        self.__ui_model = modules.ui.model.Model()

        if ngrok_config_path is not None and ngrok_config_path.exists():
            self.__ngrok_model = modules.ngrok.model.Model(config_tomlfile_path=ngrok_config_path)

