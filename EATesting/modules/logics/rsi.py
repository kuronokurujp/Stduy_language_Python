#!/usr/bin/env python
import backtrader as bt
import gc
import numpy as np
import modules.logics.logic
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# カスタムアナライザーの定義
class RSIAnalyzer(bt.Analyzer):
    def __init__(self):
        self.rsi_min_values = []
        self.rsi_max_values = []
        self.dates = []
        self.buy_signals = []
        self.sell_signals = []
        self.close_signals = []
        self.prices = []

    def next(self):
        rsi_min_value = self.strategy.rsi_min[0]
        rsi_max_value = self.strategy.rsi_max[0]

        self.rsi_min_values.append(rsi_min_value)
        self.rsi_max_values.append(rsi_max_value)
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
            "rsi_min_values": self.rsi_min_values,
            "rsi_max_values": self.rsi_max_values,
            "buy_signals": self.buy_signals,
            "sell_signals": self.sell_signals,
            "close_signals": self.close_signals,
        }


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
        self.log(
            "Ending Value %.2f" % (self.broker.getvalue()),
            doprint=not self.is_optimizing,
        )
        self.p.value = self.broker.getvalue()

        if self.is_optimizing:
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
                    doprint=not self.is_optimizing,
                )
                self.env.runstop()
            elif self.params.close_before_val != 0.0:
                self.log(
                    "Cancle: クロス後決済モードなのにクロス前値が入っていたから",
                    None,
                    doprint=not self.is_optimizing,
                )
                self.env.runstop()
        elif self.params.close_type == "クロス前":
            if self.params.close_before_val == 0.0:
                self.log(
                    "Cancle: クロス前決済モードなのにクロス前値が入っていない",
                    None,
                    doprint=not self.is_optimizing,
                )
                self.env.runstop()
            elif self.params.close_after_val != 0.0:
                self.log(
                    "Cancle: クロス前決済モードなのにクロス後値が入っていたから",
                    None,
                    doprint=not self.is_optimizing,
                )
                self.env.runstop()
        else:
            if self.params.close_after_val != 0 or self.params.close_before_val != 0.0:
                self.log(
                    "Cancle: クロス決済モードなのにクロス後かクロス前の決済値が入っていたから",
                    None,
                    doprint=not self.is_optimizing,
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


class RSILogic(modules.logics.logic.LogicBase):

    def addstrategy(self, cerebro: bt.cerebro):
        # ストラテジーをCerebroに追加
        cerebro.addstrategy(
            RSIStrategy,
            rsi_min_period=8,
            rsi_max_period=14,
            rsi_blank_entry=10,
            close_type="クロス前",
            close_before_val=10.0,
            close_after_val=0.0,
        )

        # カスタムアナライザーを追加
        cerebro.addanalyzer(RSIAnalyzer, _name="custom_analyzer")

    def show(self, results, data: pd.DataFrame):
        # カスタムアナライザーからデータを取得
        custom_analyzer = results[0].analyzers.custom_analyzer.get_analysis()
        dates = custom_analyzer["dates"]
        prices = custom_analyzer["prices"]
        rsi_min_values = custom_analyzer["rsi_min_values"]
        rsi_max_values = custom_analyzer["rsi_max_values"]
        buy_signals = custom_analyzer["buy_signals"]
        sell_signals = custom_analyzer["sell_signals"]
        close_signals = custom_analyzer["close_signals"]

        # データフレームの作成
        rsi_data = pd.DataFrame(
            {
                "Date": dates,
                "RSI Min": rsi_min_values,
                "RSI Max": rsi_max_values,
                "Buy": buy_signals,
                "Sell": sell_signals,
                "Close": close_signals,
            }
        )
        rsi_data["Date"] = pd.to_datetime(rsi_data["Date"])
        rsi_data.set_index("Date", inplace=True)

        # Plotlyを使用してサブプロットを作成
        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=("Nikkei 225", "RSI Chart"),
            row_heights=[0.7, 0.3],
        )

        # 日付を日本語形式に変換する関数
        def format_date_japanese(date):
            return date.strftime("%Y年%m月%d日 %H:%M")

        # 日付インデックスを日本語形式の文字列に変換
        formatted_dates = [format_date_japanese(date) for date in data.index]

        # ホバーテキストを作成
        hover_text = [
            f"日付: {formatted_date}<br>初値: {int(open_)}<br>高値: {int(high_)}<br>安値: {int(low_)}<br>終値: {int(close_)}<br>出来高: {int(volume)}"
            for formatted_date, open_, high_, low_, close_, volume in zip(
                formatted_dates,
                data["open"],
                data["high"],
                data["low"],
                data["close"],
                data["volume"],
            )
        ]

        # ローソク足チャート
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data["open"],
                high=data["high"],
                low=data["low"],
                close=data["close"],
                name="",
                hovertext="",
                hoverinfo="text",
                text=hover_text,
            ),
            row=1,
            col=1,
        )

        # Buy, Sell, Closeシグナルをプロット
        fig.add_trace(
            go.Scatter(
                x=rsi_data.index,
                y=rsi_data["Buy"],
                mode="markers",
                marker=dict(color="green", symbol="triangle-up", size=10),
                name="Buy Signal",
            ),
            row=1,
            col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=rsi_data.index,
                y=rsi_data["Sell"],
                mode="markers",
                marker=dict(color="red", symbol="triangle-down", size=10),
                name="Sell Signal",
            ),
            row=1,
            col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=rsi_data.index,
                y=rsi_data["Close"],
                mode="markers",
                marker=dict(color="blue", symbol="x", size=10),
                name="Close Signal",
            ),
            row=1,
            col=1,
        )

        # RSIチャート
        fig.add_trace(
            go.Scatter(
                x=rsi_data.index,
                y=rsi_data["RSI Min"],
                mode="lines",
                name=f"RSI Min {results[0].p.rsi_min_period}",
            ),
            row=2,
            col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=rsi_data.index,
                y=rsi_data["RSI Max"],
                mode="lines",
                name=f"RSI Max {results[0].p.rsi_max_period}",
            ),
            row=2,
            col=1,
        )

        # レイアウトの設定
        fig.update_layout(
            title="Nikkei 225 Chart with RSIs and Trade Signals",
            xaxis_title="",
            yaxis_title="Price (JPY)",
            yaxis2_title="RSI",
            legend=dict(x=0, y=1.2, orientation="h"),
            xaxis_rangeslider_visible=False,
            height=800,
        )

        fig.update_xaxes(
            # 日付表示を日本語に設定
            tickformat="%Y年%m月%d日",
            rangebreaks=[
                # 土曜日から月曜日の範囲
                dict(bounds=["sat", "mon"]),
                # 他にも祝日とかあるが, 設定が手間なのでやめた
                # なので祝日の箇所は歯抜けになってしまう
            ],
        )

        # チャートの表示
        fig.show()
