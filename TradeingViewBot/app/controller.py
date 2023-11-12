#!/usr/bin/env python
import modules.ui.view
import modules.ui.interface
import modules.log.interface
import modules.ngrok.controller
import modules.ngrok.interface
import modules.ngrok.model
import app.model


# TODO: アプリ制御
class Controller(modules.ui.interface.IUIViewEvent):
    __view: modules.ui.view.View = None
    __model: app.model.Model = None
    __logger: modules.log.interface.ILoegger = None

    # TODO: ngrok関連
    __ngrok_ctrl: modules.ngrok.controller.Controller = None

    __b_run_trade: bool = False

    @property
    def view(self) -> modules.ui.view.View:
        return self.__view

    def __init__(
        self, model: app.model.Model, logger: modules.log.interface.ILoegger = None
    ) -> None:
        self.__model = model

        self.__ngrok_ctrl = self._create_ngrok_ctrl(self.__model.ngrok_model)
        self.__view = modules.ui.view.View(
            title=self.__model.ui_model.title,
            size=self.__model.ui_model.size,
            event_i=self,
        )
        self.__logger = logger
        # TODO: 日をまたいだら実行する必要はあるかも
        # 別スレッドがいいか
        self.__logger.clearnup()

    def _create_ngrok_ctrl(
        self, model: modules.ngrok.model.Model
    ) -> modules.ngrok.interface.INgrokController:
        return modules.ngrok.controller.Controller(model=model)

    def open(self):
        # 初期表示は画面サイズをフルに
        self.__view.open(b_screen=True)

    # 開始
    def event_open(self):
        self.__logger.info("画面表示")

    # 更新
    def event_update(self):
        pass

    # TODO: トレード開始
    def event_run_trade(self):
        self.__view.setEnableByBtnRunTrade(enable=False)
        if not self.__b_run_trade:
            bRet, msg = self.__ngrok_ctrl.cmd_start_listen()
            if bRet:
                self.__logger.info("トレード開始: {}".format(msg))
                self.__logger.info(
                    "WebHookのURL: {}".format(self.__ngrok_ctrl.get_url())
                )
                self.__b_run_trade = True
            else:
                self.__logger.info("トレード開始に失敗: {}".format(msg))

            self.__view.setEnableByBtnRunTrade(enable=True)
        else:
            bRet, msg = self.__ngrok_ctrl.cmd_stop_listen()
            if bRet:
                self.__logger.info("トレード停止: {}".format(msg))
                self.__b_run_trade = False
            else:
                self.__logger.info("トレード停止に失敗: {}".format(msg))

            self.__view.setEnableByBtnRunTrade(enable=True)
