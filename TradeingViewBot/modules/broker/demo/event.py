#!/usr/bin/env python
import datetime
from modules.broker.event import (
    IOrderSendEvent,
    ICloseSendEvent,
)
import modules.broker.const as bk_const


# TODO: デモでの新規注文イベント
class OrderSendEvent(IOrderSendEvent):
    async def run(self) -> int:
        # TODO: 即時成功で良い
        if self.result.cmd == bk_const.CMD_ORDER_BUY:
            pass
        elif self.result.cmd == bk_const.CMD_ORDER_SELL:
            pass
        else:
            return bk_const.ERR_CODE_MISS_CMD_PARAM

        # TODO: 注文に成功したので取引時間を設定
        dt_now = datetime.datetime.now()
        self.result.date_time = dt_now.strftime("%Y年%m月%d日 %H:%M:%S")

        return 0


# TODO: 決済取引イベント
class CloseSendEvent(ICloseSendEvent):
    async def run(self) -> int:
        # TODO: 速攻で決済

        dt_now = datetime.datetime.now()
        self.result.date_time = dt_now.strftime("%Y年%m月%d日 %H:%M:%S")
        return 0
