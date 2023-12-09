#!/usr/bin/env python
from abc import ABC, abstractmethod
import datetime

# TODO: 定数一覧
ORDER_BUY: int = 0
ORDER_SELL: int = 1

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
    def event_add_strategy(self, name: str, broker_name: str, symbole_type: int, lot: float) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def event_order(
        self,
        broker: int,
        symbol: int,
        cmd: int,
        magic: int,
        price: float = -1,
        slippage: int = -1,
        stoploss: float = -1,
        takeprofit: float = -1,
        volume: float = -1,
        comment: str = None,
        aExpiration: datetime.datetime = -1,
        aSpread: float = -1,
    ):
        raise NotImplementedError()

    @abstractmethod
    def event_simple_order(
        self,
        st_idx: int,
        cmd: int,
    ):
        raise NotImplementedError()

    @abstractmethod
    def event_all_close(self):
        raise NotImplementedError()

    @abstractmethod
    def event_error(self, type, value, trace):
        raise NotImplementedError()
