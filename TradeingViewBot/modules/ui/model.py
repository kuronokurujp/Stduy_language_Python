#!/usr/bin/env python
import datetime


# TODO: ツールのモデル
class Model(object):
    __title: str = "トレーディングビューボット"
    __size: tuple[int, int] = (512, 364)

    __trans_items: list = list()
    __strategy_items: list = list()
    __history_items: list = list()

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

    @property
    def account_history_items(self) -> list:
        return self.__history_items

    # TODO: EAの戦略アイテムを追加
    def add_strategy_item(self, item):
        self.__strategy_items.append(item)

    # TODO: 取引アイテムを追加
    def add_transaction_item(self, item):
        self.__trans_items.append(item)

    # TODO: 口座履歴にアイテムを追加
    def add_account_history_item(self, item):
        self.__history_items.append(item)

    # TODO: 指定チケットの取引データを削除
    def remove_transsaction_item_by_tikcet(self, ticket: int):
        for i in range(len(self.__trans_items)):
            item = self.__trans_items[i]
            if item[0] == ticket:
                self.__trans_items.pop(i)
                break

    # TODO:チケットから取引データを取得
    def transaction_item(self, tikcet: int):
        result = filter(lambda items: items[0] == tikcet, self.__trans_items)
        if result is None:
            return None

        return list(result)[0]
