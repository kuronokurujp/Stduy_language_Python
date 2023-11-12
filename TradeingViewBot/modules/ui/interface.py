#!/usr/bin/env python
from abc import ABC, abstractmethod


# TODO: UIViewのイベントインターフェイス
class IUIViewEvent(ABC):
    @abstractmethod
    def event_open(self):
        raise NotImplementedError()

    @abstractmethod
    def event_run_trade(self):
        raise NotImplementedError()
