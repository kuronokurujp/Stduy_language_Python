#!/usr/bin/env python
from fontTools.ttLib import TTFont
import os

from kuro_p_pak.log import logger
from kuro_p_pak.loader import file
from pathlib import Path


# データからゲームパラメータに変えて出力するコンバーター
class ConverterWithFont(object):
    # Fontファイルのパス
    __font_file_path: Path = None

    # 生成するFontファイルの名前
    __new_filename: str = None

    # 出力ディレクトリの設定
    __output_dir: Path = None

    # 設定ファイルパス
    __config_file_path: Path = None

    def __init__(
        self,
        config_file_path: Path,
        font_file_path: Path,
        output_dir_path: Path,
        new_filename: str,
    ):
        self.__config_file_path = config_file_path
        self.__font_file_path = font_file_path
        self.__output_dir = output_dir_path
        self.__new_filename = new_filename

    # Fontファイルを読み込んで特定の文字を抽出した新しいFontファイルを作る
    def convert(self, logger: logger.ILoegger):
        os.makedirs(self.__output_dir, exist_ok=True)
        try:
            # iniファイルをロード
            ini_file: file.IniFile = file.IniFile(self.__config_file_path)
            unicode_pairs: str = ini_file.section("target_unicode")["unicode_pairs"]
            # 抽出する文字情報を作成
            keep_ranges: list = eval(unicode_pairs)

            # フォントを読み込み
            font: TTFont = TTFont(self.__font_file_path)
            # テーブルを取得
            cmap = font.getBestCmap()
            keys_to_remove = [
                key for key in cmap if not self.__is_in_ranges(key, keep_ranges)
            ]
            for key in keys_to_remove:
                del cmap[key]

            # 新しいフォントファイルを保存
            output_font_path: Path = Path(self.__output_dir).joinpath(
                self.__new_filename
            )
            font.save(output_font_path)
            logger.info(f"Processed font saved as: {output_font_path}")
        except FileNotFoundError as e:
            logger.err(f"File not found at {self.__font_file_path}")
            raise (e)
        except Exception as e:
            logger.err(f"reading Font file: {e}")
            raise (e)

    def __is_in_ranges(self, codepoint, ranges) -> bool:
        return any(start <= codepoint <= end for start, end in ranges)
