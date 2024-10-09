#!/usr/bin/env python
import json
import logging
import datetime
import modules.log.interface
from pathlib import Path
from logging import getLogger, config


# printでログ出力するカスタムハンドラー
class PrintHandler(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)

    def flush(self):
        self.acquire()
        try:
            pass
        finally:
            self.release()

    def emit(self, record):
        try:
            msg = self.format(record)
            print(msg)
            self.flush()
        except RecursionError:
            raise
        except Exception:
            self.handleError(record)

    def __repr__(self):
        level = logging.getLevelName(self.level)
        name = "print"
        name = str(name)
        if name:
            name += " "
        return "<%s %s(%s)>" % (self.__class__.__name__, name, level)


# アプリのログを取るロガー
class AppLogger(modules.log.interface.ILoegger):
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
            log_conf["handlers"]["fileHandler"]["filename"] = (
                self.__log_dirpath.joinpath(
                    "{}.logs".format(
                        datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
                    )
                )
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
        find_list: list = list(self.__log_dirpath.glob("*.logs"))
        if len(find_list) <= self.__logfile_max:
            return

        # 日付が古いファイルを優先して削除
        for i in range(0, self.__logfile_max, 1):
            del_filepath: Path = Path(find_list[i])
            del_filepath.unlink(missing_ok=True)


# アプリのログを取るロガー
class PrintLogger(modules.log.interface.ILoegger):
    def __init__(self) -> None:
        pass

    def info(self, msg: str):
        print("info: {}".format(msg))

    def warn(self, msg: str):
        print("warn: {}".format(msg))

    def err(self, msg: str):
        print("err: {}".format(msg))

    # ログファイルの整理
    def clearnup(self):
        pass
