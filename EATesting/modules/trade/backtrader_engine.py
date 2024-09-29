#!/usr/bin/env python
import modules.trade.engine_interface as interface
import modules.chart.model_intareface as chart_interface
import modules.logics.logic_interface as logic_interface

import holoviews as hv
import pathlib
import numpy as np
import backtrader as bt
import pandas as pd
import multiprocessing
from tqdm import tqdm
from bokeh.models import HoverTool

# hvplotを使用するために必要
import hvplot.pandas

# 日本の祝日を考慮するため
import jpholiday

hv.extension("bokeh")


# Backtraderのplotをオーバーライドするクラス
# これ各ロジック毎に用意する？
class SaveChartPlotter:
    path: pathlib.Path = None

    def __init__(self, filename: pathlib.Path):
        self.path = filename

    def plot(self, strategy, *args, **kwargs):
        # データを収集
        data = strategy.datas[0]
        data_dates = [bt.utils.date.num2date(date) for date in data.datetime.array]
        data_close = data.close.array

        # Pygalでプロット
        # line_chart = pygal.Line(title="Backtrader with Pygal", x_label_rotation=20)
        # line_chart.x_labels = map(str, data_dates)
        # line_chart.add("Close", data_close)
        # line_chart.render_to_file("backtrader_pygal_chart.svg")

    def show(self):
        # PygalはSVGファイルに出力するため、このメソッドでは何もしない
        pass


