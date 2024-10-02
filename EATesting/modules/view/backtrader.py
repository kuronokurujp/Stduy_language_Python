#!/usr/bin/env python
import modules.view.interface as view_interface
import modules.strategy.interface.analyzer_interface as analyzer_interface
import pathlib
import pandas as pd

# hvplotを使用するために必要
import hvplot.pandas
import holoviews as hv
from bokeh.models import HoverTool

# 日本の祝日を考慮するため
import jpholiday

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
        self.draw()

    def log(self, msg: str) -> None:
        print(msg)

    def draw(self) -> None:
        # カスタムアナライザーからデータを取得
        custom_analyzer: analyzer_interface.IAnalyzer = (
            self.__strategy.analyzers.custom_analyzer
        )

        dates = custom_analyzer.date_values
        close_values = custom_analyzer.close_values
        open_values = custom_analyzer.open_values
        high_values = custom_analyzer.high_values
        low_values = custom_analyzer.low_values

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
        hvplot.save(candlestick, filename=self.__save_filepath.as_posix())

        self.log(
            msg=f"チャートを '{self.__save_filepath.as_posix()}' に保存しました。Webブラウザで開いてください。"
        )


# 最適化テストした結果を表示するビュー
class OptView(view_interface.IView):

    def __init__(self, total: int) -> None:
        super().__init__()

        self.pbar = tqdm(smoothing=0.05, desc="最適化進捗率", total=total)

    def log(self, msg: str) -> None:
        print(msg)

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
    def optimizer_callbacks(self, cb):
        self.pbar.update()
