#!/usr/bin/env python
import datetime


# TODO: ツールのモデル
class Model(object):
    __title: str = "トレーディングビューボット"
    __size: tuple[int, int] = (512, 364)

    __trans_items: list = list()
    __strategy_items: list = list()

    __b_debug: bool = False

    def __init__(self, b_debug: bool) -> None:
        self.__b_debug = b_debug

    @property
    def title(self) -> str:
        return self.__title

    @property
    def size(self) -> tuple[int, int]:
        return self.__size

    @property
    def debug(self) -> bool:
        return self.__b_debug

    @property
    def strategy_items(self) -> list:
        return self.__strategy_items

    @property
    def transaction_items(self) -> list:
        return self.__trans_items

    # TODO: EAの戦略アイテムを追加
    def add_strategy_item(self, item):
        self.__strategy_items.append(item)

    # TODO: 取引アイテムを追加
    def add_transaction_item(self, item):
        self.__trans_items.append(item)
