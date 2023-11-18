#!/usr/bin/env python
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

    @abstractmethod
    def event_update(self):
        raise NotImplementedError()

    @abstractmethod
    def even_open_strategy_form(self):
        raise NotImplementedError()

    @abstractmethod
    def even_add_strategy(self, name: str):
        raise NotImplementedError()

    @abstractmethod
    def event_error(self, ex: Exception):
        raise NotImplementedError()
