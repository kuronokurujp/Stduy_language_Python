#!/usr/bin/env python
# スタックトレースを表示するために追加
import traceback

import pathlib

import modules.common as common

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
import modules.view.interface as view_interface
import modules.view.backtrader as bk_view


if __name__ == "__main__":

    import multiprocessing

    # 以下を入れないとexeファイルでマルチスレッド処理をした時にエラーになって動かない
    multiprocessing.freeze_support()
    multiprocessing.set_start_method("spawn")

    import argparse

    # 引数パーサの作成
    parser = argparse.ArgumentParser(description="")
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

    # ロジックテストしたチャートデータ保存するファイルパス
    parser.add_argument(
        "--chart_save_filepath",
        type=str,
        default="data\\test\\chart.html",
    )

    # ロジックの最適化したデータを保存するディレクトリパス
    parser.add_argument(
        "--opt_save_dirpath",
        type=str,
        default="data\\opt",
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

    # 取引のレバレッジ
    parser.add_argument("--leverage", type=float, default=1.0, help="取引のレバレッジ")
    # 初期資金
    parser.add_argument("--cash", type=int, default=1000000, help="初期資金")
    # アラート設定
    parser.add_argument("--alert", type=int, default=1)

    monitor_process = None
    try:
        # 引数の解析
        args = parser.parse_args()
        b_alert: bool = args.alert == 1

        # マーケットモデルを作成
        market_model: market_model_interface.IModel = market_csv.Model(
            args.csv_filepath,
        )

        # 指定期間の銘柄データをロード
        # テキストフォーマットはyyyy-mm-dd/yyyy-mm-dd
        # 左が開始, 右が終了
        market_model.load(datetext=args.start_to_end)

        def get_strategy_func(logic_name: str):
            return modules.strategy.rsi.RSIStrategy.add_strategy

        def get_analyzer_class_func(logic_name: str):
            return modules.strategy.rsi.RSIStrategy.analyzer_class

        # チャートのロジックモデルを作成
        test_ctrl_model: ctrl_model_interface.IModel = bk_model.IniFileModelByTest(
            logic_filepath=pathlib.Path(args.logic_data_filepath),
            cash=int(args.cash),
            # 戦略を登録するメソッド
            regist_strategey=lambda name: get_strategy_func(logic_name=name),
            # 解析を登録するメソッド
            regist_analyzer=lambda name: get_analyzer_class_func(logic_name=name),
        )

        def get_opt_func(logic_name: str):
            return modules.strategy.rsi.RSIStrategy.add_opt

        # チャートのロジックモデルを作成
        opt_ctrl_model: ctrl_model_interface.IModel = bk_model.IniFileModelByOpt(
            logic_filepath=pathlib.Path(args.logic_data_filepath),
            cash=int(args.cash),
            # 最適化戦略を登録するメソッド
            regist_opt=lambda name: get_opt_func(name),
        )

        # トレードエンジン作成
        ctrl: controller_interface.IController = bk_controller.Controller(
            leverage=args.leverage,
            cpu_count=args.cpu_count,
        )

        ctrl_model: ctrl_model_interface.IModel = None
        ctrl_view: view_interface.IView = None

        # 通常テストか最適化かで利用するモデルとビューを変える
        if test_ctrl_model.is_strategy_mode():
            ctrl_view = bk_view.SaveChartView(
                save_filepath=pathlib.Path(args.chart_save_filepath), b_alert=b_alert
            )
            ctrl_model = test_ctrl_model
        else:
            ctrl_view = bk_view.OptView(
                output_dirpath=pathlib.Path(args.opt_save_dirpath), b_alert=b_alert
            )
            ctrl_model = opt_ctrl_model

        # トレードテスト開始
        ctrl.run(model=ctrl_model, market_model=market_model, view=ctrl_view)

    except ValueError as ve:
        print(f"ValueError: {ve}")
        print(traceback.format_exc())
        if b_alert:
            common.show_alert(
                title="エラー", msg="エラーになりました。ログをチェックしてください"
            )

    except TypeError as te:
        print(f"TypeError: {te}")
        print(traceback.format_exc())
        if b_alert:
            common.show_alert(
                title="エラー", msg="エラーになりました。ログをチェックしてください"
            )

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print(traceback.format_exc())
        if b_alert:
            common.show_alert(
                title="エラー", msg="エラーになりました。ログをチェックしてください"
            )

    finally:
        if monitor_process is not None:
            # Make sure to terminate the monitoring process
            monitor_process.terminate()
            monitor_process.join()
