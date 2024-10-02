#!/usr/bin/env python
import modules.view.interface as view_interface
import modules.strategy.interface.analyzer_interface as analyzer_interface
import pathlib
import pandas as pd
import backtrader as bt

# hvplotを使用するために必要
import hvplot.pandas
import holoviews as hv
from bokeh.models import HoverTool

from tqdm import tqdm

hv.extension("bokeh")


# テスト結果をチャートファイルにして保存するビュー
class SaveChartView(view_interface.IView):

    def __init__(self, save_filepath: pathlib.Path) -> None:
        super().__init__()
        self.__save_filepath = save_filepath

    # backtraderが呼び出すメソッド
    def show(self):
        # チャートファイル出力をするクラスなので表示処理はない
        pass

    # backtraderが呼び出すメソッド
    def plot(self, strategy, *args, **kwargs):
        # 結果を設定して描画
        self.__strategy = strategy
        self.begin_draw()
        self.draw()
        self.end_draw()

    def log(self, msg: str) -> None:
        print(msg)

    def begin_draw(self) -> None:
        pass

    def draw(self) -> None:
        # カスタムアナライザーからデータを取得
        custom_analyzer: analyzer_interface.IAnalyzer = (
            self.__strategy.analyzers.custom_analyzer
        )

        # 取引データを取得
        dates = custom_analyzer.date_values
        close_values = custom_analyzer.close_values
        open_values = custom_analyzer.open_values
        high_values = custom_analyzer.high_values
        low_values = custom_analyzer.low_values
        # TODO: 買いシグナルリスト
        order_buy_signals = custom_analyzer.order_buy_signals
        # TODO: 買い決済シグナルリスト
        # TODO: 売りシグナルリスト
        # TODO: 売り決済シグナルリスト

        # データフレームの作成
        data = pd.DataFrame(
            {
                "datetime": dates,
                "close": close_values,
                "open": open_values,
                "high": high_values,
                "low": low_values,
                "order_buy": order_buy_signals,
            }
        )

        filtered_data = data.reset_index(drop=True)
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

        # 買いシグナルのプロット
        buy_signals_plot = filtered_data.hvplot.scatter(
            x="index",
            y="order_buy",
        )

        # ラベルの間隔をデータ量に応じて計算
        label_interval = max(1, len(filtered_data) // 300)

        # xticks を設定：ティックの位置は数値/ラベルは日付
        xticks = [
            (filtered_data["index"][i], filtered_data["datetime"][i])
            for i in range(0, len(filtered_data), label_interval)
        ]

        # TODO: チャートのオーバーレイ
        # キャンドルと売買シグナルとインジケーターを合成
        final_plot = candlestick * buy_signals_plot

        xLen = min(800, len(filtered_data))
        final_plot = final_plot.opts(
            xlabel="",
            # ラベルが重ならないように角度をつける
            xrotation=45,
            xticks=xticks,
            show_grid=True,
            # x軸の範囲を調整することで横のスケールを調整できる
            xlim=(0, xLen),
        )

        # チャートファイル作成
        hvplot.save(final_plot, filename=self.__save_filepath.as_posix())

    def end_draw(self) -> None:
        self.log(
            msg=f"チャートを '{self.__save_filepath.as_posix()}' に保存しました。Webブラウザで開いてください。"
        )


# 最適化テストした結果を表示するビュー
class OptView(view_interface.IView):

    def __init__(self, total: int, cerebro: bt.Cerebro) -> None:
        super().__init__()

        self.__pbar = tqdm(smoothing=0.05, desc="最適化進捗率", total=total)
        self.__cerebro = cerebro

    # 最適化の１処理が終わったに呼ばれるコールバック
    def __optimizer_callbacks(self, cb):
        self.__pbar.update()

    # backtraderが呼び出すメソッド
    def show(self):
        # チャートファイル出力をするクラスなので表示処理はない
        pass

    # backtraderが呼び出すメソッド
    def plot(self, strategy, *args, **kwargs):
        # 結果を設定して描画
        self.__strategy = strategy
        self.draw()

    def log(self, msg: str) -> None:
        print(msg)

    def begin_draw(self) -> None:
        self.__cerebro.optcallback(self.__optimizer_callbacks)

    def draw(self) -> None:
        # 最適化結果の取得
        if False:
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
        best_results = [result for result in self.__strategy if result[0].p.trades > 0]
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

    def end_draw(self) -> None:
        if self.__pbar is not None:
            self.__pbar.close()
