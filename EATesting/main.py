#!/usr/bin/env python
import traceback  # スタックトレースを表示するために追加
import yfinance as yf
import pandas as pd
import backtrader as bt
from tqdm import tqdm
import pathlib

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
    logic: modules.logics.logic.LogicBase,
    file_path: str = "data\\nikkei_mini\\15m.csv",
    start_date: pd.Timestamp = pd.Timestamp("2023-01-01"),
    end_date: pd.Timestamp = pd.Timestamp("2024-01-01"),
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
            file_path, parse_dates=["datetime"], index_col="datetime"
        )

        # 指定された期間でデータをフィルタリング
        data = data[(data.index >= start_date) & (data.index < end_date)]

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
    logic.show_test(results=results, data=data)


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


def EAOpt(
    logic: modules.logics.logic.LogicBase,
    cpu_count: int,
    file_path: str = "data\\nikkei_mini\\15m.csv",
    start_date: pd.Timestamp = pd.Timestamp("2023-01-01"),
    end_date: pd.Timestamp = pd.Timestamp("2024-01-01"),
):
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
        data = pd.read_csv(file_path, parse_dates=["datetime"], index_col="datetime")
        # 指定された期間でデータをフィルタリング
        data = data[(data.index >= start_date) & (data.index < end_date)]
        # 必要なカラムのみ選択
        data = data[["open", "high", "low", "close", "volume"]]
        # カラム名を小文字に変換
        data.columns = ["open", "high", "low", "close", "volume"]

    # データをbacktrader用に変換
    data_bt = bt.feeds.PandasData(dataname=data)

    # Cerebroの初期化
    cerebro = bt.Cerebro()

    # データをCerebroに追加
    cerebro.adddata(data_bt)

    total_combinations: int = use_logic.optstrategy(cerebro=cerebro)

    # CPUを利用数を計算
    cpu_max: int = multiprocessing.cpu_count()
    # CPUコア数最小・最大をチェック
    if cpu_count <= 0:
        cpu_count = 1
    elif cpu_max < cpu_count:
        cpu_count = cpu_max

    print(f"Use CpuCount({cpu_count}) / CpuMax({cpu_max})")

    global g_pbar
    g_pbar = tqdm(smoothing=0.05, desc="Optimization Runs", total=total_combinations)

    cerebro.optcallback(OptimizerCallbacks)
    results = RunOpt(cerebro, cpu_count)

    if g_pbar is not None:
        g_pbar.close()

    use_logic.show_opt(results=results)


if __name__ == "__main__":
    # 以下を入れないとexeファイルでマルチスレッド処理をした時にエラーになって動かない
    multiprocessing.freeze_support()
    multiprocessing.set_start_method("spawn")

    # 引数パーサの作成
    parser = argparse.ArgumentParser(description="")
    # 解析タイプ
    parser.add_argument("mode", type=str, default="test", help="test or opt")
    parser.add_argument("logic", type=str, default="rsi", help="logic type(rsi)")
    # 銘柄のデータタイプ
    parser.add_argument("data_type", type=str, default="csv", help="yahoo or csv file")
    # 銘柄のデータタイプがcsvならcsvファイルパス指定
    parser.add_argument("csv_filepath", type=str, default="", help="csv filepath")

    # 検証で使うロジックデータファイル
    parser.add_argument(
        "logic_data_filepath",
        type=str,
        default="",
        help="logic data file",
    )

    # 解析タイプがOptの時のCPUパワータイプ
    parser.add_argument(
        "--cpu_count",
        type=int,
        default=1,
        help="opt running cpu count",
    )
    parser.add_argument(
        "--start_to_end",
        type=str,
        default="2023-01-01/2024-01-01",
        help="date start to end",
    )

    try:
        # 引数の解析
        args = parser.parse_args()

        # 利用するロジックのインスタンス生成
        use_logic = modules.logics.rsi.RSILogic(
            logic_filepath=pathlib.Path(args.logic_data_filepath)
        )

        # 指定された期間でデータをフィルタリング
        dates: list[str] = str.split(args.start_to_end, "/")
        start_date: pd.Timestamp = pd.Timestamp(dates[0])
        end_date: pd.Timestamp = pd.Timestamp(dates[1])

        if args.mode == "test":
            EATesting(
                logic=use_logic,
                file_path=args.csv_filepath,
                start_date=start_date,
                end_date=end_date,
            )
            ShowAlert(title="終了", msg="テストが終わりました")
        elif args.mode == "opt":
            EAOpt(
                logic=use_logic,
                file_path=args.csv_filepath,
                cpu_count=args.cpu_count,
                start_date=start_date,
                end_date=end_date,
            )
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
