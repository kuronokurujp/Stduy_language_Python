#!/usr/bin/env python
from modules.broker.event import (
    OrderSendEventResult,
    CloseSendEventResult,
)


class BaseModel(object):
    __retry_count: int = 10
    __order_delay: int = 1
    __order_list: list = list()
    __order_retry_count: int = 0
    __close_retry_count: int = 0
    __process_order_ticket: int = 0

    @property
    def order_retry_count(self) -> int:
        return self.__order_retry_count

    @property
    def retry_count(self) -> int:
        return self.__retry_count

    @property
    def order_delay(self) -> int:
        return self.__order_delay

    @property
    def process_order_ticket(self) -> int:
        return self.__process_order_ticket

    @process_order_ticket.setter
    def process_order_ticket(self, ticket: int):
        self.__process_order_ticket = ticket

    def __init__(self) -> None:
        pass

    def add_orderevent_result(self, result: OrderSendEventResult):
        self.__order_list.append(result)

    def add_order_retry_count(self):
        self.__order_retry_count = self.__order_retry_count + 1

    def clear_order_retry_count(self):
        self.__order_retry_count = 0
