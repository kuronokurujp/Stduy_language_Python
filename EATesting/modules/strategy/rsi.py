#!/usr/bin/env python
import backtrader as bt
import numpy as np

import modules.strategy.backtrader.backtrader_strategy as strategy
import modules.strategy.backtrader.backtrader_analyzer as analyzer
import modules.strategy.interface.analyzer_interface as analyzer_interface

import modules.common


# カスタムアナライザーの定義
class RSIAnalyzer(analyzer.BaseAnalyzer):
    def __init__(self):
        self.rsi_min_values = []
        self.rsi_max_values = []

    def next(self):
        super().next()

        self.rsi_min_values.append(self.strategy.rsi_min[0])
        self.rsi_max_values.append(self.strategy.rsi_max[0])

    # インジケーターグループを取得
    @property
    def ind_dict(self) -> dict[str, np.ndarray]:
        return {
            "rsi_min": np.array(self.rsi_min_values),
            "rsi_max": np.array(self.rsi_max_values),
        }


# Backtraderシステムに依存した作るになっている
# しかし現時点でBacktrader以外のを使う予定はないので分離対応はこれ以上しない
# RSIを使用したストラテジーの定義
class RSIStrategy(strategy.BaseStrategy):
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

    @staticmethod
    def add_strategy(cerebro, params):
        # ストラテジーをCerebroに追加
        cerebro.addstrategy(
            RSIStrategy,
            rsi_min_period=int(params["rsi_min_period"]),
            rsi_max_period=int(params["rsi_max_period"]),
            rsi_blank_entry=float(params["rsi_blank_entry"]),
            close_type=str(params["close_type"]),
            close_before_val=float(params["close_before_val"]),
            close_after_val=float(params["close_after_val"]),
        )

    @staticmethod
    def analyzer_class() -> type[analyzer_interface.IAnalyzer]:
        return RSIAnalyzer

    @staticmethod
    def add_opt(cerebro, params) -> int:
        items = params["rsi_min_period"].split(",")
        rsi_min_period: range = range(int(items[0]), int(items[1]), int(items[2]))

        items = params["rsi_max_period"].split(",")
        rsi_max_period: range = range(int(items[0]), int(items[1]), int(items[2]))

        items = params["rsi_blank_entry"].split(",")
        rsi_blank_entry = modules.common.frange(
            float(items[0]), float(items[1]), float(items[2])
        )

        close_type = params["close_types"].split(",")

        items = params["close_before_val"].split(",")
        close_before_val = modules.common.frange(
            float(items[0]), float(items[1]), float(items[2])
        )

        items = params["close_before_val"].split(",")
        close_after_val = modules.common.frange(
            float(items[0]), float(items[1]), float(items[2])
        )

        # 進捗管理インスタンスを作成
        total_combinations = (
            len(rsi_min_period)
            * len(rsi_max_period)
            * len(rsi_blank_entry)
            * len(close_type)
            * len(close_before_val)
            * len(close_after_val)
        )

        # ストラテジーの最適化を追加
        cerebro.optstrategy(
            RSIStrategy,
            rsi_min_period=rsi_min_period,
            rsi_max_period=rsi_max_period,
            rsi_blank_entry=rsi_blank_entry,
            close_type=close_type,
            close_before_val=close_before_val,
            close_after_val=close_after_val,
            printlog=False,
            optimizing=True,
        )

        return total_combinations

    def __init__(self):
        super().__init__(b_opt=self.params.optimizing, b_log=self.params.printlog)

        # パラメータが不正かチェック
        if self.params.rsi_min_period <= 1:
            raise ValueError(
                f"RSIの短期値が{self.params.rsi_min_period}で不適切なのでテストできない"
            )

        if self.params.rsi_max_period <= 1:
            raise ValueError(
                f"RSIの長期値が{self.params.rsi_max_period}で不適切なのでテストできない"
            )

        if self.params.rsi_blank_entry <= 0:
            raise ValueError(
                f"RSIのブランク値が{self.params.rsi_blank_entry}で不適切なのでテストできない"
            )

        self.rsi_min = bt.indicators.RSI(
            self.data.close, period=self.params.rsi_min_period
        )
        self.rsi_max = bt.indicators.RSI(
            self.data.close, period=self.params.rsi_max_period
        )

    def next(self):
        super().next()

        rsi_min_value = self.rsi_min[0]
        rsi_max_value = self.rsi_max[0]

        # パラメータによってキャンセルする
        # クロス後の決済なのにクロス前の値が入っているのはおかしい
        # クロス後の決済の場合はクロス後の値のみが入っているのが望ましい
        if self.params.close_type == "クロス後":
            if self.params.close_after_val == 0.0:
                self._cancel("Cancle: クロス後決済モードなのにクロス後値が入っていない")
            elif self.params.close_before_val != 0.0:
                self._cancel(
                    "Cancle: クロス後決済モードなのにクロス前値が入っていたから"
                )
        elif self.params.close_type == "クロス前":
            if self.params.close_before_val == 0.0:
                self._cancel("Cancle: クロス前決済モードなのにクロス前値が入っていない")
            elif self.params.close_after_val != 0.0:
                self._cancel(
                    "Cancle: クロス前決済モードなのにクロス後値が入っていたから"
                )
        else:
            if self.params.close_after_val != 0 or self.params.close_before_val != 0.0:
                self._cancel(
                    "Cancle: クロス決済モードなのにクロス後かクロス前の関連値が入っていたから"
                )

        # not in the market
        if not self.position:
            if (
                rsi_min_value < rsi_max_value
                and (rsi_max_value - rsi_min_value) >= self.params.rsi_blank_entry
            ):
                self.order = self._buy()
            elif (
                rsi_min_value > rsi_max_value
                and (rsi_min_value - rsi_max_value) >= self.params.rsi_blank_entry
            ):
                self.order = self._sell()

        elif self.position:
            if self.is_buy_status:
                if self.params.close_type == "クロス後":
                    if (
                        abs(rsi_min_value - rsi_max_value)
                        >= self.params.close_after_val
                        and rsi_min_value > rsi_max_value
                    ):
                        self.order = self._close(msg="cross after")

                elif self.params.close_type == "クロス前":
                    if (
                        abs(rsi_min_value - rsi_max_value)
                        <= self.params.close_before_val
                        and rsi_min_value <= rsi_max_value
                    ):
                        self.order = self._close(msg="cross before")

                elif rsi_min_value > rsi_max_value:
                    self.order = self._close(msg="cross after")

            elif self.is_sell_status:
                if self.params.close_type == "クロス後":
                    if (
                        abs(rsi_min_value - rsi_max_value)
                        >= self.params.close_after_val
                        and rsi_min_value < rsi_max_value
                    ):
                        self.order = self._close(msg="cross after")

                elif self.params.close_type == "クロス前":
                    if (
                        abs(rsi_min_value - rsi_max_value)
                        <= self.params.close_before_val
                        and rsi_min_value >= rsi_max_value
                    ):
                        self.order = self._close(msg="cross before")

                elif rsi_min_value < rsi_max_value:
                    self.order = self._close(msg="cross before")
