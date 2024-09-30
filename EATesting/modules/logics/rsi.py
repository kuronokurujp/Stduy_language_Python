#!/usr/bin/env python
from pathlib import Path
import backtrader as bt
import modules.trade.backtrader.backtrader_logic
import modules.trade.backtrader.backtrader_strategy as strategy
import modules.trade.backtrader.backtrader_analyzer as analyzer
import modules.trade.interface.analyzer_interface as analyzer_interface

import modules.common
import pandas as pd


# カスタムアナライザーの定義
class RSIAnalyzer(analyzer.BaseAnalyzer):
    def __init__(self):
        self.rsi_min_values = []
        self.rsi_max_values = []

    def _next(self):
        super().next()

        self.rsi_min_values.append(self.strategy.rsi_min[0])
        self.rsi_max_values.append(self.strategy.rsi_max[0])

    def get_analysis(self) -> dict:
        data_dict: dict = super().get_analysis()
        data_dict["rsi_min_values"] = self.rsi_min_values
        data_dict["rsi_max_values"] = self.rsi_max_values

        return data_dict


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

    def __init__(self):
        super().__init__(b_opt=self.params.optimizing, b_log=self.params.printlog)

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

        # RSIの値、日時、終値を保存
        self.rsi_values.append(rsi_min_value)

        # パラメータによってキャンセルする
        # クロス後の決済なのにクロス前の値が入っているのはおかしい
        # クロス後の決済の場合はクロス後の値のみが入っているのが望ましい
        if self.params.close_type == "クロス後":
            if self.params.close_after_val == 0.0:
                self.__stop("Cancle: クロス後決済モードなのにクロス後値が入っていない")
            elif self.params.close_before_val != 0.0:
                self.__stop(
                    "Cancle: クロス後決済モードなのにクロス前値が入っていたから"
                )
        elif self.params.close_type == "クロス前":
            if self.params.close_before_val == 0.0:
                self.__stop("Cancle: クロス前決済モードなのにクロス前値が入っていない")
            elif self.params.close_after_val != 0.0:
                self.__stop(
                    "Cancle: クロス前決済モードなのにクロス後値が入っていたから"
                )
        else:
            if self.params.close_after_val != 0 or self.params.close_before_val != 0.0:
                self.__stop(
                    "Cancle: クロス決済モードなのにクロス後かクロス前の決済値が入っていたから"
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


class RSILogic(modules.trade.backtrader.backtrader_logic.LogicBase):

    def __init__(self, logic_filepath: Path) -> None:
        super().__init__(logic_filepath)

    def _addstrategy(self, cerebro: bt.cerebro):
        # ストラテジーをCerebroに追加
        test_data = self.config["test"]
        cerebro.addstrategy(
            RSIStrategy,
            rsi_min_period=int(test_data["rsi_min_period"]),
            rsi_max_period=int(test_data["rsi_max_period"]),
            rsi_blank_entry=float(test_data["rsi_blank_entry"]),
            close_type=str(test_data["close_type"]),
            close_before_val=float(test_data["close_before_val"]),
            close_after_val=float(test_data["close_after_val"]),
        )

    def analyzer_class(self) -> type[analyzer_interface.IAnalyzer]:
        return RSIAnalyzer

    def _optstrategy(self, cerebro: bt.cerebro) -> int:
        opt_data = self.config["opt"]

        items = opt_data["rsi_min_period"].split(",")
        rsi_min_period: range = range(int(items[0]), int(items[1]), int(items[2]))

        items = opt_data["rsi_max_period"].split(",")
        rsi_max_period: range = range(int(items[0]), int(items[1]), int(items[2]))

        items = opt_data["rsi_blank_entry"].split(",")
        rsi_blank_entry = modules.common.frange(
            float(items[0]), float(items[1]), float(items[2])
        )

        close_type = opt_data["close_types"].split(",")

        items = opt_data["close_before_val"].split(",")
        close_before_val = modules.common.frange(
            float(items[0]), float(items[1]), float(items[2])
        )

        items = opt_data["close_before_val"].split(",")
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
        self.show_total_combination(total=total_combinations)

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

    # TODO: チャートが見づらいので考える
    def show_test(self, results, data: pd.DataFrame):
        return

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
                "Open": data["open"],
                "High": data["high"],
                "Low": data["low"],
                "Close": data["close"],
                "RSI Min": rsi_min_values,
                "RSI Max": rsi_max_values,
                "Buy": buy_signals,
                "Sell": sell_signals,
                # "Close": close_signals,
            }
        )
        rsi_data["Date"] = pd.to_datetime(rsi_data["Date"])
        rsi_data.set_index("Date", inplace=True)

        if False:
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
                go.Scattergl(
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
                go.Scattergl(
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
                go.Scattergl(
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
                go.Scattergl(
                    x=rsi_data.index,
                    y=rsi_data["RSI Min"],
                    mode="lines",
                    name=f"RSI Min {results[0].p.rsi_min_period}",
                ),
                row=2,
                col=1,
            )

            fig.add_trace(
                go.Scattergl(
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
                height=800,
                xaxis_rangeslider_visible=False,
                # デフォルトのドラッグモードをズームに設定
                dragmode="zoom",
                updatemenus=[
                    {
                        "type": "buttons",
                        "showactive": True,
                        "buttons": [
                            {
                                "label": "Zoom In",
                                "method": "relayout",
                                "args": [
                                    {
                                        "xaxis.range": [
                                            date.iloc[30],
                                            date.iloc[70],
                                        ]
                                    }
                                ],
                            },
                            {
                                "label": "Zoom Out",
                                "method": "relayout",
                                "args": [
                                    {
                                        "xaxis.range": [
                                            date.min(),
                                            date.max(),
                                        ]
                                    }
                                ],
                            },
                            {
                                "label": "Reset Zoom",
                                "method": "relayout",
                                "args": [{"xaxis.autorange": True}],
                            },
                            {
                                "label": "Pan",
                                "method": "relayout",
                                "args": [{"dragmode": "pan"}],
                            },
                            {
                                "label": "Select",
                                "method": "relayout",
                                "args": [{"dragmode": "select"}],
                            },
                        ],
                        "direction": "left",
                        "pad": {"r": 10, "t": 10},
                        "x": 0.1,
                        "xanchor": "left",
                        "y": 1.15,
                        "yanchor": "top",
                    }
                ],
                modebar_add=["zoom", "pan", "reset", "zoomIn", "zoomOut"],
                modebar_remove=[
                    "autoScale2d",
                    "resetScale2d",
                    "toggleSpikelines",
                    "hoverClosestCartesian",
                    "hoverCompareCartesian",
                ],
            )

            fig.update_xaxes(
                # 日付表示を日本語に設定
                tickformat="%Y年%m月%d日",
                rangebreaks=[
                    # 土曜日から月曜日の範囲
                    dict(bounds=["sat", "mon"]),
                    # 他にも祝日とかあるが, 設定が手間なのでやめた
                    # なので祝日の箇所は歯抜けになってしまう
                    # TODO: 他にも日経先物miniが動いていない時間帯もぬかすようにしたい
                ],
                # rangeslider_visible=True,
                rangeselector=dict(
                    buttons=list(
                        [
                            dict(
                                count=1, label="1m", step="month", stepmode="backward"
                            ),
                            dict(
                                count=6, label="6m", step="month", stepmode="backward"
                            ),
                            dict(count=1, label="YTD", step="year", stepmode="todate"),
                            dict(count=1, label="1y", step="year", stepmode="backward"),
                            dict(step="all"),
                        ]
                    )
                ),
            )

            # チャートの表示
            fig.show()
        else:

            # DatashaderとBokehを使用して可視化

            # キャンバスの定義
            # cvs = ds.Canvas(plot_width=1000, plot_height=400)
            df = rsi_data
            source = ColumnDataSource(data=df)

            # キャンドルチャートの準備
            inc = df["Close"] > df["Open"]
            view_inc = CDSView(filter=BooleanFilter(inc))
            dec = df["Open"] > df["Close"]
            view_dec = CDSView(filter=BooleanFilter(dec))

            # w = 12 * 60 * 60 * 1000  # バーの幅 (ミリ秒単位)
            # 15分足に適したバーの幅 (ミリ秒単位)
            w = 15 * 60 * 1000  # 15分をミリ秒で表現

            p = figure(
                x_axis_type="datetime",
                height=400,
                width=1000,
                sizing_mode="stretch_width",
                title="Candlestick Chart",
            )
            p.segment(
                "Date",
                "High",
                "Date",
                "Low",
                color="black",
                source=source,
                line_width=2,
            )
            p.vbar(
                "Date",
                w,
                "Open",
                "Close",
                fill_color="red",
                line_color="black",
                source=source,
                view=view_inc,
            )
            p.vbar(
                "Date",
                w,
                "Open",
                "Close",
                fill_color="blue",
                line_color="black",
                source=source,
                view=view_dec,
            )
            # Y軸の範囲設定
            p.y_range = Range1d(df["Low"].min() * 0.95, df["High"].max() * 1.05)

            # レイアウトに統合
            layout = column(p)
            show(layout)

    def show_opt(self, results, result_put_flag: bool = False):
        opt_data = self.config["opt"]
        b: bool = bool(opt_data["result_put_flag"] == "True")
        super().show_opt(results=results, result_put_flag=b)
