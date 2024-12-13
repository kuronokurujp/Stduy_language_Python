#!/usr/bin/env python

import modules.convert as convert
from kuro_p_pak.log import logger
from pathlib import Path

# 必ず関数名にはtest_を頭につける
def test_convert_with_game_data():
    app_logger: logger.ILoegger = logger.AppLogger(
        log_dirpath=Path(__file__).parent / "data/log",
    )
    app_logger.clearnup()

    output_dir_path: Path = Path(__file__).parent / "data/parameters"
    game_parameter_convert: convert.ConverterWithGameParamater = (
        convert.ConverterWithGameParamater(
            org_file_path=Path(__file__).parent / "data/Template.xlsm",
            output_dir_path=output_dir_path,
        )
    )

    try:
        game_parameter_convert.convert(logger=app_logger)
        # ゲームファイルが作成しているか
        assert output_dir_path.joinpath("Enemy.json").exists()

    except Exception as e:
        app_logger.info(e)
        assert 0
