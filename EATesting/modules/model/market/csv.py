#!/usr/bin/env python
import modules.model.market.interface as interface
import pathlib
import backtrader as bt
import pandas as pd


# 価格を記載しているCSVファイルをロードしてチャートモデル
class Model(interface.IModel):
    __data: pd.DataFrame
    __file_path: pathlib.Path
    __min_data_count: int

    # データの最小数がいくつか設定できる
    # 価格のデータ数が最小以下ならエラーとなる
    def __init__(self, file_path: pathlib.Path, min_data_count: int) -> None:
        super().__init__()
        self.__file_path = file_path
        self.__min_data_count = min_data_count

    def load(self, datetext: str):
        dates: list[str] = str.split(datetext, "/")
        start_date: pd.Timestamp = pd.Timestamp(dates[0])
        end_date: pd.Timestamp = pd.Timestamp(dates[1])
        self.load_by_start_to_end(start_date=start_date, end_date=end_date)

    def load_by_start_to_end(
        self,
        start_date: pd.Timestamp,
        end_date: pd.Timestamp,
    ) -> None:
        # CSVファイルを読み込む
        csv_data: pd.DataFrame = pd.read_csv(
            self.__file_path, parse_dates=["datetime"], index_col="datetime"
        )

        # 指定された期間でデータをフィルタリング
        self.__data = csv_data[
            (csv_data.index >= start_date) & (csv_data.index < end_date)
        ]

        # 必要なカラムのみ選択
        self.__data = self.__data[["open", "high", "low", "close", "volume"]]
        # カラム名を小文字に変換
        self.__data.columns = ["open", "high", "low", "close", "volume"]

    def prices_format_backtrader(
        self,
    ) -> bt.feeds.PandasData:
        # データをbacktrader用に変換
        return bt.feeds.PandasData(dataname=self.__data)

    # モデルにエラーがないか
    def err_msg(self) -> str:
        data_count: int = len(self.__data)
        if data_count <= self.__min_data_count:
            return f"Error: 価格データ数が{data_count}で最小数{self.__min_data_count}以下"
        return None
