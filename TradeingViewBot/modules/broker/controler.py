#!/usr/bin/env python
from abc import ABC, abstractmethod
from modules.broker.model import BaseModel
from modules.broker.event import (
    IOrderSendEvent,
    ICloseSendEvent,
    OrderSendEventResult,
    CloseSendEventResult,
)
import modules.broker.const as bk_const
import modules.log.interface as log_interface
import threading
import asyncio
import modules.background.thread as bk_thread
import datetime


# TODO: 制御イベントのコールバッククラス
class ICallbackControler(ABC):
    # 注文結果キャッチ
    @abstractmethod
    def on_result_ordersend(self, result: OrderSendEventResult):
        pass

    # 決済結果キャッチ
    @abstractmethod
    def on_result_closesend(self, result: CloseSendEventResult):
        pass


# TODO: 証券会社制御の基本クラス
class BaseController(bk_thread.NodeCallback):
    __model: BaseModel = None
    __callback: ICallbackControler = None
    # __event_loop_thread = None
    __event_orders: list[IOrderSendEvent] = list[IOrderSendEvent]()
    __event_closes: list[ICloseSendEvent] = list[ICloseSendEvent]()
    __b_debug: bool = False
    __logger: log_interface.ILoegger = None

    def __init__(
        self,
        model: BaseModel,
        callback: ICallbackControler,
        logger: log_interface.ILoegger = None,
        b_debug: bool = False,
    ) -> None:
        self.__model = model
        self.__callback = callback
        self.__logger = logger
        self.__b_debug = b_debug

    def start_thread(self, lock: threading.RLock):
        pass

    # TODO: バックグラウンド処理
    def run_thread(self, lock: threading.RLock) -> bool:
        # TODO: 注文処理
        if 0 < len(self.__event_orders):
            # TODO: キャッシュした注文イベントを取得
            order_event: IOrderSendEvent = self.__event_orders.pop()
            # TODO: 注文イベントを実行
            result: OrderSendEventResult = asyncio.run(
                self.__async_ordersend(order_event)
            )
            # TODO: メインスレッドに処理を渡すのでロックしておく
            if self.__callback is not None:
                with lock:
                    self.__callback.on_result_ordersend(result=result)

        # TODO: 決済処理
        if 0 < len(self.__event_closes):
            close_event: ICloseSendEvent = self.__event_closes.pop()
            result: CloseSendEventResult = asyncio.run(
                self.__async_closesend(close_event)
            )

            if self.__callback is not None:
                with lock:
                    self.__callback.on_result_closesend(result=result)

        return True

    # TODO: バックグラウンド停止した時の処理
    def end_thread(self, lock: threading.RLock):
        pass

    def error_thread(self, ex: Exception, lock: threading.RLock):
        if self.__logger is None:
            return

        with lock:
            self.__logger.err(ex)

    # TODO: 新規取引イベント
    def event_ordersend(self, event: IOrderSendEvent):
        self.__event_orders.append(event)

    # TODO: 決済取引イベント
    def event_orderclose(self, event: ICloseSendEvent):
        self.__event_closes.append(event)

    # TODO: 新規取引の非同期処理
    async def __async_ordersend(self, event: IOrderSendEvent) -> OrderSendEventResult:
        count: int = 0
        # TODO: 注文処理をする
        task = asyncio.create_task(event.run())
        while True:
            result_code: int = await task

            # リザルト毎の処理を実行
            match result_code:
                case 0:
                    event.result.set(
                        b_success=True,
                        ok_msg="注文成功 チケット({}):  証券({}) ロット({}) 銘柄({}) 売買({})".format(
                            event.result.ticket,
                            event.result.broker,
                            event.result.lot,
                            event.result.symbol,
                            event.result.cmd,
                        ),
                    )
                case bk_const.ERR_CODE_MISS_CMD_PARAM:
                    event.result.set(
                        b_success=False,
                        err_msg="注文失敗 エラー番号({}): 証券({}) ロット({}) 銘柄({}) 売買({})".format(
                            result_code,
                            event.result.broker,
                            event.result.lot,
                            event.result.symbol,
                            event.result.cmd,
                        ),
                    )

            if not event.result.is_error:
                if self.__logger is not None:
                    self.__logger.info(event.result.ok_msg)
                break
            else:
                if self.__logger is not None:
                    self.__logger.err(event.result.err_msg)

            # TODO: 失敗した場合は指定回数まで繰り返す
            await asyncio.sleep(delay=self.__model.__order_delay)

            count = count + 1
            # TODO: 失敗した回数が一定以上だと失敗にして終了
            if self.__model.__retry_count < count:
                break

        return event.result

    # TODO: 決済処理
    async def __async_closesend(self, event: ICloseSendEvent) -> CloseSendEventResult:
        count: int = 0
        # TODO: 注文処理をする
        task = asyncio.create_task(event.run())
        while True:
            result_code: int = await task

            # リザルト毎の処理を実行
            match result_code:
                case 0:
                    event.result.set(
                        b_success=True,
                        ok_msg="決済成功 チケット({}):  ロット({}))".format(
                            event.result.ticket,
                            event.result.lot,
                        ),
                        # TODO: 決済した時間を書き込む
                        expiration=datetime.datetime.now(),
                    )
                case bk_const.ERR_CODE_MISS_CMD_PARAM:
                    event.result.set(
                        b_success=False,
                        err_msg="決済失敗 エラー番号({}): チケット({}) ロット({}) )".format(
                            result_code,
                            event.result.ticket,
                            event.result.lot,
                        ),
                    )

            if not event.result.is_error:
                if self.__logger is not None:
                    self.__logger.info(event.result.ok_msg)
                break
            else:
                if self.__logger is not None:
                    self.__logger.err(event.result.err_msg)

            # TODO: 失敗した場合は指定回数まで繰り返す
            await asyncio.sleep(delay=self.__model.order_delay)

            count = count + 1
            # TODO: 失敗した回数が一定以上だと失敗にして終了
            if self.__model.retry_count < count:
                break

        return event.result
