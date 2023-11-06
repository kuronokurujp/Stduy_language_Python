#!/usr/bin/env python
from modules.log.logger import AppLogger
import modules.excel.model
import xlwings as xw


# エクセルの制御クラス
class Controller(object):
    __model: modules.excel.model.Model = None
    __logger: AppLogger = None
    __xw_app: xw.App = None
    __book: xw.Book = None

    def __init__(
        self, model: modules.excel.model.Model, logger: AppLogger = None
    ) -> None:
        self.__model = model
        self.__logger = logger

    def __del__(self):
        self.close(bSave=True)

    def open(self) -> tuple[bool, str]:
        bRet: bool = False
        msg: str = ""
        try:
            if self.__logger is not None:
                self.__logger.info("excel open {}".format(self.__model.filepath))
            else:
                print("excel open {}".format(self.__model.filepath))

            # VBAファイルを開く
            self.__xw_app = xw.App(visible=True, add_book=False)
            self.__book = self.__xw_app.books.open(self.__model.filepath)

            bRet = True
        except Exception as ex:
            if self.__logger is not None:
                self.__logger.err("{}".format(ex))
            else:
                print("{}".format(ex))

            msg = ex
            bRet = False

        return bRet, msg

    def close(self, bSave=False) -> tuple[bool, str]:
        bRet: bool = False
        msg: str = ""

        try:
            if self.__book is not None:
                if self.__logger is not None:
                    self.__logger.info("excel close {}".format(self.__model.filepath))
                else:
                    print("excel close {}".format(self.__model.filepath))

                if bSave:
                    self.__book.save()

                # TODO:
                # ファイルを開いて手動でセーブをするとエラーになる
                # もう一度試したら起きなかった
                # 原因が分からないな
                self.__book.close()
                self.__book = None

            if self.__xw_app is not None:
                if self.__logger is not None:
                    self.__logger.info("excel quit {}".format(self.__model.filepath))
                else:
                    print("excel quit {}".format(self.__model.filepath))

                self.__xw_app.quit()
                self.__xw_app = None

            bRet = True
        except Exception as ex:
            bRet = False
            msg = ex

        return bRet, msg
