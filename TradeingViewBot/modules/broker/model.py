#!/usr/bin/env python
from modules.broker.event import (
    BaseOrderSendEventResult,
    ICloseSendEventResult,
    IAllCloseSendEventResult,
)


class BaseModel(object):
    __retry_count: int = 10
    __order_delay: int = 1
    __order_list: list = list()

    @property
    def retry_count(self) -> int:
        return self.__retry_count

    @property
    def order_delay(self) -> int:
        return self.__order_delay

    def __init__(self) -> None:
        pass

    def add_orderevent_result(self, result: BaseOrderSendEventResult):
        self.__order_list.append(result)
