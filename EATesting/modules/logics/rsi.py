#!/usr/bin/env python
import backtrader as bt
import gc
import numpy as np


# RSIを使用したストラテジーの定義
class RSIStrategy(bt.Strategy):
    params = (
        ("rsi_min_period", 7),
        ("rsi_max_period", 14),
        ("rsi_blank_entry", 10.0),
        ("close_type", "クロス"),  # 'クロス', 'クロス前', 'クロス後'
        ("close_before_val", 0.0),
        ("close_after_val", 0.0),
        ("printlog", True),
        ("optimizing", False),
    )

    def log(self, txt, dt=None, doprint=False):
        """Logging function fot this strategy"""
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print("%s, %s" % (dt.isoformat(), txt))

    def __init__(self):

        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.p.value = 0
        self.p.trades = 0

        self.data_close = self.datas[0].close

        self.rsi_min = bt.indicators.RSI(
            self.data.close, period=self.params.rsi_min_period
        )
        self.rsi_max = bt.indicators.RSI(
            self.data.close, period=self.params.rsi_max_period
        )

        self.bBuy = False
        self.bSell = False

        # 最適化中かどうかを判別
        self.is_optimizing = self.params.optimizing
        if not self.is_optimizing:
            self.buy_signals = []
            self.sell_signals = []
            self.close_signals = []
            self.buy_signal = np.nan
            self.sell_signal = np.nan
            self.close_signal = np.nan

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    "BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f"
                    % (
                        order.executed.price,
                        order.executed.value,
                        order.executed.comm,
                    )
                )

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm

            else:  # Sell
                self.log(
                    "SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f"
                    % (
                        order.executed.price,
                        order.executed.value,
                        order.executed.comm,
                    )
                )

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("Order Canceled/Margin/Rejected")

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log("OPERATION PROFIT, GROSS %.2f, NET %.2f" % (trade.pnl, trade.pnlcomm))
        self.p.trades = self.p.trades + 1

    def stop(self):
        if not self.is_optimizing:
            self.log("Ending Value %.2f" % (self.broker.getvalue()), doprint=True)
        else:
            self.p.value = self.broker.getvalue()
            gc.collect()

    def next(self):
        rsi_min_value = self.rsi_min[0]
        rsi_max_value = self.rsi_max[0]

        # パラメータによってキャンセルする
        # クロス後の決済なのにクロス前の値が入っているのはおかしい
        # クロス後の決済の場合はクロス後の値のみが入っているのが望ましい
        if self.params.close_type == "クロス後":
            if self.params.close_after_val == 0.0:
                self.log(
                    "Cancle: クロス後決済モードなのにクロス後値が入っていない",
                    None,
                    True,
                )
                self.env.runstop()
            elif self.params.close_before_val != 0.0:
                self.log(
                    "Cancle: クロス後決済モードなのにクロス前値が入っていたから",
                    None,
                    True,
                )
                self.env.runstop()
        elif self.params.close_type == "クロス前":
            if self.params.close_before_val == 0.0:
                self.log(
                    "Cancle: クロス前決済モードなのにクロス前値が入っていない",
                    None,
                    True,
                )
                self.env.runstop()
            elif self.params.close_after_val != 0.0:
                self.log(
                    "Cancle: クロス前決済モードなのにクロス後値が入っていたから",
                    None,
                    True,
                )
                self.env.runstop()
        else:
            if self.params.close_after_val != 0 or self.params.close_before_val != 0.0:
                self.log(
                    "Cancle: クロス決済モードなのにクロス後かクロス前の決済値が入っていたから",
                    None,
                    True,
                )
                self.env.runstop()

        if not self.is_optimizing:
            self.buy_signal = np.nan
            self.sell_signal = np.nan
            self.close_signal = np.nan

        # not in the market
        if not self.position:
            if (
                rsi_min_value < rsi_max_value
                and (rsi_max_value - rsi_min_value) >= self.params.rsi_blank_entry
            ):
                self.order = self.buy()
                if not self.is_optimizing:
                    self.buy_signal = self.data.close[0]
                self.bBuy = True
                self.bSell = False
                self.log(f"BUY ORDER: {self.data.datetime.date(0)}")

            elif (
                rsi_min_value > rsi_max_value
                and (rsi_min_value - rsi_max_value) >= self.params.rsi_blank_entry
            ):
                self.order = self.sell()
                if not self.is_optimizing:
                    self.sell_signal = self.data.close[0]
                self.bBuy = False
                self.bSell = True
                self.log(f"SELL ORDER: {self.data.datetime.date(0)}")

        elif self.position:
            if self.bBuy:
                if self.params.close_type == "クロス後":
                    if (
                        abs(rsi_min_value - rsi_max_value)
                        >= self.params.close_after_val
                        and rsi_min_value > rsi_max_value
                    ):
                        self.order = self.close()
                        if not self.is_optimizing:
                            self.close_signal = self.data.close[0]
                        self.log(
                            f"CLOSE ORDER (cross after): {self.data.datetime.date(0)}"
                        )
                elif self.params.close_type == "クロス前":
                    if (
                        abs(rsi_min_value - rsi_max_value)
                        <= self.params.close_before_val
                        and rsi_min_value <= rsi_max_value
                    ):
                        self.order = self.close()
                        if not self.is_optimizing:
                            self.close_signal = self.data.close[0]
                        self.log(
                            f"CLOSE ORDER (cross before): {self.data.datetime.date(0)}"
                        )
                elif rsi_min_value > rsi_max_value:
                    self.order = self.close()
                    if not self.is_optimizing:
                        self.close_signal = self.data.close[0]
                    self.log(f"CLOSE ORDER (cross after): {self.data.datetime.date(0)}")
            elif self.bSell:
                if self.params.close_type == "クロス後":
                    if (
                        abs(rsi_min_value - rsi_max_value)
                        >= self.params.close_after_val
                        and rsi_min_value < rsi_max_value
                    ):
                        self.order = self.close()
                        if not self.is_optimizing:
                            self.close_signal = self.data.close[0]
                        self.log(
                            f"CLOSE ORDER (cross after): {self.data.datetime.date(0)}"
                        )
                elif self.params.close_type == "クロス前":
                    if (
                        abs(rsi_min_value - rsi_max_value)
                        <= self.params.close_before_val
                        and rsi_min_value >= rsi_max_value
                    ):
                        self.order = self.close()
                        if not self.is_optimizing:
                            self.close_signal = self.data.close[0]
                        self.log(
                            f"CLOSE ORDER (cross before): {self.data.datetime.date(0)}"
                        )
                elif rsi_min_value < rsi_max_value:
                    self.order = self.close()
                    if not self.is_optimizing:
                        self.close_signal = self.data.close[0]
                    self.log(
                        f"CLOSE ORDER (cross before): {self.data.datetime.date(0)}"
                    )
