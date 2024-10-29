#!/usr/bin/env python
import csv
import kuro_p_pak.common
import kuro_p_pak.common.sys
import modules.view.interface as view_interface
import modules.strategy.interface.analyzer_interface as analyzer_interface
import modules.common as common
import modules.log.interface as logger_interface
import pathlib
import pandas as pd
import backtrader as bt
import numpy as np
import kuro_p_pak.common.sys as kuro_common_sys

# hvplotを使用するために必要
import hvplot.pandas
import holoviews as hv
from bokeh.models import HoverTool

from tqdm import tqdm

hv.extension("bokeh")


# テスト結果をチャートファイルにして保存するビュー
class SaveChartView(view_interface.IView):

    __b_alert: bool = True
    __logger_sys: logger_interface.ILoegger = None

    def __init__(
        self,
        save_dirpath: pathlib.Path,
        logger_sys: logger_interface.ILoegger,
        b_alert: bool = True,
    ) -> None:
        super().__init__()
        self.__save_dirpath = save_dirpath
        self.__logger_sys = logger_sys
        self.__b_alert = b_alert

        # ディレクトリを作成（存在しない場合のみ）
        self.__save_dirpath.mkdir(parents=True, exist_ok=True)

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
        self.__logger_sys.info(msg)

    def begin_draw(self, **kwargs) -> None:
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
            }
        )

        # インジケーターグループを取得
        ind_dict: dict[str, np.ndarray] = custom_analyzer.ind_dict
        for key, values in ind_dict.items():
            data[key] = values

        filtered_data: pd.DataFrame = data.reset_index(drop=True)
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

        # チャートに表示する売買シグナル
        signal_plots: list = self.__create_signal_plots(
            filtered_data,
            order_buy_signals=order_buy_signals,
            order_sell_signals=order_sell_signals,
            close_buy_signals=close_buy_signals,
            close_sell_signals=close_sell_signals,
        )

        main_plot = candlestick
        # キャンドルと売買シグナルとインジケーターを合成
        for add_main_plot in signal_plots:
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

        # 表示したい範囲の幅を設定
        # 必要に応じて調整
        window_width = 800

        # x軸の表示範囲を計算
        x_start = max(0, len(filtered_data) - window_width)
        x_end = len(filtered_data)

        # 設定した全プロットのオプション設定
        # x軸に日付を表示していないが
        # サブプロットが入ると表示する空白面積が少なくなって日付を表示しても視認性が悪い
        # かつ見ないのでx軸に日付は表示しないようにした
        def apply_common_opts(plot):
            return plot.opts(
                xlim=(x_start, x_end),
                show_grid=True,
                width=layout_width,
                height=layout_height,
            )

        layout = layout.map(apply_common_opts, hv.Element)

        # 結果を保存するディレクトリを作成
        self.__save_dirpath = kuro_common_sys.create_directory_by_datetime_jp_name(
            self.__save_dirpath
        )

        # チャートファイル作成
        chart_filepath: pathlib.Path = self.__save_dirpath / pathlib.Path("chart.html")
        hvplot.save(layout, filename=pathlib.Path(chart_filepath.as_posix()))

    def end_draw(self, **kwargs) -> None:
        msg: str = (
            f"チャートを '{self.__save_dirpath.absolute()}' に保存しました。Webブラウザで開いてください。"
        )

        self.log(msg=msg)
        if self.__b_alert:
            common.show_alert(title="テストが終わりました", msg=msg)

    def __create_signal_plots(
        self,
        data: pd.DataFrame,
        order_buy_signals: np.array,
        order_sell_signals: np.array,
        close_buy_signals: np.array,
        close_sell_signals: np.array,
    ) -> list:
        signal_plots: list = []

        shift_value: float = 20.0
        # 買いシグナルの設定
        order_buy_condition = ~np.isnan(order_buy_signals)
        data["order_buy_signal_price"] = np.where(
            order_buy_condition, data["low"] - shift_value, np.nan
        )

        # 買い転売シグナルの設定
        close_buy_condition = ~np.isnan(close_buy_signals)
        data["close_buy_signal_price"] = np.where(
            close_buy_condition, data["high"] + shift_value, np.nan
        )

        # 売りシグナルの設定
        order_sell_condition = ~np.isnan(order_sell_signals)
        data["order_sell_signal_price"] = np.where(
            order_sell_condition, data["high"] + shift_value, np.nan
        )

        # 売り転買シグナルの設定
        close_sell_condition = ~np.isnan(close_sell_signals)
        data["close_sell_signal_price"] = np.where(
            close_sell_condition, data["low"] - shift_value, np.nan
        )

        mark_size: int = 128
        # シグナルのプロット
        signal_plots.append(
            data.hvplot.scatter(
                x="index",
                y="order_buy_signal_price",
                marker="triangle",
                color="red",
                size=mark_size,
                legend=False,
            )
        )

        signal_plots.append(
            data.hvplot.scatter(
                x="index",
                y="close_buy_signal_price",
                marker="inverted_triangle",
                color="#18EBF9",
                size=mark_size,
                legend=False,
            )
        )

        signal_plots.append(
            data.hvplot.scatter(
                x="index",
                y="order_sell_signal_price",
                marker="inverted_triangle",
                color="blue",
                size=mark_size,
                legend=False,
            )
        )

        signal_plots.append(
            data.hvplot.scatter(
                x="index",
                y="close_sell_signal_price",
                marker="triangle",
                color="#F94FB8",
                size=mark_size,
                legend=False,
            )
        )

        return signal_plots


