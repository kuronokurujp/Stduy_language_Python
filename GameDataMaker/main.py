#!/usr/bin/env python
# スタックトレースを表示するために追加
import traceback
import click

# パラメータファイル
import modules.convert as convert
from pathlib import Path
from kuro_p_pak.log import logger
from kuro_p_pak.common import my_sys

# グローバル参照
g_logger_sys: logger.AppLogger = None


# エラーメッセージ
def err_msg(msg: str, logger_sys: logger.AppLogger):
    if logger_sys is None:
        print(msg)
    else:
        logger_sys.err(msg)


# エクセルファイルからパラメータファイルをコンバートコマンド
@click.command()
@click.argument("output", type=Path, default="")
@click.argument("excel", type=Path, default="")
def conv_param(output: Path, excel: Path):
    # エクセルファイルからパラメータファイルをコンバート
    game_parameter_convert: convert.ConverterWithGameParamater = (
        convert.ConverterWithGameParamater(
            org_file_path=excel,
            output_dir_path=output,
        )
    )

    global g_logger_sys
    game_parameter_convert.convert(logger=g_logger_sys)


@click.group()
def cli():
    pass


# コマンド一覧
# _を付けると-に変えてコマンド名を指定
cli.add_command(conv_param)


if __name__ == "__main__":
    import multiprocessing

    # 以下を入れないとexeファイルでマルチスレッド処理をした時にエラーになって動かない
    multiprocessing.freeze_support()
    multiprocessing.set_start_method("spawn")

    # グローバル変数の設定
    current_path: Path = my_sys.get_root_dir()

    log_path = current_path.joinpath("log")
    print(f"log dirpath : {log_path.as_posix()}")
    g_logger_sys = logger.AppLogger(log_dirpath=log_path)

    try:
        cli()
    except ValueError as ve:
        err_msg(f"ValueError: {ve}", logger_sys=g_logger_sys)
        err_msg(traceback.format_exc(), logger_sys=g_logger_sys)

    except TypeError as te:
        err_msg(f"TypeError: {te}", logger_sys=g_logger_sys)
        err_msg(traceback.format_exc(), logger_sys=g_logger_sys)

    except Exception as e:
        err_msg(f"An unexpected error occurred: {e}", logger_sys=g_logger_sys)
        err_msg(traceback.format_exc(), logger_sys=g_logger_sys)
    finally:
        pass
