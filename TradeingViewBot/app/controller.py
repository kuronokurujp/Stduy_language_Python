#!/usr/bin/env python
import app.model
import datetime
import traceback
import modules.ui.view as ui_view
import modules.ui.interface as ui_interface
import modules.utility.random as utility_rnd
import modules.log.interface as log_interface

import modules.ngrok.controller as ng_ctrl
import modules.ngrok.interface as ng_interface
import modules.ngrok.model as ng_model
import modules.strategy.object as st_obj

import modules.broker.const as bk_const
import modules.broker.model as bk_model
import modules.broker.controler as bk_ctrl
import modules.broker.demo.controller as bk_demo_ctrl
import modules.broker.demo.event as bk_demo_event
import modules.broker.rrss.controller as bk_rrss_ctrl

import modules.background.thread as bk_thread

import pyperclip


# TODO: アプリ制御
class Controller(ui_interface.IUIViewEvent, bk_ctrl.ICallbackControler):
    __view_ctrl: ui_view.ViewController = None
    __model: app.model.Model = None
    __logger: log_interface.ILoegger = None
    __bk_thread_manger: bk_thread.Manager = bk_thread.Manager()

    # TODO: ngrok関連
    __ngrok_ctrl: ng_ctrl.Controller = None
    __broker_ctrls: dict[int, bk_ctrl.BaseController] = dict()

    __b_run_trade: bool = False

    @property
    def view(self) -> ui_view.ViewController:
        return self.__view_ctrl

    def __init__(
        self, model: app.model.Model, logger: log_interface.ILoegger = None
    ) -> None:
        self.__model = model

        # TODO: Ngrokの機能作成
        self.__ngrok_ctrl = self._create_ngrok_ctrl(self.__model.ngrok_model)
        self.__view_ctrl = ui_view.ViewController(
            model=self.__model.ui_model,
            event_i=self,
        )

        self.__logger = logger
        # TODO: 日をまたいだら実行する必要はあるかも
        # 別スレッドがいいか
        self.__logger.clearnup()

        # TODO: 証券口座の制御を作成
        self.__broker_ctrls[bk_const.BROKER_TYPE_DEMO] = bk_demo_ctrl.Controller(
            model=self.__model.get_broker_model(bk_const.BROKER_TYPE_DEMO),
            callback=self,
            logger=logger,
        )
        # TODO: バックグラウンドスレッド設定
        self.__bk_thread_manger.create(self.__broker_ctrls[bk_const.BROKER_TYPE_DEMO])

        rrss_model = self.__model.get_broker_model(bk_const.BROKER_TYPE_RAKUTEN_RSS)
        if rrss_model is not None:
            self.__broker_ctrls[
                bk_const.BROKER_TYPE_RAKUTEN_RSS
            ] = bk_rrss_ctrl.Controller(
                model=rrss_model,
                callback=self,
                logger=logger,
            )

    def _create_ngrok_ctrl(
        self, model: ng_model.Model
    ) -> ng_interface.INgrokController:
        return ng_ctrl.Controller(model=model)

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
            broker_names=list(bk_const.BROKER_TYPE_MAP.values())
        )

    # TODO: 戦略を更新
    def event_update_strategy(self):
        # TODO: 戦略追加のウィンドウが必要
        # メインウィンドウの入力はだめ
        # すでに設定しているパラメータを設定
        self.__view_ctrl.open_strategy_form(
            list(broker_names=bk_const.BROKER_TYPE_MAP.values())
        )

    # TODO: 戦略を追加
    def event_add_strategy(
        self, name: str, broker_name: str, symbole_type: int, lot: float
    ) -> bool:
        # TODO: 指定証券会社名がなければ失敗
        if broker_name not in bk_const.BROKER_TYPE_MAP.values():
            raise Exception("証券会社の選択に失敗({})".format(broker_name))
            return False

        broker_type: int = [
            k for k, v in bk_const.BROKER_TYPE_MAP.items() if v == broker_name
        ][0]
        b_flg, msg, id, idx = self.__model.add_strategy(
            name=name, broker_type=broker_type, symbole_type=symbole_type, lot=lot
        )
        if b_flg:
            # TODO: 戦略テーブルに追加
            object: st_obj.DataObject = self.__model.get_strategy_at(idx)
            self.__view_ctrl.add_item_strategy(
                id=id,
                b_demo=broker_type == bk_const.BROKER_TYPE_DEMO,
                name=object.name,
                lot=object.lot,
            )
        else:
            self.__logger.err(msg)

    # TODO: 新規注文
    def event_order(
        self,
        st_id: int,
        cmd: int,
        magic: int,
        lot: float,
        ticket: int,
        price: float = -1,
        slippage: int = -1,
        stoploss: float = -1,
        takeprofit: float = -1,
        volume: float = 1,
        comment: str = None,
        aExpiration: datetime.datetime = -1,
        aSpread: float = -1,
    ):
        # TODO: 注文のイベント作成して対応ブローカーに投げる
        order_event: bk_ctrl.IOrderSendEvent = None

        st: st_obj.DataObject = self.__model.get_strategy(id=st_id)

        broker_name: str = bk_const.BROKER_TYPE_MAP[st.broker_type]
        match (st.broker_type):
            case bk_const.BROKER_TYPE_DEMO:
                order_event = bk_demo_event.OrderSendEvent(
                    st_id=st_id,
                    ticket=ticket,
                    symbol=st.symbole_type,
                    # 戦略名
                    strategy=st.name,
                    # 証券会社
                    broker=broker_name,
                    cmd=cmd,
                    volume=volume,
                    price=price,
                    slippage=slippage,
                    stoploss=stoploss,
                    takeprofit=takeprofit,
                    lot=lot,
                    comment=comment,
                    magic=magic,
                    expiration=aExpiration,
                    spread=aSpread,
                )

        # TODO: 取引実行する
        self.__broker_ctrls[st.broker_type].event_ordersend(order_event)

    # TODO: 戦略データidx指定での新規注文
    def event_simple_order(self, st_idx: int, cmd: int):
        current_st_obj: st_obj.DataObject = self.__model.get_strategy_at(idx=st_idx)
        # TODO: 失敗
        if current_st_obj is None:
            # TODO: エラー
            raise Exception("存在しない戦略データを指定({})".format(st_idx))

        # UIのコマンドから証券会社のコマンドに変える
        cmd_order: int = bk_const.CMD_ORDER_BUY
        if cmd == ui_interface.ORDER_BUY:
            cmd_order = bk_const.CMD_ORDER_BUY
        elif cmd == ui_interface.ORDER_SELL:
            cmd_order = bk_const.CMD_ORDER_SELL
        else:
            # TODO: エラー
            raise Exception("売買タイプが間違っている({})".format(cmd))

        # TODO: 銘柄に応じた現在の最新価格を取得
        volume: float = 0
        # TODO: チケットを生成
        ticket: int = utility_rnd.random_num()

        # TODO: チケットがかぶっていないかチェック
        # TODO: かぶっているならかぶらない値を作る

        self.event_order(
            current_st_obj.id,
            cmd=cmd_order,
            magic=st_idx,
            lot=current_st_obj.lot,
            volume=volume,
            ticket=ticket,
        )

    # TODO: すべての注文を強制決済
    def event_all_close(self, st_idx: int):
        current_st_obj: st_obj.DataObject = self.__model.get_strategy_at(idx=st_idx)
        # TODO: 失敗
        if current_st_obj is None:
            # TODO: エラー
            raise Exception("存在しない戦略データを指定({})".format(st_idx))

        # TODO: 注文のイベント作成して対応ブローカーに投げる
        close_event: bk_ctrl.ICloseSendEvent = None

        # TODO: 戦略と結びついたすべての取引チケットに決済イベント発行する
        for ticket in current_st_obj.transaction_tickets:
            # TODO: 決済イベント呼ぶ
            match (current_st_obj.broker_type):
                case bk_const.BROKER_TYPE_DEMO:
                    close_event = bk_demo_event.CloseSendEvent(
                        st_id=current_st_obj.id,
                        ticket=ticket,
                    )
                    # TODO: 決済実行する
                    self.__broker_ctrls[current_st_obj.broker_type].event_orderclose(
                        close_event
                    )

    # TODO: トレーディングビューのアラートURLを取得
    def event_copy_alert_url(self, st_idx: int):
        current_st_obj: st_obj.DataObject = self.__model.get_strategy_at(idx=st_idx)
        # TODO: 失敗
        if current_st_obj is None:
            # TODO: エラー
            raise Exception("存在しない戦略データを指定({})".format(st_idx))

        # TODO: トレーディングビューのURLを生成してクリップボードでコピー
        webhook_url = self.__ngrok_ctrl.get_url()
        # URLに別のパスを追加することができる
        # クエリにストラテジー情報を含める
        webhook_url = "{}/25f4b493-85fe-11ee-92c2-7c7635fff5e0?id={}".format(
            webhook_url, current_st_obj.id
        )
        pyperclip.copy(webhook_url)
        print(webhook_url)

    # TODO: アラートメッセージ
    def event_copy_alert_message(self, st_idx: int):
        current_st_obj: st_obj.DataObject = self.__model.get_strategy_at(idx=st_idx)
        # TODO: 失敗
        if current_st_obj is None:
            # TODO: エラー
            raise Exception("存在しない戦略データを指定({})".format(st_idx))

        msg: str =  "@RRSS, @{{ticker}} で @{{strategy.order.action}} @{{strategy.order.contracts}} 約定。ポジは @{{strategy.position_size}}"
        pyperclip.copy(msg)

    # TODO: エラー
    def event_error(self, type, value, trace):
        # TODO: デバッグ時は詳細表示する？
        self.__logger.err(
            "例外:{}が起きた.\n 例外は{}.\n 起きた箇所は\n{}".format(
                type, value, traceback.format_tb(trace)
            )
        )

    # TODO: 注文結果キャッチ
    def on_result_ordersend(self, result: bk_ctrl.OrderSendEventResult):
        if result.is_error:
            # 注文失敗
            self.__logger.err(result.err_msg)
            # TODO: アラートを出すのがいいか？
        else:
            # 注文成功
            # self.__logger.info(result.ok_msg)
            # TODO: 注文成功した場合はチケットをストラテジーに追加
            # TODO: 取引情報を戦略に結びつける
            st: st_obj.DataObject = self.__model.get_strategy(id=result.st_id)
            st.add_ticket(result.ticket)

            # TODO: 取引項目を追加
            self.__view_ctrl.add_transaction_item(
                # 注文番号
                ticket=result.ticket,
                # 注文時間
                date_time=result.date_time,
                # 戦略名
                strategy=result.strategy,
                # 証券会社
                broker=result.broker,
                # 銘柄
                symbol=result.symbol,
                # 売買タイプ
                cmd=bk_const.CMD_ORDER_TYPE_MAP[result.cmd],
                # 売買時の価格
                volume=result.volume,
                # 取引数量
                lot=result.lot,
                # 損切価格
                stoploss=result.stoploss,
                # 決済価格
                takeprofit=result.stoploss,
            )

    # 決済結果キャッチ
    def on_result_closesend(self, result: bk_ctrl.CloseSendEventResult):
        if result.is_error:
            # 注文失敗
            self.__logger.err(result.err_msg)
            # TODO: アラートを出すのがいいか？
        else:
            # 注文成功
            # self.__logger.info(result.ok_msg)

            # TODO: 注文成功した場合はチケットをストラテジーから外す
            st: st_obj.DataObject = self.__model.get_strategy(id=result.st_id)
            st.remove_ticket(result.ticket)

            # TODO: 取引項目から指定したチケットを削除
            # TODO: 口座履歴に追加
            self.__view_ctrl.move_transaction_to_account_history(
                ticket=result.ticket, price=result.price, expiration=result.expiration
            )
