#!/usr/bin/env python
import backtrader as bt


# ロジックの基本クラス
class LogicBase:
    def addstrategy(self, cerebro: bt.cerebro):
        pass

    def show(self, results):
        pass
