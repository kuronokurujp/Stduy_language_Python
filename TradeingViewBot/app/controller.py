#!/usr/bin/env python
import modules.ui.view
import modules.ui.interface
import modules.log.interface
import modules.ngrok.controller
import app.model


# TODO: アプリ制御
class Controller(modules.ui.interface.IUIViewEvent):
    __view: modules.ui.view.View = None
    __model: app.model.Model = None
    __logger: modules.log.interface.ILoegger = None

    # TODO: ngrok関連
    __ngrok_ctrl: modules.ngrok.controller.Controller = None

    __b_run_trade: bool = False

    def __init__(
        self, model: app.model.Model, logger: modules.log.interface.ILoegger = None
    ) -> None:
        self.__model = model

        self.__ngrok_ctrl = modules.ngrok.controller.Controller(
            model=self.__model.ngrok_model
        )
        self.__view = modules.ui.view.View(
            title=self.__model.ui_model.title,
            size=self.__model.ui_model.size,
            event_i=self,
        )
        self.__logger = logger
        # TODO: 日をまたいだら実行する必要はあるかも
        # 別スレッドがいいか
        self.__logger.clearnup()

    def open(self):
        self.__view.open()

    # 開始
    def event_open(self):
        self.__logger.info("画面表示")

    # TODO: トレード開始
    def event_run_trade(self):
        if not self.__b_run_trade:
            bRet, msg = self.__ngrok_ctrl.cmd_start_listen()
            if bRet:
                self.__logger.info("トレード開始: {}".format(msg))
                self.__b_run_trade = True
            else:
                self.__logger.info("トレード開始に失敗: {}".format(msg))
        else:
            bRet, msg = self.__ngrok_ctrl.cmd_stop_listen()
            if bRet:
                self.__logger.info("トレード停止: {}".format(msg))
                self.__b_run_trade = False
            else:
                self.__logger.info("トレード停止に失敗: {}".format(msg))
