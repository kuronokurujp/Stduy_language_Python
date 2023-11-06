#!/usr/bin/env python
import toml
from pathlib import Path


# ngrokのコントローラーのデータモデル
class Model(object):
    __token: str = ""
    __http_port: int = 0

    @property
    def token(self) -> str:
        return self.__token

    @property
    def http_port(self) -> int:
        return self.__http_port

    def __init__(self, config_tomlfile_path: Path) -> None:
        # 設定ファイルのtomlファイルをロードしてパラメータ取得
        with open(config_tomlfile_path, "r", encoding="utf-8") as f:
            toml_dict: dict = toml.load(f)
            self.__token = toml_dict["config"]["AUTHTOKEN"]
            self.__http_port = toml_dict["config"]["HTTP_PORT"]
