#!/usr/bin/env python
import modules.excel.controller
import modules.rrss.model
from modules.log.logger import AppLogger
import asyncio


# TODO: 楽天RSSの売買制御クラス
class Controller(modules.excel.controller.Controller):
    def __init__(
        self, model: modules.rrss.model.Model, logger: AppLogger = None
    ) -> None:
        super().__init__(model=model, logger=logger)

    async def __apply_order_buy(self, num: int, delay):
        await asyncio.sleep(delay=delay)

        rrss_model: modules.rrss.model.Model = self.__model
        val: int = int(self.__book["main"].range(rrss_model.__pos_buy_cell).value)

        self.__book["main"].range(rrss_model.__pos_buy_cell).value = val + num
        self.__book["main"].range(rrss_model.__order_flg_buy_cell).value = 0

        return

    async def __apply_order_sell(self, num: int, delay):
        await asyncio.sleep(delay=delay)

        rrss_model: modules.rrss.model.Model = self.__model
        val: int = int(self.__book["main"].range(rrss_model.__pos_sell_cell).value)

        self.__book["main"].range(rrss_model.__pos_sell_cell).value = val + num
        self.__book["main"].range(rrss_model.__order_flg_sell_cell).value = 0

        return

    async def __apply_close_buy(self, delay):
        await asyncio.sleep(delay=delay)

        rrss_model: modules.rrss.model.Model = self.__model
        self.__book["main"].range(rrss_model.__pos_buy_cell).value = 0
        return

    async def __apply_close_sell(self, delay):
        await asyncio.sleep(delay=delay)

        rrss_model: modules.rrss.model.Model = self.__model
        self.__book["main"].range(rrss_model.__pos_buy_cell).value = 0
        return

    # TODO: 売買のオーダーをする
    def orderBuy(self):
        rrss_model: modules.rrss.model.Model = self.__model
        self.__book["main"].range(rrss_model.__order_flg_buy_cell).value = 1

        asyncio.run(self.__apply_order_buy(1, 10))

    def orderSell(self):
        rrss_model: modules.rrss.model.Model = self.__model
        self.__book["main"].range(rrss_model.__order_flg_sell_cell).value = 1
        self.__book["main"].range(rrss_model.__pos_sell_cell).value = 0

        asyncio.run(self.__apply_order_sell(1, 10))

    # TODO: 売買のクローズをする
    def close_buy(self):
        rrss_model: modules.rrss.model.Model = self.__model
        self.__book["main"].range(rrss_model.__close_flg_buy_cell).value = 1

        asyncio.run(self.__apply_close_buy(10))

    def close_sell(self):
        rrss_model: modules.rrss.model.Model = self.__model
        self.__book["main"].range(rrss_model.__close_flg_sell_cell).value = 1

        asyncio.run(self.__apply_close_sell(10))

    def all_close(self):
        self.close_buy()
        self.close_sell()
