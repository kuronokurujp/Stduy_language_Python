#!/usr/bin/env python
# スタックトレースを表示するために追加
import traceback

import pandas as pd
import backtrader as bt
from tqdm import tqdm
import pathlib

import multiprocessing

# EAロジッククラス
import modules.logics.rsi

# マーケットモデルクラス
import modules.chart.model.market.csv_model as market_csv
import modules.chart.model.market.market_intareface as market_interface

# ロジックモデルクラス
import modules.chart.model.logic.model as logic_model
import modules.chart.model.logic.backtrader_model as bk_logic_model

# トレードエンジン
import modules.trade.backtrader.backtrader_engine
import modules.trade.interface.engine_interface


import argparse
import tkinter as tk
from tkinter import messagebox

import time

g_pbar = None

# import pygal


# Backtraderのplotをオーバーライドするクラス
# これ各ロジック毎に用意する？
class PygalPlotter:
    def __init__(self):
        pass

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


def limit_cpu_usage(max_usage=10):
    """
    Monitor and limit CPU usage of the current process.
    max_usage: int, Maximum CPU usage percentage (0-100).
    """
    while True:
        pass
        # cpu_usage = psutil.cpu_percent(interval=1)
        # if cpu_usage > max_usage:
        #    time.sleep(1)


def show_alert(title: str, msg: str):
    # ベル音
    print("\a")

    root = tk.Tk()
    root.withdraw()
    messagebox.showwarning(title=title, message=msg)


# 最適化の１処理が終わったに呼ばれるコールバック
def OptimizerCallbacks(cb):
    g_pbar.update()


def RunOpt(cerebro, cpu_count: int = 1, leverage: float = 1.0):
    # 初期資金を設定
    cerebro.broker.set_cash(1000000)
    cerebro.broker.setcommission(commission=0.0)

    # ポジジョンサイズを変える事でレバレッジを変える
    cerebro.addsizer(bt.sizers.FixedSize, stake=leverage)

    # Run over everything
    return cerebro.run(maxcpus=cpu_count)


# def EAOpt(
#    use_logic: modules.trade.backtrader.backtrader_logic.LogicBase,
#    chart_model: modules.chart.model.model_intarefacereface.IModel,
#    cpu_count: int,
#    leverage: float = 1.0,
# ):
# データをbacktrader用に変換
#    data_bt = chart_model.prices_format_backtrader()

# Cerebroの初期化
#    cerebro = bt.Cerebro()

# データをCerebroに追加
#    cerebro.adddata(data_bt)

#    total_combinations: int = use_logic._optstrategy(cerebro=cerebro)

# CPUを利用数を計算
#    cpu_max: int = multiprocessing.cpu_count()
# CPUコア数最小・最大をチェック
#    if cpu_count <= 0:
#        cpu_count = 1
#    elif cpu_max < cpu_count:
#        cpu_count = cpu_max

#    print(f"使用するCPUコア数は({cpu_count}) / CPUコア最大数は({cpu_max})")

#    global g_pbar
#    g_pbar = tqdm(smoothing=0.05, desc="最適化進捗率", total=total_combinations)

#    cerebro.optcallback(OptimizerCallbacks)
#    results = RunOpt(cerebro, cpu_count, leverage=leverage)

#    if g_pbar is not None:
#        g_pbar.close()

#    use_logic.show_opt(results=results)


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
        help="取引の開始と終わりの日付",
    )
    # CPUパワーリミット%
    parser.add_argument(
        "--cpu_limit_power_percent",
        type=int,
        default=100,
        help="",
    )
    # 取引のレバレッジ
    parser.add_argument("--leverage", type=float, default=1.0, help="取引のレバレッジ")

    monitor_process = None
    try:
        # 引数の解析
        args = parser.parse_args()
        b_test: bool = args.mode == "test"
        b_opt: bool = args.mode == "opt"

        # テストも最適化の設定がない状態
        if not b_test and not b_opt:
            raise ValueError(f"Unknown type '{args.type}' specified")

        # トレードエンジン作成
        trade_engine: modules.trade.interface.engine_interface.IEngine = (
            modules.trade.backtrader.backtrader_engine.Engine(
                leverage=args.leverage,
                b_opt=not b_test,
                cpu_count=args.cpu_count,
            )
        )

        #  チャートモデルを作成
        chart_model: market_interface.IModel = (
            market_csv.Model(  # modules.chart.model.model_intarefacereface.IModel = (  # modules.chart.model.csv_model.Model(
                args.csv_filepath,
            )
        )

        # 指定された期間でデータをフィルタリング
        # TODO: loadメソッド内に文字列解析して開始と終わりの日付を作る
        dates: list[str] = str.split(args.start_to_end, "/")
        start_date: pd.Timestamp = pd.Timestamp(dates[0])
        end_date: pd.Timestamp = pd.Timestamp(dates[1])
        chart_model.load(start_date=start_date, end_date=end_date)

        if b_test:
            # TODO: チャートのロジックモデルを作成
            model_logic: logic_model.IModel = bk_logic_model.IniFileModelByTest(
                logic_filepath=pathlib.Path(args.logic_data_filepath),
                # 戦略を登録するメソッド
                regist_strategey=modules.logics.rsi.RSIStrategy.add_strategy,
                # 解析を登録するメソッド
                regist_analyzer=modules.logics.rsi.RSIStrategy.analyzer_class,
            )

            # トレードテスト開始
            trade_engine.run(logic_model=model_logic, chart_model=chart_model)
            # trade_engine.run(use_logic, chart_model=chart_model)
            # トレードテスト結果をチャートファイルで保存
            trade_engine.save_file(
                filepath=pathlib.Path(
                    "data\\test\\holoviews_datashader_candlestick.html"
                )
            )
            show_alert(title="終了", msg="テストが終わりました")
        # TODO: 最適化処理はまったくリファクタリングしていないのでテスト処理が終わったらする
        else:
            """
            Run the backtrader strategy with limited CPU usage.
            """
            # TODO: チャートのロジックモデルを作成
            model_logic: logic_model.IModel = bk_logic_model.IniFileModelByOpt(
                logic_filepath=pathlib.Path(args.logic_data_filepath),
                # 最適化戦略を登録するメソッド
                regist_opt=modules.logics.rsi.RSIStrategy.add_opt,
            )

            # CPUパワーの制限%があれば制限処理のスレッドを起動
            if args.cpu_limit_power_percent < 100:
                monitor_process = multiprocessing.Process(
                    target=limit_cpu_usage, args=(args.cpu_limit_power_percent)
                )
                monitor_process.start()

            # 利用するロジックのインスタンス生成
            # use_logic = modules.logics.rsi.RSILogic(
            #    logic_filepath=pathlib.Path(args.logic_data_filepath)
            # )

            # EAOpt(
            #    logic=use_logic,
            #    # model_logic=model_logic,
            #    chart_model=chart_model,
            #    cpu_count=args.cpu_count,
            #    leverage=args.leverage,
            # )
            show_alert(title="終了", msg="最適化が終わりました")

    except ValueError as ve:
        print(f"ValueError: {ve}")
        print(traceback.format_exc())

    except TypeError as te:
        print(f"TypeError: {te}")
        print(traceback.format_exc())

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print(traceback.format_exc())

    finally:
        if monitor_process is not None:
            # Make sure to terminate the monitoring process
            monitor_process.terminate()
            monitor_process.join()
