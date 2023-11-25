#!/usr/bin/env python
import modules.ui.model
import modules.ngrok.model

import modules.broker.model
import modules.broker.const
import modules.broker.demo.model
import modules.broker.rrss.model

import modules.strategy.object
from pathlib import Path


# TODO: モデル設定のクラス
class ModelConfig(object):
    ngrok_config_path: Path = None
    rrss_config_tomlfile_path: Path = None


class Model(object):
    __ui_model: modules.ui.model.Model = None
    __ngrok_model: modules.ngrok.model.Model = None
    __broker_models: dict[int, modules.broker.model.BaseModel] = dict()
    __strategy_data_manager: modules.strategy.object.DataObjectManager = (
        modules.strategy.object.DataObjectManager()
    )

    # TODO: 証券会社を設定しないとだめ
    __default_broker_type: int = modules.broker.const.BROKER_TYPE_DEMO

    @property
    def broker_type(self) -> int:
        return self.__default_broker_type

    @property
    def ui_model(self) -> modules.ui.model.Model:
        return self.__ui_model

    @property
    def ngrok_model(self) -> modules.ngrok.model.Model:
        return self.__ngrok_model

    def __init__(self, config: ModelConfig) -> None:
        self.__ui_model = modules.ui.model.Model()

        if config.ngrok_config_path is not None and config.ngrok_config_path.exists():
            self.__ngrok_model = modules.ngrok.model.Model(
                config_tomlfile_path=config.ngrok_config_path
            )

        # TODO: 各証券会社のモデルを設定
        self.__broker_models[
            modules.broker.const.BROKER_TYPE_DEMO
        ] = modules.broker.demo.model.Model()
        self.__broker_models[
            modules.broker.const.BROKER_TYPE_RAKUTEN_RSS
        ] = modules.broker.rrss.model.Model(
            config_tomlfile_path=config.rrss_config_tomlfile_path
        )

    # TODO: 戦略の追加
    def add_strategy(self, name: str, broker_type: int) -> tuple[bool, str, int]:
        return self.__strategy_data_manager.add_object(
            name=name, broker_type=broker_type
        )

    # TODO: 戦略の削除
    def del_strategy(self, id: int) -> tuple[bool, str]:
        return self.__strategy_data_manager.del_object(id=id)

    # TODO: 戦略の取得
    def get_strategy(self, id: int) -> modules.strategy.object.DataObject:
        return self.__strategy_data_manager.objects[id]

    def get_broker_model(self, broker_type: int) -> modules.broker.model.BaseModel:
        return self.__broker_models[broker_type]
