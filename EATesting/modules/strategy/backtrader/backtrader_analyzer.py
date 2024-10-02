#!/usr/bin/env python
import backtrader as bt
import numpy as np
import modules.strategy.interface.analyzer_interface as analyzer_interface
import modules.strategy.backtrader.backtrader_strategy as bk_st


# バックトレード用の基本解析クラス
class BaseAnalyzer(analyzer_interface.IAnalyzer, bt.Analyzer):
    __dates: list = []
    __order_buy_signals: list = []
    __order_sell_signals: list = []
    __close_buy_signals: list = []
    __close_sell_signals: list = []
    __closes: list = []
    __opens: list = []
    __highs: list = []
    __lows: list = []
    __buy_signal = np.nan
    __sell_signal = np.nan

    def __init__(self):
        pass

    @property
    def date_values(self) -> np.ndarray:
        return np.array(self.__dates)

    @property
    def close_values(self) -> np.ndarray:
        return np.array(self.__closes)

    @property
    def high_values(self) -> np.ndarray:
        return np.array(self.__highs)

    @property
    def low_values(self) -> np.ndarray:
        return np.array(self.__lows)

    @property
    def open_values(self) -> np.ndarray:
        return np.array(self.__opens)

    @property
    def order_buy_signals(self) -> np.ndarray:
        return np.array(self.__order_buy_signals)

    @property
    def order_sell_signals(self) -> np.ndarray:
        return np.array(self.__order_sell_signals)

    @property
    def close_buy_signals(self) -> np.ndarray:
        return np.array(self.__close_buy_signals)

    @property
    def close_sell_signals(self) -> np.ndarray:
        return np.array(self.__close_sell_signals)

    def next(self):
        st: bk_st.BaseStrategy = self.strategy
        data = st.data
        date = data.datetime.datetime(0)

        self.__dates.append(date)
        self.__closes.append(data.close[0])
        self.__opens.append(data.open[0])
        self.__highs.append(data.high[0])
        self.__lows.append(data.low[0])

        # nextメソッドでシグナルを追加しないと注文時間位置とずれがおきてしまう
        if not np.isnan(self.__buy_signal):
            self.__order_buy_signals.append(self.__buy_signal)
        else:
            self.__order_buy_signals.append(np.nan)

        self.__order_sell_signals.append(st.sell_signal)
        self.__close_buy_signals.append(st.close_buy_signal)
        self.__close_sell_signals.append(st.close_sell_signal)

        self.__buy_signal = np.nan
        self.__sell_signal = np.nan

    # 注文通知
    def notify_order(self, order):
        # 注文の状態が送信済み or 受理済みの場合
        if order.status in [order.Submitted, order.Accepted]:
            return

        # 注文が完了
        if order.status in [order.Completed]:
            # 買いで注文
            # 売り建てして売り転売した場合も呼ばれる？
            if order.isbuy():
                self.__buy_signal = order.executed.price
            # 売り建てと買い転売でよばれるぽい
            elif order.issell():
                self.__sell_signal = order.executed.price
