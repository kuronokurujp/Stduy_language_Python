#!/usr/bin/env python
import traceback  # スタックトレースを表示するために追加
import time
import yfinance as yf
import pandas as pd
import backtrader as bt
from tqdm import tqdm

import multiprocessing

# EAロジッククラス
import modules.logics.rsi
import modules.logics.logic

import argparse
import tkinter as tk
from tkinter import messagebox

g_pbar = None


def ShowAlert(title: str, msg: str):
    # ベル音
    print("\a")

    root = tk.Tk()
    root.withdraw()
    messagebox.showwarning(title=title, message=msg)


# 最適化の１処理が終わったに呼ばれるコールバック
def OptimizerCallbacks(cb):
    g_pbar.update()


def EATesting(
    logic: modules.logics.logic.LogicBase, filePath: str = "data\\nikkei_mini\\15m.csv"
):
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
        data: pd.DataFrame = pd.read_csv(
            filePath, parse_dates=["datetime"], index_col="datetime"
        )

        # 必要なカラムのみ選択
        data = data[["open", "high", "low", "close", "volume"]]
        # カラム名を小文字に変換
        data.columns = ["open", "high", "low", "close", "volume"]

    # データをbacktrader用に変換
    data_bt = bt.feeds.PandasData(dataname=data)

    # Cerebroの初期化
    cerebro: bt.Cerebro = bt.Cerebro()
    # データをCerebroに追加
    cerebro.adddata(data_bt)

    # ストラテジーをCerebroに追加
    logic.addstrategy(cerebro)

    # 初期資金を設定
    cerebro.broker.set_cash(1000000)

    # バックテストの実行
    results = cerebro.run()
    logic.show(results=results, data=data)


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
    close_before_val = frange(0, 20.0, 0.1)
    close_after_val = frange(0, 20.0, 0.1)

    # 動作確認用のパラメータ
    #    rsi_min_period = range(9, 10, 1)
    #    rsi_max_period = range(19, 20, 1)
    #    rsi_blank_entry = range(19, 20, 1)
    #    close_type = ["クロス", "クロス前", "クロス後"]
    #    close_before_val = frange(0, 0.3, 0.1)
    #    close_after_val = frange(0, 0.3, 0.1)

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
    #    print("==================================================")
    # 最適化結果の収集
    #    for stratrun in results:
    #        print("**************************************************")
    #        for strat in stratrun:
    #            print("--------------------------------------------------")
    #            print(strat.p._getkwargs())
    # 残り残金
    #            print(strat.p.value)
    # トレード回数
    #            print(strat.p.trades)
    #    print("==================================================")

    #    print("Time(M) used:", str((tend - tstart) / 60))

    # トレードをしていないパラメータは除外する
    best_results = [result for result in results if result[0].p.trades > 0]

    # 一番高い結果から降順にソート
    best_results = sorted(best_results, key=lambda x: x[0].p.value, reverse=True)

    # 1から20位までのリストを作る
    top_20_results = best_results[:20]

    # リストの各要素の値を出力
    for result in top_20_results:
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

    # 利用するロジックのインスタンス生成
    use_logic = modules.logics.rsi.RSILogic()

    try:
        # 引数の解析
        args = parser.parse_args()
        if args.type == "test":
            EATesting(logic=use_logic, filePath=args.csv_filepath)
            ShowAlert(title="終了", msg="テストが終わりました")
        elif args.type == "opt":
            EAOpt(filePath=args.csv_filepath, cpu_power=args.cpu_power)
            ShowAlert(title="終了", msg="最適化が終わりました")
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
