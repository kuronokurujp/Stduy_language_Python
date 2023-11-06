#!/usr/bin/env python
import toml
from pathlib import Path


class Model(object):
    __filepath: Path = None

    @property
    def filepath(self) -> Path:
        return self.__filepath

    def __init__(self, config_tomlfile_path: Path) -> None:
        # 設定ファイルのtomlファイルをロードしてパラメータ取得
        with open(config_tomlfile_path, "r", encoding="utf-8") as f:
            toml_dict: dict = toml.load(f)
            self.__set_config_dict(toml_dict=toml_dict)

    def __set_config_dict(self, toml_dict: dict):
        self.__filepath = Path(toml_dict["config"]["RRSS_EXCEL_FILEPATH"])

        if not self.__filepath.exists:
            raise Exception("rakuten rss excel file findnot {}".format(self.__filepath))