# 最適化進捗表示
_g_opt_process_print: tqdm = None


# 最適化の１処理が終わったに呼ばれるコールバック
# マルチスレッドで実行されるのメモリ共有やデッドロックに注意
def _call_optimizer_with_multi_thread(cb):
    global _g_opt_process_print
    _g_opt_process_print.update()


# 最適化テストした結果を表示するビュー
class OptView(view_interface.IView):

    __output_dirpath: pathlib.Path = None
    __b_alert: bool = True
    __logger_sys: logger_interface.ILoegger = None

    def __init__(
        self,
        output_dirpath: pathlib.Path,
        logger_sys: logger_interface.ILoegger,
        b_alert: bool = True,
    ) -> None:
        super().__init__()

        self.__output_dirpath = output_dirpath
        self.__logger_sys = logger_sys

        # ディレクトリを作成（存在しない場合のみ）
        self.__output_dirpath.mkdir(parents=True, exist_ok=True)
        self.__b_alert = b_alert

    def log(self, msg: str) -> None:
        self.__logger_sys.info(msg)

    def begin_draw(self, **kwargs) -> None:
        total: int = kwargs["total"]

        global _g_opt_process_print
        _g_opt_process_print = tqdm(smoothing=0.05, desc="最適化進捗率", total=total)

        cerebro: bt.cerebro = kwargs["cerebro"]
        cerebro.optcallback(_call_optimizer_with_multi_thread)

    def draw(self) -> None:
        pass

    def end_draw(self, **kwargs) -> None:

        global _g_opt_process_print
        if _g_opt_process_print is not None:
            _g_opt_process_print.close()
            _g_opt_process_print = None

        # 引数から必要なパラメータを取得
        #  最適化結果リスト
        results = kwargs["result"]
        # 初期資金
        cash: int = kwargs["cash"]
        msg: str = ""
        if 0 < len(results):
            # TODO: 結果を出力するフォルダを作成
            # TODO: 最適化結果をリストでcsvファイル出力

            # 以下の条件に該当するものは除外
            # トレードしていない
            # 利益がマイナス
            best_results = [
                result
                for result in results
                if (result[0].p.trades > 0) and (result[0].p.value - cash) > 0
            ]

            if len(best_results) <= 0:
                msg = "トレードを一度もしていないか利益がマイナスの結果しかなかった"
            else:
                # 一番高い結果から降順にソート
                best_results = sorted(
                    best_results, key=lambda x: x[0].p.value, reverse=True
                )

                # 最適化の結果をリストで保存
                self.__output_file(
                    output_path=self.__output_dirpath.joinpath("最適化結果.csv"),
                    results=best_results,
                    cash=cash,
                )

                msg = f"フォルダ({self.__output_dirpath.as_posix()})に最適化結果を出力した"
        else:
            msg = f"最適化結果がひとつもない"

        self.log(msg)
        if self.__b_alert:
            common.show_alert(title="最適化が終わりました", msg=msg)

    def __output_file(self, output_path: pathlib.Path, results, cash: int):
        # リストの各要素の値を出力
        # パラメータ名のみ抜き出す
        param_names: list = list(results[0][0].p._getkwargs().keys())

        with open(
            output_path.as_posix(), mode="w", newline="", encoding="utf-8"
        ) as file:
            # ヘッダー書き込み
            writer = csv.writer(file)
            writer.writerow(["資金", "資金増減", "トレード回数"] + param_names)

            for result in results:
                writer.writerow(
                    [
                        int(result[0].p.value),
                        int(result[0].p.value) - cash,
                        int(result[0].p.trades),
                    ]
                    + list(result[0].p._getkwargs().values())
                )

                # print("資金: ", result[0].p.value)
                # print("トレード回数: ", result[0].p.trades)
                # print("パラメータ: ", result[0].p._getkwargs())
