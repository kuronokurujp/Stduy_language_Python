#!/usr/bin/env python
# スタックトレースを表示するために追加
import traceback
import click

import pathlib

import modules.common as common
import modules.log.logger as logger
import modules.log.interface as logger_interface
import modules.analysis.opt as analysis_opt

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

import kuro_p_pak.common.sys as kuro_common_sys

g_logger_sys: logger.AppLogger = None
g_b_alert: bool = False
g_output_dirpath: pathlib.Path = None


def err_msg(msg: str, logger_sys: logger_interface.ILoegger):
    if logger_sys is None:
        print(msg)
    else:
        logger_sys.err(msg)


# 検証 / 最適化の戦略一覧
def get_strategy_func(logic_name: str):
    return modules.strategy.rsi.RSIStrategy.add_strategy


def get_analyzer_class_func(logic_name: str):
    return modules.strategy.rsi.RSIStrategy.analyzer_class


def get_opt_func(logic_name: str):
    return modules.strategy.rsi.RSIStrategy.add_opt


def init_common(output, config, log, alert):
    global g_logger_sys
    global g_b_alert
    global g_output_dirpath

    config_dir: pathlib.Path = pathlib.Path(config)
    if config_dir.exists() is False:
        raise ValueError(f"コンフィグディレクトリがない({config_dir.as_posix()})")

    # ログシステムを作成
    g_logger_sys = logger.AppLogger(
        config_json_filepath=pathlib.Path.joinpath(config_dir, "log.json"),
        log_dirpath=pathlib.Path(log),
    )
    g_logger_sys.clearnup()
    g_b_alert = False
    if alert == 1:
        g_b_alert = True
    g_output_dirpath = pathlib.Path(output)


# どのコマンドでも利用する共通引数
def common_argument(f):
    # 引数の順番が最後に設定したのが初めになっていて最初に設定したのが順番の最後になっていた
    # つまり下から上の順番になっていた
    # 引数追加する時には注意する

    # ログファイル出力するディレクトリパス
    # 引数3
    f = click.argument(
        "log",
        type=str,
        default="",
    )(f)

    # ツールを動かすのに必要な設定ファイルを収めているディレクトリパス
    # 引数2
    f = click.argument(
        "config",
        type=str,
        default="",
    )(f)

    # データ保存するファイルパス
    # 引数1
    f = click.argument(
        "output",
        type=str,
        default="data\\test",
    )(f)

    return f


# どのコマンドでも利用する共通オプション
def common_options(f):
    # アラート設定
    f = click.option("--alert", type=int, default=1)(f)
    return f


@click.command()
@common_argument
@common_options
# 銘柄のデータタイプがcsvならcsvファイルパス指定
@click.argument("csv", type=str, default="")
# 検証で使うロジックデータファイル
@click.argument(
    "logic",
    type=str,
    default="",
)
@click.argument(
    "start_to_end",
    type=str,
    default="2023-01-01/2024-01-01",
)
# 取引のレバレッジ
@click.option("--leverage", type=float, default=1.0)
# 初期資金
@click.option("--cash", type=int, default=1000000)
def valid_t(output, config, log, alert, csv, logic, start_to_end, leverage, cash):

    # 共通初期化
    init_common(output, config, log, alert)

    global g_logger_sys
    global g_b_alert
    global g_output_dirpath

    # 検証
    # マーケットモデルを作成
    market_model: market_model_interface.IModel = market_csv.Model(
        file_path=csv, min_data_count=10000
    )

    # 指定期間の銘柄データをロード
    # テキストフォーマットはyyyy-mm-dd/yyyy-mm-dd
    # 左が開始, 右が終了
    market_model.load(datetext=start_to_end)

    # チャートのロジックモデルを作成
    test_ctrl_model: ctrl_model_interface.IModel = bk_model.IniFileModelByTest(
        logic_filepath=pathlib.Path(logic),
        cash=int(cash),
        # 戦略を登録するメソッド
        regist_strategey=lambda name: get_strategy_func(logic_name=name),
        # 解析を登録するメソッド
        regist_analyzer=lambda name: get_analyzer_class_func(logic_name=name),
    )
    if test_ctrl_model.is_strategy_mode():
        pass
    else:
        raise ValueError("単体検証なのに最適化のロジックデータをロードしている")

    # トレードエンジン作成
    ctrl: controller_interface.IController = bk_controller.Controller(leverage=leverage)

    ctrl_view: view_interface.IView = None
    # 通常テストか最適化かで利用するモデルとビューを変える
    ctrl_view = bk_view.SaveChartView(
        save_dirpath=g_output_dirpath,
        logger_sys=g_logger_sys,
        b_alert=g_b_alert,
    )

    # トレードテスト開始
    ctrl.run(model=test_ctrl_model, market_model=market_model, view=ctrl_view)


