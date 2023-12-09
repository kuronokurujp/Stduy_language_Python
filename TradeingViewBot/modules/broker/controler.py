#!/usr/bin/env python
import modules.log.interface
from abc import ABC, abstractmethod
from modules.broker.model import BaseModel
from modules.broker.event import (
    IOrderSendEvent,
    IAllCloseSendEvent,
    ICloseSendEvent,
    OrderSendEventResult,
    ICloseSendEventResult,
    IAllCloseSendEventResult,
)
import asyncio


# TODO: 制御イベントのコールバッククラス
class ICallbackControler(ABC):
    # 注文結果キャッチ
    @abstractmethod
    def on_result_ordersend(self, result: OrderSendEventResult):
        pass


# TODO: 証券会社制御の基本クラス
class BaseController(object):
    __model: BaseModel = None
    __callback: ICallbackControler = None

    def __init__(self, model: BaseModel, callback: ICallbackControler) -> None:
        self.__model = model
        self.__callback = callback

    # TODO: 新規取引イベント
    def event_ordersend(self, event: IOrderSendEvent):
        result: OrderSendEventResult = asyncio.run(self.__async_ordersend(event))
        # TODO: エラーがないか
        if result.is_error:
            pass
        else:
            pass
        self.__callback.on_result_ordersend(result=result)

    # TODO: 決済取引イベント
    def event_orderclose(self, event: ICloseSendEvent):
        pass

    # TODO: 全決済取引イベント
    def event_all_orderclose(self, event: IAllCloseSendEvent):
        pass

    # TODO: 新規取引の非同期処理
    async def __async_ordersend(
        self, event: IOrderSendEvent
    ) -> OrderSendEventResult:
        count: int = 0
        # TODO: 注文処理をする
        task = event.run()
        while True:
            b_result: bool = await task
            if b_result == True:
                break

            # TODO: 失敗した場合は指定回数まで繰り返す
            await asyncio.sleep(delay=self.__model.__order_delay)
            count = count + 1
            # TODO: 失敗した回数が一定以上だと失敗にして終了
            if self.__model.__retry_count < +count:
                break

        return event.result
