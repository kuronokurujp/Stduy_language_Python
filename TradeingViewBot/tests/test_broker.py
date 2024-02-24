import modules.broker.demo.controller as demo_ctrl
import modules.broker.demo.model as demo_model
import modules.broker.demo.event as demo_event
import modules.background.thread as bk_thread
import modules.broker.const as bk_const
import modules.broker.controler as broker_ctrl
from modules.broker.event import (
    OrderSendEventResult,
    CloseSendEventResult,
)

import time
import datetime
import asyncio

import modules.log.logger as log
from pathlib import Path


class BrokerCallback(broker_ctrl.ICallbackControler):
    order_count: int = 0
    close_count: int = 0

    # 注文結果キャッチ
    def on_result_ordersend(self, result: OrderSendEventResult):
        if not result.is_error:
            print("成功")

        self.order_count = self.order_count + 1

    # 決済結果キャッチ
    def on_result_closesend(self, result: CloseSendEventResult):
        self.close_count = self.close_count + 1


# TODO: バックグラウンドで注文が可能かテスト
def test_broker_demo_order_send():
    logger = log.AppLogger(
        config_json_filepath="data/config/log.json", log_dirpath=Path("data/log")
    )
    bk_manger = bk_thread.Manager()

    broker_callback: BrokerCallback = BrokerCallback()

    model: demo_model.Model = demo_model.Model()
    ctrl: demo_ctrl.Controller = demo_ctrl.Controller(
        model=model, callback=broker_callback, b_debug=True, logger=logger
    )
    bk_manger.create(callback=ctrl)

    order_event: demo_event.OrderSendEvent = demo_event.OrderSendEvent(
        ticket=11234,
        symbol=bk_const.SYMBOL_TYPE_225_MINI,
        # 戦略名
        strategy="TestST",
        # 証券会社
        broker=bk_const.BROKER_TYPE_DEMO,
        cmd=bk_const.CMD_ORDER_BUY,
        volume=1000,
        price=35000,
        slippage=999,
        stoploss=455,
        takeprofit=123,
        lot=1,
        comment="Comment",
        magic=99,
        expiration=datetime.datetime.now(),
        spread=10,
    )

    # TODO: テスト中
    while bk_manger.is_threads:
        time.sleep(1)
        # TODO: イベントを作成
        ctrl.event_ordersend(event=order_event)

        if 1 <= broker_callback.order_count:
            asyncio.run(bk_manger.async_all_delete())
