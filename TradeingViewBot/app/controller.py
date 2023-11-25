#!/usr/bin/env python
import modules.ui.view
import modules.ui.interface

import modules.log.interface

import modules.ngrok.controller
import modules.ngrok.interface
import modules.ngrok.model

import modules.strategy.object

import modules.broker.const
import modules.broker.controler
import modules.broker.demo.controller
import modules.broker.rrss.controller

import datetime
import app.model


# TODO: アプリ制御
class Controller(modules.ui.interface.IUIViewEvent):
    __view_ctrl: modules.ui.view.ViewController = None
    __model: app.model.Model = None
    __logger: modules.log.interface.ILoegger = None

    # TODO: ngrok関連
    __ngrok_ctrl: modules.ngrok.controller.Controller = None
    __broker_ctrls: dict[int, modules.broker.controler.BaseController] = dict()

    __b_run_trade: bool = False

    @property
    def view(self) -> modules.ui.view.ViewController:
        return self.__view_ctrl

    def __init__(
        self, model: app.model.Model, logger: modules.log.interface.ILoegger = None
    ) -> None:
        self.__model = model

        self.__ngrok_ctrl = self._create_ngrok_ctrl(self.__model.ngrok_model)
        self.__view_ctrl = modules.ui.view.ViewController(
            title=self.__model.ui_model.title,
            size=self.__model.ui_model.size,
            event_i=self,
        )
        self.__logger = logger
        # TODO: 日をまたいだら実行する必要はあるかも
        # 別スレッドがいいか
        self.__logger.clearnup()

        # TODO: 証券口座の制御を作成
        self.__broker_ctrls[
            modules.broker.const.BROKER_TYPE_DEMO
        ] = modules.broker.demo.controller.Controller(
            model=self.__model.get_broker_model(modules.broker.const.BROKER_TYPE_DEMO),
            logger=logger,
        )
        self.__broker_ctrls[
            modules.broker.const.BROKER_TYPE_RAKUTEN_RSS
        ] = modules.broker.rrss.controller.Controller(
            model=self.__model.get_broker_model[
                modules.broker.const.BROKER_TYPE_RAKUTEN_RSS
            ],
            logger=logger,
        )

    def _create_ngrok_ctrl(
        self, model: modules.ngrok.model.Model
    ) -> modules.ngrok.interface.INgrokController:
        return modules.ngrok.controller.Controller(model=model)

    def open(self):
        # 初期表示は画面サイズをフルに
        self.__view_ctrl.open(b_screen=True)

    # 開始
    def event_open(self):
        self.__logger.info("画面表示")

    # 更新
    def event_update(self):
        pass

    # TODO: トレード開始
    def event_run_trade(self):
        self.__view_ctrl.enable_trade(b_enable=False)
        if not self.__b_run_trade:
            bRet, msg = self.__ngrok_ctrl.cmd_start_listen()
            if bRet:
                self.__logger.info("トレード開始: {}".format(msg))
                # self.__logger.info(
                #     "WebHookのURL: {}".format(self.__ngrok_ctrl.get_url())
                # )
                self.__b_run_trade = True
            else:
                self.__logger.info("トレード開始に失敗: {}".format(msg))

            self.__view_ctrl.enable_trade(b_enable=True)
        else:
            bRet, msg = self.__ngrok_ctrl.cmd_stop_listen()
            if bRet:
                self.__logger.info("トレード停止: {}".format(msg))
                self.__b_run_trade = False
            else:
                self.__logger.info("トレード停止に失敗: {}".format(msg))

            self.__view_ctrl.enable_trade(b_enable=True)

    # 戦略を新規追加
    def event_new_strategy(self):
        # 戦略追加のウィンドウが必要
        # メインウィンドウの入力はだめ
        self.__view_ctrl.open_strategy_form(
            broker_names=modules.broker.const.BROKER_TYPE_NAMES
        )

    # TODO: 戦略を更新
    def event_update_strategy(self):
        # TODO: 戦略追加のウィンドウが必要
        # メインウィンドウの入力はだめ
        # すでに設定しているパラメータを設定
        self.__view_ctrl.open_strategy_form(
            broker_names=modules.broker.const.BROKER_TYPE_NAMES
        )

    # TODO: 戦略を追加
    def even_add_strategy(self, name: str, b_demo: bool):
        # TODO: デモフラグが立っているなら設定した証券会社ではなくデモ用の戦略にする
        broker_type: int = self.__model.broker_type
        if b_demo:
            broker_type = modules.broker.const.BROKER_TYPE_DEMO

        b_flg, msg, id = self.__model.add_strategy(name=name, broker_type=broker_type)
        if b_flg:
            # self.__logger.info(msg)
            # TODO: 戦略テーブルに追加
            object: modules.strategy.object.DataObject = self.__model.get_strategy(id)
            self.__view_ctrl.add_item_strategy(
                id=id,
                b_demo=broker_type == modules.broker.const.BROKER_TYPE_DEMO,
                name=object.name,
                url=object.url,
            )
        else:
            self.__logger.err(msg)

    def event_order_buy(
        self,
        broker: int,
        symbol: str,
        cmd: int,
        volume: float,
        price: float,
        slippage: int,
        stoploss: float,
        takeprofit: float,
        comment: str = None,
        magic: int = 0,
        aExpiration: datetime.datetime = 0,
        aSpread: float = -1,
    ):
        pass

    def event_order_sell(
        self,
        broker: int,
        symbol: str,
        cmd: int,
        volume: float,
        price: float,
        slippage: int,
        stoploss: float,
        takeprofit: float,
        comment: str = None,
        magic: int = 0,
        aExpiration: datetime.datetime = 0,
        aSpread: float = -1,
    ):
        pass

    # TODO: エラー
    def event_error(self, ex: Exception):
        self.__logger.err(ex)

    # TODO: 新規取引実行
    # symbol            通貨ペア
    # cmd               注文種別
    # volume            ロット数
    # price             仕掛け価格
    # slippage          スリッページ（ポイント）
    # stoploss          損切り価格
    # takeprofit        利食い価格
    # comment           コメント
    # magic             マジックナンバー
    # expiration        待機注文の有効期限
    # spread            許容スプレッド
    def __ordersend(
        self,
        broker: str,
        symbol: str,
        cmd: int,
        volume: float,
        price: float,
        slippage: int,
        stoploss: float,
        takeprofit: float,
        comment: str = None,
        magic: int = 0,
        aExpiration: datetime.datetime = 0,
        aSpread: float = -1,
    ):
        match broker:
            case "":
                pass

    # TODO: 決済取引実行
    def __orderclose(self, ticket: int, lots: float, price: float, slippage: int):
        pass

    # TODO: 全決済取引実行
