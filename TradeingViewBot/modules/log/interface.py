#!/usr/bin/env python
from abc import ABC, abstractmethod


# TODO: Loggerwのインターフェイス
class ILoegger(ABC):
    @abstractmethod
    def info(self, msg: str):
        raise NotImplementedError()

    @abstractmethod
    def warn(self, msg: str):
        raise NotImplementedError()

    @abstractmethod
    def err(self, msg: str):
        raise NotImplementedError()

    # ログファイルの整理
    @abstractmethod
    def clearnup(self):
        raise NotImplementedError()