@click.command()
@common_argument
@common_options
# 銘柄のデータタイプがcsvならcsvファイルパス指定
@click.argument("csv", type=str, default="")
# 検証で使うロジックデータファイル
@click.argument(
    "logic",
    type=str,
    default="",
)
@click.argument(
    "start_to_end",
    type=str,
    default="2023-01-01/2024-01-01",
)
# 取引のレバレッジ
@click.option("--leverage", type=float, default=1.0)
# 初期資金
@click.option("--cash", type=int, default=1000000)
# 解析タイプがOptの時のCPUパワータイプ
@click.option("--cpu_count", type=int, default=1)
def valid_o(
    output, config, log, alert, csv, logic, start_to_end, leverage, cash, cpu_count: int
):

    # 共通初期化
    init_common(output, config, log, alert)

    global g_logger_sys
    global g_b_alert
    global g_output_dirpath

    # 検証
    # マーケットモデルを作成
    market_model: market_model_interface.IModel = market_csv.Model(
        file_path=csv, min_data_count=10000
    )

    # 指定期間の銘柄データをロード
    # テキストフォーマットはyyyy-mm-dd/yyyy-mm-dd
    # 左が開始, 右が終了
    market_model.load(datetext=start_to_end)

    # チャートのロジックモデルを作成
    opt_ctrl_model: ctrl_model_interface.IModel = bk_model.IniFileModelByOpt(
        logic_filepath=pathlib.Path(logic),
        cash=int(cash),
        # 最適化戦略を登録するメソッド
        regist_opt=lambda name: get_opt_func(name),
    )

    if opt_ctrl_model.is_strategy_mode():
        raise ValueError("最適化検証なのに単体検証のロジックデータをロードしている")

    # トレードエンジン作成
    ctrl: controller_interface.IController = bk_controller.Controller(
        leverage=leverage,
        cpu_count=cpu_count,
    )

    ctrl_model: ctrl_model_interface.IModel = None
    ctrl_view: view_interface.IView = None

    # 通常テストか最適化かで利用するモデルとビューを変える
    ctrl_view = bk_view.OptView(
        output_dirpath=g_output_dirpath,
        logger_sys=g_logger_sys,
        b_alert=g_b_alert,
    )
    ctrl_model = opt_ctrl_model

    # トレードテスト開始
    ctrl.run(model=ctrl_model, market_model=market_model, view=ctrl_view)


@click.command()
@common_argument
@common_options
@click.argument("filepath", type=str, default="")
def analysis_o(output, config, log, alert, filepath: str):
    # 共通初期化
    init_common(output, config, log, alert)

    global g_logger_sys
    global g_b_alert
    global g_output_dirpath

    save_dirpath: pathlib.Path = kuro_common_sys.create_directory_by_datetime_jp_name(
        pathlib.Path(output)
    )

    # TODO: 解析する
    analysis = analysis_opt.Opt(save_dirpath, pathlib.Path(filepath))
    msg: str = analysis.plot()

    if g_b_alert:
        common.show_alert(title="結果", msg=msg)


