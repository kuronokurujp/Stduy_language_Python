#!/usr/bin/env python
from abc import ABC, abstractmethod
import datetime


class BaseEventResult(object):
    _b_success: bool = False
    _err_msg: str = ""
    _ok_msg: str = ""

    @property
    def is_error(self) -> bool:
        return self.b_success == False

    @property
    def err_msg(self) -> str:
        return self._err_msg

    @property
    def ok_msg(self) -> str:
        return self._ok_msg


class BaseOrderSendEventResult(BaseEventResult):
    # 注文番号
    _ticket: int = 0


# TODO: 新規取引イベント
class IOrderSendEvent(ABC):
    @abstractmethod
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
        pass

    # TODO: イベントを走らせる
    @abstractmethod
    async def run(self) -> bool:
        return True

    # TODO: runの結果を取得
    @abstractmethod
    def result(self) -> BaseOrderSendEventResult:
        return BaseOrderSendEventResult()


# TODO: 決済結果
class ICloseSendEventResult(ABC):
    pass


# TODO: 決済取引イベント
class ICloseSendEvent(ABC):
    @abstractmethod
    def __init__(self, ticket: int, lots: float, price: float, slippage: int) -> None:
        pass

    @abstractmethod
    async def run(self) -> bool:
        return True

    # TODO: runの結果を取得
    @abstractmethod
    def result(self) -> ICloseSendEventResult:
        return ICloseSendEventResult()


# TODO: 全決済結果
class IAllCloseSendEventResult(ABC):
    pass


# TODO: 全決済取引イベント
class IAllCloseSendEvent(ABC):
    @abstractmethod
    async def run(self) -> bool:
        return True

    # TODO: runの結果を取得
    @abstractmethod
    def result(self) -> IAllCloseSendEventResult:
        return IAllCloseSendEventResult()
