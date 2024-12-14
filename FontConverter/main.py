#!/usr/bin/env python
# スタックトレースを表示するために追加
import traceback
import click

# コンバート処理を記述したモジュール
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


# TODO: フォントのttfファイルから設定ファイルに応じたコンバートを実行してコンバート結果のフォントttfファイルを出力
@click.command()
@click.argument("config", type=Path, default="")
@click.argument("output", type=Path, default="")
@click.argument("ttf", type=Path, default="")
@click.argument("newfile_name", type=str, default="")
def conv(config: Path, output: Path, ttf: Path, newfile_name: str):
    font_convert: convert.ConverterWithFont = convert.ConverterWithFont(
        config_file_path=config,
        font_file_path=ttf,
        output_dir_path=output,
        new_filename=newfile_name,
    )
    global g_logger_sys
    font_convert.convert(logger=g_logger_sys)


@click.group()
def cli():
    pass


# コマンド一覧
# _を付けると-に変えてコマンド名を指定
cli.add_command(conv)


if __name__ == "__main__":
    import multiprocessing

    # 以下を入れないとexeファイルでマルチスレッド処理をした時にエラーになって動かない
    multiprocessing.freeze_support()
    multiprocessing.set_start_method("spawn")

    # グローバル変数の設定
    current_path: Path = my_sys.get_root_dir()

    log_path = current_path.joinpath("log")
    g_logger_sys = logger.AppLogger(log_dirpath=log_path)

    try:
        cli()
        pass
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
