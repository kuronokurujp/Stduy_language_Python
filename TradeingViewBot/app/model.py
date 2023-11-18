#!/usr/bin/env python
import modules.ui.model
import modules.ngrok.model
import modules.strategy.object
from pathlib import Path


class Model(object):
    __ui_model: modules.ui.model.Model = None
    __ngrok_model: modules.ngrok.model.Model = None
    __strategy_data_manager: modules.strategy.object.DataObjectManager = (
        modules.strategy.object.DataObjectManager()
    )

    @property
    def ui_model(self) -> modules.ui.model.Model:
        return self.__ui_model

    @property
    def ngrok_model(self) -> modules.ngrok.model.Model:
        return self.__ngrok_model

    def __init__(self, ngrok_config_path: Path) -> None:
        self.__ui_model = modules.ui.model.Model()

        if ngrok_config_path is not None and ngrok_config_path.exists():
            self.__ngrok_model = modules.ngrok.model.Model(
                config_tomlfile_path=ngrok_config_path
            )

    def add_strategy(self, name: str, url: str) -> tuple[bool, str, int]:
        return self.__strategy_data_manager.add_object(name=name, url=url)

    def del_strategy(self, id: int) -> tuple[bool, str]:
        return self.__strategy_data_manager.del_object(id=id)

    def get_strategy(self, id: int) -> modules.strategy.object.DataObject:
        return self.__strategy_data_manager.objects[id]
