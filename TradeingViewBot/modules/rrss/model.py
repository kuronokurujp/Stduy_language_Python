#!/usr/bin/env python
import modules.excel.model

from pathlib import Path


# 楽天RSSの制御モデル
class Model(modules.excel.model.Model):
    __order_flg_sell_cell: str = ""
    __order_flg_buy_cell: str = ""
    __close_flg_sell_cell: str = ""
    __close_flg_buy_cell: str = ""
    __pos_sell_cell: str = ""
    __pos_buy_cell: str = ""

    def __init__(self, config_tomlfile_path: Path) -> None:
        super().__init__(config_tomlfile_path=config_tomlfile_path)

    def __set_config_dict(self, toml_dict: dict):
        super().__set_config_dict(toml_dict=toml_dict)

        self.__order_flg_sell_cell = toml_dict["config"]["ORDER_FLG_SELL_CELL"]
        self.__order_flg_buy_cell = toml_dict["config"]["ORDER_FLG_BUY_CELL"]
        self.__close_flg_sell_cell = toml_dict["config"]["CLOSE_FLG_SELL_CELL"]
        self.__close_flg_buy_cell = toml_dict["config"]["CLOSE_FLG_BUY_CELL"]

        self.__pos_sell_cell = toml_dict["config"]["POSTION_SELL_CELL"]
        self.__pos_buy_cell = toml_dict["config"]["POSTION_SELL_CELL"]


