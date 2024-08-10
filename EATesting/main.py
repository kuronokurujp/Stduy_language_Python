#!/usr/bin/env python
import traceback  # スタックトレースを表示するために追加
import datetime
import time
import yfinance as yf
import pandas as pd
import backtrader as bt
import mplfinance as mpf
import numpy as np
import plotly.graph_objects as go
import backtrader.analyzers as btanalyzers
from plotly.subplots import make_subplots
import multiprocessing
import modules.logics.rsi
from tqdm.auto import tqdm
import argparse

g_pbar = None


# 最適化の１処理が終わったに呼ばれるコールバック
def OptimizerCallbacks(cb):
    g_pbar.update()


def EATesting(filePath: str = "data\\nikkei_mini\\15m.csv"):
    if False:
        # 日経225指数のティッカーシンボルを指定
        ticker_symbol = "^N225"

        # データを取得する期間の指定
        start_date = "2023-01-01"
        end_date = "2024-12-31"

        # yfinanceを使用してデータをダウンロード
        data = yf.download(ticker_symbol, start=start_date, end=end_date, period="1d")
        # 必要なカラムのみ選択
        data = data[["Open", "High", "Low", "Close", "Volume"]]
        # カラム名を小文字に変換
        data.columns = ["open", "high", "low", "close", "volume"]
        # タイムゾーンを日本時間に変換
        data.index = data.index.tz_localize("UTC").tz_convert("Asia/Tokyo")
    else:
        # CSVファイルを読み込む
        data = pd.read_csv(filePath, parse_dates=["datetime"], index_col="datetime")

        # 必要なカラムのみ選択
        data = data[["open", "high", "low", "close", "volume"]]
        # カラム名を小文字に変換
        data.columns = ["open", "high", "low", "close", "volume"]

    # データをbacktrader用に変換
    data_bt = bt.feeds.PandasData(dataname=data)

    # カスタムアナライザーの定義
    class CustomAnalyzer(bt.Analyzer):
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

    # Cerebroの初期化
    cerebro = bt.Cerebro()

    # データをCerebroに追加
    cerebro.adddata(data_bt)

    # ストラテジーをCerebroに追加
    cerebro.addstrategy(
        modules.logics.rsi.RSIStrategy,
        rsi_min_period=8,
        close_type="クロス前",
        close_before_val=10.0,
    )

    # カスタムアナライザーを追加
    cerebro.addanalyzer(CustomAnalyzer, _name="custom_analyzer")

    # 初期資金を設定
    cerebro.broker.set_cash(1000000)

    # バックテストの実行
    results = cerebro.run()

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


def RunOpt(cerebro, cpu_count: int = 1):
    # これを入れないとメモリが少なくて済む？
    # カスタムアナライザーを追加
    # 最適化だとメモリを食うので使えない
    # cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trade_analyzer")

    # 初期資金を設定
    cerebro.broker.set_cash(1000000)
    cerebro.broker.setcommission(commission=0.0)

    # Run over everything
    return cerebro.run(maxcpus=cpu_count)


