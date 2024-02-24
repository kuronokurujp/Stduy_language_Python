#!/usr/bin/env python
from abc import ABC, abstractmethod
import datetime


# TODO: イベント結果のひな形クラス
class BaseEventResult(object):
    __b_success: bool = False
    __err_msg: str = ""
    __ok_msg: str = ""

    @property
    def is_error(self) -> bool:
        return not self.__b_success

    @property
    def err_msg(self) -> str:
        return self.__err_msg

    @property
    def ok_msg(self) -> str:
        return self.__ok_msg

    def set(self, b_success: bool, err_msg: str = "", ok_msg: str = ""):
        self.__b_success = b_success
        self.__err_msg = err_msg
        self.__ok_msg = ok_msg


# TODO: 注文イベントの結果
class OrderSendEventResult(BaseEventResult):
    # 戦略番号
    st_id: int = 0

    # 注文番号
    ticket: int = 0
    # 注文時間
    date_time: str = ""
    # 戦略名
    strategy: str = ""
    # 証券会社
    broker: str = ""
    symbol: str = ""
    cmd: int = 0
    volume: float = 0.0
    price: float = 0.0
    slippage: int = 0.0
    stoploss: float = 0.0
    takeprofit: float = 0.0
    comment: str = None
    magic: int = 0
    expiration: datetime.datetime = 0
    spread: float = -1
    lot: float = 0

    def __init__(
        self,
        st_id: int,
        ticket: int,
        # 戦略名
        strategy: str,
        # 証券会社
        broker: str,
        symbol: int,
        cmd: int,
        volume: float,
        price: float,
        slippage: int,
        stoploss: float,
        takeprofit: float,
        comment: str,
        magic: int,
        expiration: datetime.datetime,
        spread: float,
        lot: float,
    ) -> None:
        super().__init__()

        self.st_id = st_id
        self.ticket = ticket
        self.strategy = strategy
        self.broker = broker
        self.symbol = symbol
        self.cmd = cmd
        self.volume = volume
        self.price = price
        self.slippage = slippage
        self.stoploss = stoploss
        self.takeprofit = takeprofit
        self.comment = comment
        self.magic = magic
        self.expiration = expiration
        self.spread = spread
        self.lot = lot


# TODO: 新規取引イベント
class IOrderSendEvent(ABC):
    __result: OrderSendEventResult = None

    # TODO: runの結果を取得
    @property
    def result(self) -> OrderSendEventResult:
        return self.__result

    def __init__(
        self,
        # 戦略ID
        st_id: int,
        # 注文チケット
        ticket: int,
        # 銘柄
        symbol: int,
        # 戦略名
        strategy: str,
        # 証券会社
        broker: str,
        cmd: int,
        volume: float,
        price: float,
        slippage: int,
        stoploss: float,
        takeprofit: float,
        lot: float,
        comment: str,
        magic: int,
        expiration: datetime.datetime,
        spread: float,
    ) -> None:
        self.__result = OrderSendEventResult(
            st_id=st_id,
            ticket=ticket,
            # 戦略名
            strategy=strategy,
            # 証券会社
            broker=broker,
            symbol=symbol,
            cmd=cmd,
            volume=volume,
            price=price,
            slippage=slippage,
            stoploss=stoploss,
            takeprofit=takeprofit,
            comment=comment,
            magic=magic,
            expiration=expiration,
            spread=spread,
            lot=lot,
        )
        pass

    # TODO: イベントを走らせる
    @abstractmethod
    async def run(self) -> int:
        return 0


# TODO: 決済結果
class CloseSendEventResult(BaseEventResult):
    st_id: int = 0
    ticket: int = 0
    lot: float = 0.0
    price: float = 0.0
    slippage: int = 0
    expiration: datetime.datetime = 0

    def __init__(
        self,
        st_id: int,
        ticket: int,
        lot: float,
        price: float,
        slippage: int,
    ) -> None:
        self.st_id = st_id
        self.ticket = ticket
        self.lot = lot
        self.price = price
        self.slippage = slippage

    def set(
        self,
        b_success: bool,
        err_msg: str = "",
        ok_msg: str = "",
        expiration: datetime.datetime = 0,
    ):
        super().set(b_success=b_success, err_msg=err_msg, ok_msg=ok_msg)
        self.expiration = expiration


# TODO: 決済取引イベント
class ICloseSendEvent(ABC):
    __result: CloseSendEventResult = None

    # TODO: runの結果を取得
    @property
    def result(self) -> CloseSendEventResult:
        return self.__result

    def __init__(
        self,
        st_id: int,
        ticket: int,
        lot: float = -1.0,
        price: float = -1.0,
        slippage: int = -1.0,
    ) -> None:
        self.__result = CloseSendEventResult(
            st_id=st_id, ticket=ticket, lot=lot, price=price, slippage=slippage
        )

    @abstractmethod
    async def run(self) -> int:
        return 0
