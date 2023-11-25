#!/usr/bin/env python
from abc import ABC, abstractmethod
import datetime


# TODO: UIViewのイベントインターフェイス
class IUIViewEvent(ABC):
    @abstractmethod
    def event_open(self):
        raise NotImplementedError()

    @abstractmethod
    def event_run_trade(self):
        raise NotImplementedError()

    @abstractmethod
    def event_update(self):
        raise NotImplementedError()

    @abstractmethod
    def event_new_strategy(self):
        raise NotImplementedError()

    @abstractmethod
    def event_update_strategy(self):
        raise NotImplementedError()

    @abstractmethod
    def even_add_strategy(self, name: str, b_demo: bool):
        raise NotImplementedError()

    @abstractmethod
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
        raise NotImplementedError()

    @abstractmethod
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
        raise NotImplementedError()

    @abstractmethod
    def event_error(self, ex: Exception):
        raise NotImplementedError()