def EAOpt(cpu_power: str, filePath: str = "data\\nikkei_mini\\15m.csv"):

    if False:
        # 日経225指数のティッカーシンボルを指定
        ticker_symbol = "^N225"

        # データを取得する期間の指定
        #    start_date = "2023-01-01"
        start_date = "2019-01-01"
        end_date = "2024-12-31"

        # yfinanceを使用してデータをダウンロード
        data = yf.download(ticker_symbol, start=start_date, end=end_date, period="1d")
        # 必要なカラムのみ選択
        data = data[["Open", "High", "Low", "Close", "Volume"]]
        # カラム名を小文字に変換
        data.columns = ["open", "high", "low", "close", "volume"]

        # タイムゾーンを日本時間に変換
        data.index = data.index.tz_localize("UTC").tz_convert("Asia/Tokyo")
    else:
        # CSVファイルを読み込む
        data = pd.read_csv(filePath, parse_dates=["datetime"], index_col="datetime")
        # 必要なカラムのみ選択
        data = data[["open", "high", "low", "close", "volume"]]
        # カラム名を小文字に変換
        data.columns = ["open", "high", "low", "close", "volume"]

    # データをbacktrader用に変換
    data_bt = bt.feeds.PandasData(dataname=data)

    # 開始値、終了値、ステップ値に浮動小数点数値を受け取る関数の定義
    def frange(start, end, step):
        if step == 0:
            raise ValueError("step must not be zero")

        start = float(start)
        end = float(end)
        step = float(step)

        # range関数と同様な振る舞いにする
        if abs(step) > abs(start - end):
            return [start]
        if step > 0 and end - start < 0:
            return []
        elif step < 0 and end - start > 0:
            return []

        exp = len(str(step).split(".")[1])  # 丸める際に使用する桁数
        result = [start]
        val = start
        if step > 0:
            while (val := round(val + step, exp)) < end:
                result.append(val)
        else:
            while (val := round(val + step, exp)) > end:
                result.append(val)
        return result

    # Cerebroの初期化
    cerebro = bt.Cerebro()

    # データをCerebroに追加
    cerebro.adddata(data_bt)

    rsi_min_period = range(6, 20, 1)
    rsi_max_period = range(15, 30, 1)
    rsi_blank_entry = range(10, 30, 1)
    close_type = ["クロス", "クロス前", "クロス後"]
    close_before_val = frange(2.5, 3.0, 0.1)
    close_after_val = frange(2.5, 3.0, 0.1)

    # 動作確認用のパラメータ
    #    rsi_min_period = range(6, 7, 1)
    #    rsi_max_period = range(15, 16, 1)
    #    rsi_blank_entry = range(10, 11, 1)
    #    close_type = ["クロス", "クロス前", "クロス後"]
    #    close_before_val = frange(2.5, 2.6, 0.1)
    #    close_after_val = frange(2.5, 2.7, 0.1)

    # ストラテジーの最適化を追加
    cerebro.optstrategy(
        modules.logics.rsi.RSIStrategy,
        rsi_min_period=rsi_min_period,
        rsi_max_period=rsi_max_period,
        rsi_blank_entry=rsi_blank_entry,
        close_type=close_type,
        close_before_val=close_before_val,
        close_after_val=close_after_val,
        printlog=False,
        optimizing=True,
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
    print(f"Number of Patterns({total_combinations})")

    # CPUを利用数を計算
    cpu_count: int = 1
    cpu_max: int = multiprocessing.cpu_count()
    # CPUコア数の半分を使用
    if cpu_power == "low":
        cpu_count = 1
    elif cpu_power == "mid":
        # 利用可能なCPUコア数を取得
        cpu_count = int(cpu_max * 0.5)
        if cpu_count <= 0:
            cpu_count = 1
    elif cpu_power == "high":
        # 利用可能なCPUコア数を取得
        cpu_count = int(cpu_max * 0.7)
        if cpu_count <= 0:
            cpu_count = 1
    elif cpu_power == "full":
        cpu_count = cpu_max
    print(f"Use CpuCount({cpu_count}) / CpuMax({cpu_max})")

    global g_pbar
    g_pbar = tqdm(smoothing=0.05, desc="Optimization Runs", total=total_combinations)
    # clock the start of the process
    tstart = time.perf_counter()

    cerebro.optcallback(OptimizerCallbacks)
    results = RunOpt(cerebro, cpu_count)

    # clock the end of the process
    tend = time.perf_counter()

    if g_pbar is not None:
        g_pbar.close()

    # 最適化結果の取得
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

    print("Time(M) used:", str((tend - tstart) / 60))

    # 一番高い値から10位までのリストを生成するコード
    best_results = sorted(results, key=lambda x: x[0].p.value, reverse=True)
    top_10_results = best_results[:10]

    # リストの各要素の値を出力
    for result in top_10_results:
        print("Value: ", result[0].p.value)
        print("TradeCount: ", result[0].p.trades)
        print("Prams: ", result[0].p._getkwargs())


if __name__ == "__main__":
    # 以下を入れないとexeファイルでマルチスレッド処理をした時にエラーになって動かない
    multiprocessing.freeze_support()
    multiprocessing.set_start_method("spawn")

    # 引数パーサの作成
    parser = argparse.ArgumentParser(description="")
    # 解析タイプ
    parser.add_argument("type", type=str, default="test", help="test or opt")
    parser.add_argument("logic", type=str, default="rsi", help="logic type(rsi)")
    # 銘柄のデータタイプ
    parser.add_argument("data_type", type=str, default="csv", help="yahoo or csv file")
    # 銘柄のデータタイプがcsvならcsvファイルパス指定
    parser.add_argument("csv_filepath", type=str, default="", help="csv filepath")

    # 解析タイプがOptの時のCPUパワータイプ
    parser.add_argument(
        "--cpu_power",
        type=str,
        default="mid",
        help="opt running cpu power to low / mid / high / full",
    )

    try:
        # 引数の解析
        args = parser.parse_args()
        if args.type == "test":
            EATesting(filePath=args.csv_filepath)
        elif args.type == "opt":
            EAOpt(filePath=args.csv_filepath, cpu_power=args.cpu_power)
        else:
            raise ValueError(f"Unknown type '{args.type}' specified")

    except ValueError as ve:
        print(f"ValueError: {ve}")
        print(traceback.format_exc())  # 詳細なスタックトレースを表示

    except TypeError as te:
        print(f"TypeError: {te}")
        print(traceback.format_exc())  # 詳細なスタックトレースを表示

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print(traceback.format_exc())  # 詳細なスタックトレースを表示
