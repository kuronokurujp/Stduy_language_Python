#!/usr/bin/env python
import datetime
from modules.broker.event import (
    IOrderSendEvent,
)
import modules.broker.const as bk_const


# TODO: デモでの新規注文イベント
class OrderSendEvent(IOrderSendEvent):
    async def run(self) -> bool:
        # TODO: 即時成功で良い
        order_cmd_msg: str = ""
        if self.result.cmd == bk_const.CMD_ORDER_BUY:
            order_cmd_msg = "新規買い"
        elif self.result.cmd == bk_const.CMD_ORDER_SELL:
            order_cmd_msg = "新規売り"
        else:
            return False

        # TODO: 注文に成功したので取引時間を設定
        dt_now = datetime.datetime.now()
        self.result.date_time = dt_now.strftime("%Y年%m月%d日 %H:%M:%S")

        self.result.set(
            b_success=True,
            err_msg="",
            ok_msg="{}が成功, 建玉は{}".format(order_cmd_msg, self.result.volume),
        )
        return True
