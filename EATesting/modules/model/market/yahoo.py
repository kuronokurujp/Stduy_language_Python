#!/usr/bin/env python
import modules.model.market.interface as interface
import backtrader as bt
import pandas as pd
import yfinance as yf


class Model(interface.IModel):
    symbol: str = ""

    def __init__(self, symbol: str = "^N225") -> None:
        super().__init__()
        # 日経225指数のティッカーシンボルを指定
        self.symbol = symbol

    def load(
        self,
        start_date: pd.Timestamp = pd.Timestamp("2023-01-01"),
        end_date: pd.Timestamp = pd.Timestamp("2024-01-01"),
    ) -> None:
        # yfinanceを使用してデータをダウンロード
        self.data = yf.download(
            self.symbol, start=start_date, end=end_date, period="1d"
        )
        # 必要なカラムのみ選択
        self.data = self.data[["Open", "High", "Low", "Close", "Volume"]]
        # カラム名を小文字に変換
        self.data.columns = ["open", "high", "low", "close", "volume"]
        # タイムゾーンを日本時間に変換
        self.data.index = self.data.index.tz_localize("UTC").tz_convert("Asia/Tokyo")

    def prices_format_backtrader(
        self,
    ) -> bt.feeds.PandasData:
        return bt.feeds.PandasData(dataname=self.data)
