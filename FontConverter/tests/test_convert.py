#!/usr/bin/env python
import modules.convert as convert
from kuro_p_pak.log import logger
from pathlib import Path


def test_convert():
    app_logger: logger.ILoegger = logger.AppLogger(
        log_dirpath=Path(__file__).parent / "data/log",
    )
    app_logger.clearnup()

    output_dir_path: Path = Path(__file__).parent / "data/font"

    font_convert: convert.ConverterWithFont = convert.ConverterWithFont(
        config_file_path=Path(__file__).parent / "data/config.ini",
        font_file_path=Path(__file__).parent / "data/font/TestFont.ttf",
        output_dir_path=output_dir_path,
        new_filename="TestFontConvert.ttf",
    )

    try:
        font_convert.convert(logger=app_logger)
        # コンバーターしたファイルが生成されているか
        assert output_dir_path.joinpath("TestFontConvert.ttf").exists()

    except Exception as e:
        app_logger.info(e)
        assert 0
