#!/usr/bin/env python
import modules.view.interface as view_interface
import modules.strategy.interface.analyzer_interface as analyzer_interface
import pathlib
import pandas as pd
import backtrader as bt
import numpy as np

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
        # 買いシグナルリスト
        order_buy_signals = custom_analyzer.order_buy_signals
        # 買い決済シグナルリスト
        close_buy_signals = custom_analyzer.close_buy_signals
        # 売りシグナルリスト
        order_sell_signals = custom_analyzer.order_sell_signals
        # 売り決済シグナルリスト
        close_sell_signals = custom_analyzer.close_sell_signals

        # データフレームの作成
        data: pd.DataFrame = pd.DataFrame(
            {
                "datetime": dates,
                "close": close_values,
                "open": open_values,
                "high": high_values,
                "low": low_values,
                "order_buy": order_buy_signals,
                "close_buy": close_buy_signals,
                "order_sell": order_sell_signals,
                "close_sell": close_sell_signals,
            }
        )

        # インジケーターグループを取得
        ind_dict: dict[str, np.ndarray] = custom_analyzer.ind_dict
        for key, values in ind_dict.items():
            data[key] = values

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
            neg_color="indianred",
            pos_color="chartreuse",
            line_color="gray",
            bar_width=1.0,
        )

        signal_labels_plots: list[hv.Labels] = []

        # 買い注文シグナルのプロット
        # データに表示するテキストを入れる必要がある
        filtered_data["order_buy_text"] = "買新規"
        # テキストのスケール値を変えることできない？
        signal_labels_plots.append(
            hv.Labels(
                data=filtered_data,
                kdims=["index", "order_buy"],
                vdims=["order_buy_text"],
            ).opts(
                text_color="blue",
            )
        )

        # 買いクローズシグナルのプロット
        filtered_data["close_buy_text"] = "買転売"
        signal_labels_plots.append(
            hv.Labels(
                data=filtered_data,
                kdims=["index", "close_buy"],
                vdims=["close_buy_text"],
            ).opts(
                text_color="red",
            )
        )

        # 売り新規のシグナルプロット
        filtered_data["order_sell_text"] = "売新規"
        signal_labels_plots.append(
            hv.Labels(
                data=filtered_data,
                kdims=["index", "order_sell"],
                vdims=["order_sell_text"],
            ).opts(
                text_color="blue",
            )
        )

        # 売りクローズシグナルのプロット
        filtered_data["close_sell_text"] = "売転売"
        signal_labels_plots.append(
            hv.Labels(
                data=filtered_data,
                kdims=["index", "close_sell"],
                vdims=["close_sell_text"],
            ).opts(
                text_color="red",
            )
        )

        main_plot = candlestick
        # キャンドルと売買シグナルとインジケーターを合成
        for add_main_plot in signal_labels_plots:
            main_plot = main_plot * add_main_plot

        # サブプロットがない場合はmain_plotがレイアウトになる
        layout = main_plot

        # チャートレイアウトの縦横サイズ
        # サブプロットがあるとheight値を調整
        layout_width: int = 1200
        layout_height: int = 600

        # インジケータープロットを作成してサブプロットで追加
        # インジケーターリストからプロットリストを生成
        sub_plots: list = []
        for key, values in ind_dict.items():
            sub_plots.append(filtered_data.hvplot.line(x="index", y=key))

        if 0 < len(sub_plots):
            layout_height = int(layout_height / 2)
            compoite_sub_plot = sub_plots[0]
            for i in range(1, len(sub_plots)):
                compoite_sub_plot = compoite_sub_plot * sub_plots[i]
            layout = (main_plot + compoite_sub_plot).cols(1)

        xLen = min(800, len(filtered_data))

        # 設定した全プロットのオプション設定
        # x軸に日付を表示していないが
        # サブプロットが入ると表示する空白面積が少なくなって日付を表示しても視認性が悪い
        # かつ見ないのでx軸に日付は表示しないようにした
        def apply_common_opts(plot):
            return plot.opts(
                xlim=(0, xLen),
                show_grid=True,
                width=layout_width,
                height=layout_height,
            )

        layout = layout.map(apply_common_opts, hv.Element)

        # チャートファイル作成
        hvplot.save(layout, filename=self.__save_filepath.as_posix())

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
