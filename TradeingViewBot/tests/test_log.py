from modules.log.logger import AppLogger
from pathlib import Path


def test_log_print():
    logger = AppLogger(
        config_json_filepath="data/config/log.json", log_dirpath=Path("data/log")
    )
    logger.info("info test")


def test_log_cleanup():
    logger = AppLogger(
        config_json_filepath="data/config/log.json", log_dirpath=Path("data/log")
    )
    logger.clearnup()
    logger.info("info test")
