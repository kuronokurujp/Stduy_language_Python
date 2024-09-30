#!/usr/bin/env python
import backtrader as bt
import numpy as np
import modules.trade.interface.analyzer_interface as analyzer_interface


# バックトレード用の基本解析クラス
class BaseAnalyzer(analyzer_interface.IAnalyzer, bt.Analyzer):
    dates: list = []
    buy_signals: list = []
    sell_signals: list = []
    close_signals: list = []
    # prices: list = []
    closes: list = []
    opens: list = []
    highs: list = []
    lows: list = []

    def __init__(self):
        pass

    @property
    def date_values(self) -> np.ndarray:
        return np.array(self.dates)

    @property
    def close_values(self) -> np.ndarray:
        return np.array(self.closes)

    @property
    def high_values(self) -> np.ndarray:
        return np.array(self.highs)

    @property
    def low_values(self) -> np.ndarray:
        return np.array(self.lows)

    @property
    def open_values(self) -> np.ndarray:
        return np.array(self.opens)

    def next(self):
        st = self.strategy
        data = st.data

        self.dates.append(data.datetime.datetime(0))
        self.closes.append(data.close[0])
        self.opens.append(data.open[0])
        self.highs.append(data.high[0])
        self.lows.append(data.low[0])

        # if self.strategy.buy_signals:
        self.buy_signals.append(st.buy_signal)

        # if self.strategy.sell_signals:
        self.sell_signals.append(st.sell_signal)

        # if self.strategy.close_signals:
        self.close_signals.append(st.close_signal)

    def get_analysis(self) -> dict:
        return {
            "dates": self.dates,
            "close": self.closes,
            "high": self.highs,
            "low": self.lows,
            "open": self.opens,
            "buy_signals": self.buy_signals,
            "sell_signals": self.sell_signals,
            "close_signals": self.close_signals,
        }
