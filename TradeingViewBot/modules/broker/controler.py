#!/usr/bin/env python
import modules.log.interface
from modules.broker.model import BaseModel
from modules.broker.event import (
    IOrderSendEvent,
    IAllCloseSendEvent,
    ICloseSendEvent,
    BaseOrderSendEventResult,
    ICloseSendEventResult,
    IAllCloseSendEventResult,
)
import asyncio


class BaseController(object):
    __model: BaseModel = None
    __log: modules.log.interface.ILoegger = None

    def __init__(
        self, model: BaseModel, logger: modules.log.interface.ILoegger
    ) -> None:
        self.__model = model
        self.__log = logger

    # TODO: 新規取引イベント
    def event_ordersend(self, event: IOrderSendEvent):
        result: BaseOrderSendEventResult = asyncio.run(self.__async_ordersend(event))
        # TODO: エラーがないか
        if result.is_error():
            self.__log.err(result.err_msg())
        else:
            # TODO: 取引成功
            self.__log.info(result.ok_msg())
            # TODO: 取引成功したオーダー情報を管理するのでリストに設定
            self.__model.add_orderevent_result(result)

    # TODO: 決済取引イベント
    def event_orderclose(self, event: ICloseSendEvent):
        pass

    # TODO: 全決済取引イベント
    def event_all_orderclose(self, event: IAllCloseSendEvent):
        pass

    # TODO: 新規取引の非同期処理
    async def __async_ordersend(self, event: IOrderSendEvent) -> BaseOrderSendEventResult:
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

        return event.result()
