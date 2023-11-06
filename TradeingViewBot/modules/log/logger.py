#!/usr/bin/env python
import json
import logging
import datetime
from pathlib import Path
from logging import getLogger, config


# アプリのログを取るロガー
class AppLogger(object):
    __logger: logging.Logger = None
    __log_dirpath: Path = None
    __logfile_max: int = 2

    def __init__(self, config_json_filepath: str, log_dirpath: Path) -> None:
        # logファイルを置くディレクトリを作成
        self.__log_dirpath = log_dirpath
        self.__log_dirpath.mkdir(parents=True, exist_ok=True)

        with open(config_json_filepath, "r") as f:
            log_conf: dict = json.load(f)

            # ファイル名をタイムスタンプで作成
            log_conf["handlers"]["fileHandler"][
                "filename"
            ] = self.__log_dirpath.joinpath("{}.logs".format(
                datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S"))
            )
            config.dictConfig(log_conf)

            self.__logger = getLogger(__name__)

    def info(self, msg: str):
        self.__logger.info(msg)

    def warn(self, msg: str):
        self.__logger.warn(msg)

    def err(self, msg: str):
        self.__logger.error(msg)

    # ログファイルの整理
    def clearnup(self):
        find_list: list = list(self.__log_dirpath.glob('*.logs'))
        if len(find_list) <= self.__logfile_max:
            return

        # 日付が古いファイルを優先して削除
        for i in range(self.__logfile_max):
            del_filepath: Path = Path(find_list[i])
            del_filepath.unlink(missing_ok=True)


