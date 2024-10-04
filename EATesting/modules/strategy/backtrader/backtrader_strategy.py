#!/usr/bin/env python
import backtrader as bt
import numpy as np
import gc


# バックトレードを使った基本ストラテジー
class BaseStrategy(bt.Strategy):
    __b_opt: bool = False
    __b_log: bool = False
    __b_buy: bool = True
    __b_sell: bool = False
    __order = None
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
        return self.__b_buy

    @property
    def is_sell_status(self) -> bool:
        return self.__b_sell

    def __init__(self, b_opt: bool, b_log: bool):
        self.__b_opt = b_opt
        self.__b_log = b_log

        self.p.value = 0
        self.p.trades = 0
        self.data_close = self.datas[0].close

        # 最適化中かどうかを判別
        if self.__b_opt is False:

            self.trade_log = []  # 取引履歴を記録
            self.rsi_values = []  # RSIの値を保存するリスト

    # ローソク足更新のたびに呼ばれる
    def next(self):
        pass

    # 戦略取引が終了した時に呼ばれる
    def stop(self):
        self._log("資金: %.2f" % (self.broker.getvalue()), doprint=not self.__b_opt)
        self.p.value = self.broker.getvalue()

        if self.__b_opt:
            gc.collect()

    # トレード通知
    def notify_trade(self, trade):
        # クローズのトレードか
        if trade.isclosed:
            if self.__b_log:
                self._log(
                    "クローズ: 取引利益, 総額(%.2f), 純額(%.2f)"
                    % (trade.pnl, trade.pnlcomm),
                    doprint=True,
                )

            self.p.trades = self.p.trades + 1

    # 注文通知
    def notify_order(self, order):
        # 注文の状態が送信済み or 受理済みの場合
        if order.status in [order.Submitted, order.Accepted]:
            return

        # 注文が完了
        if order.status in [order.Completed]:
            # 注文情報を取得
            order_type: str = order.info.get("name", "unknown")

            # 買い新規と売り転売
            if order.isbuy():
                if order_type == "entry":
                    self._log("買新規", doprint=self.params.printlog)
                elif order_type == "exit":
                    self._log("売転売", doprint=self.params.printlog)

                self._log(
                    "買い約定: 取引数量(%.2f), 価格(%.2f), 取引額(%.2f), 手数料(%.2f)"
                    % (
                        order.executed.size,
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

            # 売り建てと買い転売
            elif order.issell():
                if order_type == "entry":
                    self._log("売新規", doprint=self.params.printlog)
                elif order_type == "exit":
                    self._log("買転売", doprint=self.params.printlog)

                self._log(
                    "売り約定: 取引数量(%.2f), 価格(%.2f), 取引額(%.2f), 手数料(%.2f)"
                    % (
                        order.executed.size,
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

        # 注文状態がキャンセル済み
        elif order.status in [order.Canceled]:
            self._log("注文キャンセル", doprint=self.__b_log)
        # 証拠金不足
        elif order.status in [order.Margin]:
            self._log("注文証拠金不足", doprint=self.__b_log)
        # 拒否済み
        elif order.status in [order.Rejected]:
            self._log("注文の拒否", doprint=self.__b_log)

        # Write down: no pending order
        self.__order = None

    def _buy(self):
        self.__order = self.buy()
        # 注文かどうかの識別情報を設定
        self.__order.addinfo(name="entry")

        self.__b_buy = True
        self.__b_sell = False

        return self.__order

    def _sell(self):
        self.__order = self.sell()
        # 注文かどうかの識別情報を設定
        self.__order.addinfo(name="entry")

        self.__b_buy = False
        self.__b_sell = True

        return self.__order

    def _close(self, msg: str = None):
        self.__order = self.close()
        # 決済かどうかの識別情報を設定
        self.__order.addinfo(name="exit")

        return self.__order

    def _cancel(self, msg: str):
        if self.__b_opt is False:
            self._log(msg, doprint=True)

        self.env.runstop()

    def _log(self, txt, dt=None, doprint=False):
        """Logging function fot this strategy"""
        if doprint:
            dt = dt or self.datas[0].datetime.datetime(0)
            print("%s, %s" % (dt.isoformat(), txt))
