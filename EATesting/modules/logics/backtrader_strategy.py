#!/usr/bin/env python
import backtrader as bt
import numpy as np


class BaseStrategy(bt.Strategy):
    b_opt: bool = False
    bBuy: bool = True
    bSell: bool = False

    def __init__(self, b_opt: bool):
        self.b_opt = b_opt

        self.data_close = self.datas[0].close

        # 最適化中かどうかを判別
        if b_opt is False:
            self.buy_signals = []
            self.sell_signals = []
            self.close_signals = []
            self.buy_signal = np.nan
            self.sell_signal = np.nan
            self.close_signal = np.nan
            self.trade_log = []  # 取引履歴を記録
            self.rsi_values = []  # RSIの値を保存するリスト
            self.dates = []  # 日時を保存するリスト
            self.close_values = []  # 終値を保存するリスト
            self.open_values = []  # 終値を保存するリスト
            self.high_values = []  # 終値を保存するリスト
            self.low_values = []  # 終値を保存するリスト

    def next(self):
        self.dates.append(self.datas[0].datetime.datetime(0))
        self.close_values.append(self.data_close[0])
        self.open_values.append(self.data_open[0])
        self.high_values.append(self.data_high[0])
        self.low_values.append(self.data_low[0])

        if not self.b_opt:
            self.buy_signal = np.nan
            self.sell_signal = np.nan
            self.close_signal = np.nan

    def _buy(self, b_log: bool = False):
        order = self.buy()
        if not self.b_opt:
            self.buy_signal = self.data.close[0]

        self.bBuy = True
        self.bSell = False

        if b_log:
            self._log(f"BUY ORDER: {self.data.datetime.date(0)}", doprint=True)

        return order

    def _sell(self, b_log: bool = False):
        order = self.sell()
        if not self.b_opt:
            self.sell_signal = self.data.close[0]

        self.bBuy = False
        self.bSell = True
        if b_log:
            self._log(
                f"SELL ORDER: {self.data.datetime.date(0)}",
                doprint=True,
            )

        return order

    def _close(self, msg: str = None, b_log: bool = False):
        order = self.close()
        if not self.b_opt:
            self.close_signal = self.data.close[0]

        if msg and b_log:
            self._log(
                f"CLOSE ORDER ({msg}): {self.data.datetime.date(0)}",
                doprint=True
            )

        return order

    def __stop(self, msg: str):
        if self.b_opt is False:
            self._log(msg, doprint=True)

        self.env.runstop()

    def _log(self, txt, dt=None, doprint=False):
        """Logging function fot this strategy"""
        if doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print("%s, %s" % (dt.isoformat(), txt))
