#!/usr/bin/env python
import modules.tvdata_feed as tvdata_feed
import kuro_p_pak.log.logger as logger
import kuro_p_pak.loader.file as loader_file
from pathlib import Path


def test_log():
    try:
        app_logger: logger.ILoegger = logger.AppLogger(
            log_dirpath=Path(__file__).parent / "data/log",
        )
        app_logger.info("info test")

    except Exception as e:
        print(e)
        assert False


def test_config():
    try:
        ini_file: loader_file.IniFile = loader_file.IniFile(
            logic_filepath=Path("data/config/user/config.ini")
        )
        section = ini_file.section("tv_account")
        print(section["username"])
        print(section["password"])

    except Exception as e:
        print(e)
        assert False


# 必ず関数名にはtest_を頭につける
def test_process_tvdata():

    try:
        tv = tvdata_feed.TvDatafeed()
        # 銘柄のチャートデータを取得して表示
        print(
            tv.get_hist(
                "NK225M",
                "OSE",
                fut_contract=1,
                interval=tvdata_feed.Interval.in_1_hour,
            )
        )

        print(tv.get_hist("CRUDEOIL", "MCX", fut_contract=1))
        print(tv.get_hist("NIFTY", "NSE", fut_contract=1))
        print(
            tv.get_hist(
                "EICHERMOT",
                "NSE",
                interval=tvdata_feed.Interval.in_1_hour,
                n_bars=500,
                extended_session=False,
            )
        )
    except Exception as identifier:
        print(identifier)
        assert False
