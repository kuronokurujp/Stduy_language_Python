#!/usr/bin/env python
# スタックトレースを表示するために追加
import traceback

import pandas as pd
import pathlib


# EAロジッククラス
import modules.strategy.rsi

# マーケットモデルクラス
import modules.model.market.interface as market_model_interface
import modules.model.market.csv as market_csv

# ロジックモデルクラス
import modules.model.controller.model as ctrl_model_interface
import modules.model.controller.backtrader as bk_model

# コントローラークラス
import modules.controller.interface as controller_interface
import modules.controller.backtrader as bk_controller

# ビュークラス
import modules.view.backtrader as bk_view

import tkinter as tk
from tkinter import messagebox


# 処理終了時のアラート表示
def show_alert(title: str, msg: str):
    # ベル音
    print("\a")

    root = tk.Tk()
    root.withdraw()
    messagebox.showwarning(title=title, message=msg)


if __name__ == "__main__":

    import multiprocessing

    # 以下を入れないとexeファイルでマルチスレッド処理をした時にエラーになって動かない
    multiprocessing.freeze_support()
    multiprocessing.set_start_method("spawn")

    import argparse

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

        # マーケットモデルを作成
        market_model: market_model_interface.IModel = market_csv.Model(
            args.csv_filepath,
        )

        # 指定された期間でデータをフィルタリング
        # TODO: loadメソッド内に文字列解析して開始と終わりの日付を作る
        dates: list[str] = str.split(args.start_to_end, "/")
        start_date: pd.Timestamp = pd.Timestamp(dates[0])
        end_date: pd.Timestamp = pd.Timestamp(dates[1])
        market_model.load(start_date=start_date, end_date=end_date)

        if b_test:
            view: bk_view.SaveChartView = bk_view.SaveChartView(
                save_filepath=pathlib.Path(
                    "data\\test\\holoviews_datashader_candlestick.html"
                )
            )

            # チャートのロジックモデルを作成
            ctrl_model: ctrl_model_interface.IModel = bk_model.IniFileModelByTest(
                logic_filepath=pathlib.Path(args.logic_data_filepath),
                # 戦略を登録するメソッド
                regist_strategey=modules.strategy.rsi.RSIStrategy.add_strategy,
                # 解析を登録するメソッド
                regist_analyzer=modules.strategy.rsi.RSIStrategy.analyzer_class,
            )

            # トレードエンジン作成
            ctrl: controller_interface.IController = bk_controller.Controller(
                leverage=args.leverage,
                b_opt=False,
                cpu_count=args.cpu_count,
                cerebro=ctrl_model.Cerebro,
            )

            # トレードテスト開始
            ctrl.run(controller_model=ctrl_model, market_model=market_model, view=view)

            show_alert(title="終了", msg="テストが終わりました")

        # TODO: 最適化処理はまったくリファクタリングしていないのでテスト処理が終わったらする
        else:
            view: bk_view.OptView = bk_view.OptView()

            # TODO: チャートのロジックモデルを作成
            ctrl_model: ctrl_model_interface.IModel = bk_model.IniFileModelByOpt(
                logic_filepath=pathlib.Path(args.logic_data_filepath),
                # 最適化戦略を登録するメソッド
                regist_opt=modules.strategy.rsi.RSIStrategy.add_opt,
            )

            # トレードエンジン作成
            ctrl: controller_interface.IController = bk_controller.Controller(
                leverage=args.leverage,
                b_opt=True,
                cpu_count=args.cpu_count,
                cerebro=ctrl_model.Cerebro,
            )

            # トレードテスト開始
            ctrl.run(controller_model=ctrl_model, market_model=market_model, view=view)

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