def dummy():
    import argparse

    # 引数パーサの作成
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "process_type", type=str, default="v", help="v(validate) / a(analyze)"
    )
    # ツールを動かすのに必要な設定ファイルを収めているディレクトリパス
    parser.add_argument(
        "config_dirpath",
        type=str,
        default="",
    )

    # ログファイル出力するディレクトリパス
    parser.add_argument(
        "log_dirpath",
        type=str,
        default="",
    )

    # 解析タイプの引数一覧

    # 検証 / 最適化の引数一覧
    # 銘柄のデータタイプ
    parser.add_argument(
        "--data_type", type=str, default="csv", help="yahoo or csv file"
    )
    # 銘柄のデータタイプがcsvならcsvファイルパス指定
    parser.add_argument("--csv_filepath", type=str, default="", help="csv filepath")

    # 検証で使うロジックデータファイル
    parser.add_argument(
        "--logic_data_filepath",
        type=str,
        default="",
        help="logic data file",
    )

    # ロジックテストしたチャートデータ保存するファイルパス
    parser.add_argument(
        "--chart_save_dirpath",
        type=str,
        default="data\\test",
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
    logger_sys: logger_interface.ILoegger = None
    try:
        # 引数の解析
        args = parser.parse_args()
        b_alert: bool = args.alert == 1

        config_dir: pathlib.Path = pathlib.Path(args.config_dirpath)
        if config_dir.exists() is False:
            raise ValueError(f"コンフィグディレクトリがない({config_dir.as_posix()})")

        # ログシステムを作成
        logger_sys = logger.AppLogger(
            config_json_filepath=pathlib.Path.joinpath(config_dir, "log.json"),
            log_dirpath=pathlib.Path(args.log_dirpath),
        )
        logger_sys.clearnup()
        if args.process_type == "v":
            # 検証 / 最適化
            # マーケットモデルを作成
            market_model: market_model_interface.IModel = market_csv.Model(
                file_path=args.csv_filepath, min_data_count=10000
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
                    save_dirpath=pathlib.Path(args.chart_save_dirpath),
                    logger_sys=logger_sys,
                    b_alert=b_alert,
                )
                ctrl_model = test_ctrl_model
            else:
                ctrl_view = bk_view.OptView(
                    output_dirpath=pathlib.Path(args.opt_save_dirpath),
                    logger_sys=logger_sys,
                    b_alert=b_alert,
                )
                ctrl_model = opt_ctrl_model

            # トレードテスト開始
            ctrl.run(model=ctrl_model, market_model=market_model, view=ctrl_view)
        elif args.process_type == "a":
            # TODO: 最適化ファイルの解析
            pass

    except ValueError as ve:
        err_msg(f"ValueError: {ve}", logger_sys=logger_sys)
        err_msg(traceback.format_exc(), logger_sys=logger_sys)
        if b_alert:
            common.show_alert(title="エラー", msg=ve)

    except TypeError as te:
        err_msg(f"TypeError: {te}", logger_sys=logger_sys)
        err_msg(traceback.format_exc(), logger_sys=logger_sys)
        if b_alert:
            common.show_alert(title="エラー", msg=te)

    except Exception as e:
        err_msg(f"An unexpected error occurred: {e}", logger_sys=logger_sys)
        err_msg(traceback.format_exc(), logger_sys=logger_sys)
        if b_alert:
            common.show_alert(title="エラー", msg=e)

    finally:
        if monitor_process is not None:
            # Make sure to terminate the monitoring process
            monitor_process.terminate()
            monitor_process.join()


@click.group()
def cli():
    pass


# valid_tの_が-に代わっている
# _を使ったらコマンドでは_ではなく-にしないとだめみたい
cli.add_command(valid_t)
cli.add_command(valid_o)
cli.add_command(analysis_o)

if __name__ == "__main__":

    import multiprocessing

    # 以下を入れないとexeファイルでマルチスレッド処理をした時にエラーになって動かない
    multiprocessing.freeze_support()
    multiprocessing.set_start_method("spawn")

    try:
        cli()
    except ValueError as ve:
        err_msg(f"ValueError: {ve}", logger_sys=g_logger_sys)
        err_msg(traceback.format_exc(), logger_sys=g_logger_sys)
        if g_b_alert:
            common.show_alert(title="エラー", msg=ve)

    except TypeError as te:
        err_msg(f"TypeError: {te}", logger_sys=g_logger_sys)
        err_msg(traceback.format_exc(), logger_sys=g_logger_sys)
        if g_b_alert:
            common.show_alert(title="エラー", msg=te)

    except Exception as e:
        err_msg(f"An unexpected error occurred: {e}", logger_sys=g_logger_sys)
        err_msg(traceback.format_exc(), logger_sys=g_logger_sys)
        if g_b_alert:
            common.show_alert(title="エラー", msg=e)
    finally:
        pass
