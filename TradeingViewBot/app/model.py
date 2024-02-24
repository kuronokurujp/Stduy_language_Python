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
    __ngrok_config_path: Path = None
    __rrss_config_tomlfile_path: Path = None

    @property
    def ngrok_config_path(self) -> Path:
        return self.__ngrok_config_path

    @property
    def rrss_config_tomlfile_path(self) -> Path:
        return self.__rrss_config_tomlfile_path

    def __init__(
        self, ngrok_config_path: Path = None, rrss_config_tomlfile_path: Path = None
    ) -> None:
        self.__ngrok_config_path = ngrok_config_path
        self.__rrss_config_tomlfile_path = rrss_config_tomlfile_path

    # TODO: Ngrokのコンフィグが存在するか
    def exists_ngrok_config(self) -> bool:
        return (
            self.__ngrok_config_path is not None and self.__ngrok_config_path.exists()
        )

    # TODO: 楽天RSSのコンフィグが存在するか
    def exists_rrss_config(self) -> bool:
        return (
            self.__rrss_config_tomlfile_path is not None
            and self.__rrss_config_tomlfile_path.exists()
        )


class Model(object):
    __ui_model: modules.ui.model.Model = None
    __ngrok_model: modules.ngrok.model.Model = None
    __broker_models: dict[int, modules.broker.model.BaseModel] = dict()
    __strategy_data_manager: modules.strategy.object.DataObjectManager = (
        modules.strategy.object.DataObjectManager()
    )
    __b_debug: bool = False

    @property
    def ui_model(self) -> modules.ui.model.Model:
        return self.__ui_model

    @property
    def ngrok_model(self) -> modules.ngrok.model.Model:
        return self.__ngrok_model

    def __init__(self, config: ModelConfig, b_debug: bool = False) -> None:
        self.__b_debug = b_debug
        self.__ui_model = modules.ui.model.Model(b_debug=self.__b_debug)

        if config.exists_ngrok_config():
            self.__ngrok_model = modules.ngrok.model.Model(
                config_tomlfile_path=config.ngrok_config_path
            )

        # TODO: 各証券会社のモデルを設定
        self.__broker_models[
            modules.broker.const.BROKER_TYPE_DEMO
        ] = modules.broker.demo.model.Model()
        # TODO: 楽天RSSの設定があれば専用モデルを作成
        if config.exists_rrss_config():
            self.__broker_models[
                modules.broker.const.BROKER_TYPE_RAKUTEN_RSS
            ] = modules.broker.rrss.model.Model(
                config_tomlfile_path=config.rrss_config_tomlfile_path
            )

    # TODO: 戦略の追加
    def add_strategy(
        self, name: str, broker_type: int, symbole_type: int, lot: float
    ) -> tuple[bool, str, int, int]:
        return self.__strategy_data_manager.add_object(
            name=name, broker_type=broker_type, symbol_type=symbole_type, lot=lot
        )

    # TODO: 戦略の削除
    def del_strategy_at(self, idx: int) -> tuple[bool, str]:
        return self.__strategy_data_manager.del_object(id=idx)

    # TODO: 戦略の取得
    def get_strategy_at(self, idx: int) -> modules.strategy.object.DataObject:
        return self.__strategy_data_manager.get_object_at(idx=idx)

    # TODO: 戦略の取得(idから)
    def get_strategy(self, id: int) -> modules.strategy.object.DataObject:
        return self.__strategy_data_manager.get_object(id=id)

    # TODO: 証券会社のモデルを取得
    def get_broker_model(self, broker_type: int) -> modules.broker.model.BaseModel:
        if broker_type in self.__broker_models:
            return self.__broker_models[broker_type]
        return None
