#!/usr/bin/env python
import configparser
import pathlib


# iniファイルを扱う基本モデル
class IniFileBaseModel(object):
    # ConfigParserオブジェクトを作成
    _config = configparser.ConfigParser()

    def __init__(self, logic_filepath: pathlib.Path) -> None:
        # INIファイルを読み込む
        # UTF-8エンコーディングでファイルを読み込む
        with open(logic_filepath, "r", encoding="utf-8") as configfile:
            self._config.read_file(configfile)

    def err_msg(self) -> str:
        # モデルエラーになっているか判定してエラーメッセージを返す
        return None


# 設定情報のモデル
class ConfigModel(IniFileBaseModel):
    @property
    def username(self) -> str:
        return self._config["tv_acount"]["username"]

    @property
    def password(self) -> str:
        return self._config["tv_acount"]["psssword"]

    def err_msg(self) -> str:
        # モデルエラーになっているか判定してエラーメッセージを返す
        return None
