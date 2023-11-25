#!/usr/bin/env python
from modules.broker.event import (
    IOrderSendEvent,
    IAllCloseSendEvent,
    ICloseSendEvent,
    ICloseSendEventResult,
    IAllCloseSendEventResult,
    BaseOrderSendEventResult,
)
import datetime


# TODO: デモの注文リザルト
class OrderSendEventResult(BaseOrderSendEventResult):
    pass


# TODO: デモでの注文イベント
class OrderSendEvent(IOrderSendEvent):
    __result = OrderSendEventResult()

    def __init__(
        self,
        symbol: str,
        cmd: int,
        volume: float,
        price: float,
        slippage: int,
        stoploss: float,
        takeprofit: float,
        comment: str = None,
        magic: int = 0,
        expiration: datetime.datetime = 0,
        spread: float = -1,
    ) -> None:
        # TODO: 適当な値を入れる
        pass

    # TODO: イベントを走らせる
    async def run(self) -> bool:
        return True

    # TODO: runの結果を取得
    def result(self) -> BaseOrderSendEventResult:
        return self.__result
