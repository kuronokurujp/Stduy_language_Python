#!/usr/bin/env python
import backtrader as bt
import numpy as np
import gc


# バックトレードを使った基本ストラテジー
class BaseStrategy(bt.Strategy):
    __b_opt: bool = False
    __b_log: bool = False
    bBuy: bool = True
    bSell: bool = False
    order = None
    buyprice = None
    buycomm = None

    @property
    def is_opt(self) -> bool:
        return self.__b_opt

    @property
    def is_log(self) -> bool:
        return self.__b_log

    @property
    def is_buy_status(self) -> bool:
        return self.bBuy

    @property
    def is_sell_status(self) -> bool:
        return self.bSell

    def __init__(self, b_opt: bool, b_log: bool):
        self.__b_opt = b_opt
        self.__b_log = b_log

        self.p.value = 0
        self.p.trades = 0
        self.data_close = self.datas[0].close

        # 最適化中かどうかを判別
        if self.__b_opt is False:
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

    # ローソク足更新のたびに呼ばれる
    def next(self):
        self.dates.append(self.datas[0].datetime.datetime(0))
        self.close_values.append(self.data_close[0])
        self.open_values.append(self.data_open[0])
        self.high_values.append(self.data_high[0])
        self.low_values.append(self.data_low[0])

        if not self.__b_opt:
            self.buy_signal = np.nan
            self.sell_signal = np.nan
            self.close_signal = np.nan

    # 戦略取引が終了した時に呼ばれる
    def stop(self):
        self._log(
            "Ending Value %.2f" % (self.broker.getvalue()), doprint=not self.__b_opt
        )
        self.p.value = self.broker.getvalue()

        if self.__b_opt:
            gc.collect()

    # トレード通知
    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        if self.__b_log:
            self._log(
                "OPERATION PROFIT, GROSS %.2f, NET %.2f" % (trade.pnl, trade.pnlcomm),
                doprint=True,
            )

        self.p.trades = self.p.trades + 1

    # 注文通知
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self._log(
                    "BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f"
                    % (
                        order.executed.price,
                        order.executed.value,
                        order.executed.comm,
                    ),
                    doprint=self.params.printlog,
                )
                self.trade_log.append(
                    {
                        "datetime": self.datas[0].datetime.datetime(0),
                        "price": self.data_close[0],
                        "action": "buy",
                    }
                )

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm

            else:  # Sell
                self._log(
                    "SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f"
                    % (
                        order.executed.price,
                        order.executed.value,
                        order.executed.comm,
                    ),
                    doprint=self.__b_log,
                )
                self.trade_log.append(
                    {
                        "datetime": self.datas[0].datetime.datetime(0),
                        "price": self.data_close[0],
                        "action": "sell",
                    }
                )

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self._log("Order Canceled/Margin/Rejected", doprint=self.__b_log)

        # Write down: no pending order
        self.order = None

    def _buy(self):
        self.order = self.buy()
        if not self.__b_opt:
            self.buy_signal = self.data.close[0]

        self.bBuy = True
        self.bSell = False

        if self.__b_log:
            self._log(f"BUY ORDER: {self.data.datetime.date(0)}", doprint=True)

        return self.order

    def _sell(self):
        self.order = self.sell()
        if not self.__b_opt:
            self.sell_signal = self.data.close[0]

        self.bBuy = False
        self.bSell = True
        if self.__b_log:
            self._log(
                f"SELL ORDER: {self.data.datetime.date(0)}",
                doprint=True,
            )

        return self.order

    def _close(self, msg: str = None):
        self.order = self.close()

        if not self.__b_opt:
            self.close_signal = self.data.close[0]

        if msg and self.__b_log:
            self._log(
                f"CLOSE ORDER ({msg}): {self.data.datetime.date(0)}", doprint=True
            )

        return self.order

    def __stop(self, msg: str):
        if self.__b_opt is False:
            self._log(msg, doprint=True)

        self.env.runstop()

    def _log(self, txt, dt=None, doprint=False):
        """Logging function fot this strategy"""
        if doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print("%s, %s" % (dt.isoformat(), txt))
