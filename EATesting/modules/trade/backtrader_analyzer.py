#!/usr/bin/env python
import backtrader as bt


# カスタムアナライザーの定義
class BaseAnalyzer(bt.Analyzer):
    def __init__(self):
        self.dates = []
        self.buy_signals = []
        self.sell_signals = []
        self.close_signals = []
        self.prices = []

    def next(self):
        self.dates.append(self.strategy.data.datetime.datetime(0))
        self.prices.append(self.strategy.data.close[0])

        # if self.strategy.buy_signals:
        self.buy_signals.append(self.strategy.buy_signal)

        # if self.strategy.sell_signals:
        self.sell_signals.append(self.strategy.sell_signal)

        # if self.strategy.close_signals:
        self.close_signals.append(self.strategy.close_signal)

    def get_analysis(self):
        return {
            "dates": self.dates,
            "prices": self.prices,
            "buy_signals": self.buy_signals,
            "sell_signals": self.sell_signals,
            "close_signals": self.close_signals,
        }