class Engine(interface.IEngine):
    cerebro: bt.Cerebro = None
    leverage: float = 1.0
    b_opt: bool = False
    result_strategy = None
    cpu_count: int = 0
    pbar = None

    def __init__(
        self, leverage: float = 1.0, b_opt: bool = False, cpu_count: int = 0
    ) -> None:
        super().__init__()

        self.leverage = leverage
        self.b_opt = b_opt
        self.cpu_count = cpu_count

        # Cerebroの初期化
        self.cerebro = bt.Cerebro()

    def run(
        self, logic: logic_interface.ILogic, chart_model: chart_interface.IModel
    ) -> None:
        # データをCerebroに追加
        self.cerebro.adddata(chart_model.prices_format_backtrader())

        # 初期資金を設定
        self.cerebro.broker.set_cash(1000000)
        # レバレッジを変える
        # commisionは手数料
        self.cerebro.broker.setcommission(commission=0)

        # ポジジョンサイズを変える事でレバレッジを変える
        self.cerebro.addsizer(bt.sizers.FixedSize, stake=self.leverage)

        if self.b_opt is False:
            self.__test(logic=logic)
        else:
            self.__opt(logic=logic)

    def save_file(self, filepath: pathlib.Path):
        if self.b_opt is False:
            # カスタムプロッターを使用してプロットしてセーブ
            # self.cerebro.plot(plotter=pygal_plotter)
            # self.cerebro.plot()

            self.__save_test_chart_file(
                strategy=self.result_strategy, filepath=filepath
            )

    def __test(self, logic: logic_interface.ILogic):
        # カスタムアナライザーを追加
        logic.attach_test_strategy(self)

        # バックテストの実行
        strategies = self.cerebro.run()
        self.result_strategy = strategies[0]

    def __opt(self, logic: logic_interface.ILogic):
        total: int = logic.attach_opt_strategy(self)
        print(f"検証回数({total})")

        # CPUを利用数を計算
        cpu_max: int = multiprocessing.cpu_count()
        # CPUコア数最小・最大をチェック
        if self.cpu_count <= 0:
            self.cpu_count = 1
        elif cpu_max < self.cpu_count:
            self.cpu_count = cpu_max

        print(f"使用するCPUコア数は({self.cpu_count}) / CPUコア最大数は({cpu_max})")

        self.pbar = tqdm(smoothing=0.05, desc="最適化進捗率", total=total)

        # バックテストの実行
        self.cerebro.optcallback(self.__optimizer_callbacks)
        self.result_strategy = self.cerebro.run()

        if self.pbar is not None:
            self.pbar.close()

    # TODO: 最適化結果を出力して保存
    def __save_opt_result_file(self, filepath: pathlib.Path):
        self.__show_opt(results=self.result_strategy)

    # TODO: トレード用なのにチャートファイル生成までやっているのおかしい
    # チャート生成は別クラスに分離しないと
    def __save_test_chart_file(self, strategy, filepath: pathlib.Path):
        dates = np.array(strategy.dates)
        close_values = np.array(strategy.close_values)
        open_values = np.array(strategy.open_values)
        high_values = np.array(strategy.high_values)
        low_values = np.array(strategy.low_values)

        # データフレームの作成
        data = pd.DataFrame(
            {
                "datetime": dates,
                "close": close_values,
                "open": open_values,
                "high": high_values,
                "low": low_values,
            }
        )

        # 土日祝日を除いたデータのみを残す
        business_days = data["datetime"].index[
            data["datetime"].apply(
                lambda x: x.weekday() < 5 and not jpholiday.is_holiday(x)
            )
        ]

        # 営業日のみを使ったデータフレームを作成
        filtered_data = data.loc[business_days]

        # 整数のインデックスを作成し、指定した間隔で増加
        filtered_data = filtered_data.reset_index(drop=True)
        filtered_data["index"] = range(len(filtered_data))

        # ローソク足のtooltip情報に日付を入れる
        hover = HoverTool(
            tooltips=[
                ("Date", "@{datetime}{%Y-%m-%d %H:%M}"),
                ("Open", "@open{0.2f}"),
                ("High", "@high{0.2f}"),
                ("Low", "@low{0.2f}"),
                ("Close", "@close{0.2f}"),
            ],
            formatters={
                "@{datetime}": "datetime",
            },
        )

        # ローソク足チャートの描画（hvplotを使用）
        candlestick = filtered_data.hvplot.ohlc(
            x="index",
            y=["open", "high", "low", "close"],
            hover_cols=["datetime"],
            tools=[hover, "pan", "wheel_zoom", "box_zoom", "reset"],
            grid=True,
            width=1200,
            height=400,
            neg_color="indianred",
            pos_color="chartreuse",
            line_color="gray",
            bar_width=1.0,
        )

        # ラベルの間隔をデータ量に応じて計算
        label_interval = max(1, len(filtered_data) // 300)

        # xticks を設定：ティックの位置は数値/ラベルは日付
        xticks = [
            (filtered_data["index"][i], filtered_data["datetime"][i])
            for i in range(0, len(filtered_data), label_interval)
        ]

        xLen = min(800, len(filtered_data))
        candlestick = candlestick.opts(
            xlabel="",
            # ラベルが重ならないように角度をつける
            xrotation=45,
            xticks=xticks,
            show_grid=True,
            # x軸の範囲を調整することで横のスケールを調整できる
            xlim=(0, xLen),
        )

        # チャートファイル作成
        hvplot.save(candlestick, filename=filepath.as_posix())

        print(
            "チャートを 'backtrader_datashader_chart.html' に保存しました。Webブラウザで開いてください。"
        )

    def __show_opt(self, results, result_put_flag: bool = False):
        # 最適化結果の取得
        if result_put_flag:
            print("==================================================")
            # 最適化結果の収集
            for stratrun in results:
                print("**************************************************")
                for strat in stratrun:
                    print("--------------------------------------------------")
                    print(strat.p._getkwargs())
                    # 残り残金
                    print(strat.p.value)
                    # トレード回数
                    print(strat.p.trades)
            print("==================================================")

        # トレードをしていないパラメータは除外する
        best_results = [result for result in results if result[0].p.trades > 0]
        if len(best_results) <= 0:
            print("トレードを一度もしていない結果しかなかった")

        # 一番高い結果から降順にソート
        best_results = sorted(best_results, key=lambda x: x[0].p.value, reverse=True)

        # 1から20位までのリストを作る
        top_20_results = best_results[:20]

        # リストの各要素の値を出力
        for result in top_20_results:
            print("資金: ", result[0].p.value)
            print("トレード回数: ", result[0].p.trades)
            print("パラメータ: ", result[0].p._getkwargs())

    # 最適化の１処理が終わったに呼ばれるコールバック
    def __optimizer_callbacks(self, cb):
        self.pbar.update()
