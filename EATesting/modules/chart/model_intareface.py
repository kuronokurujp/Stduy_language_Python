#!/usr/bin/env python
import abc
import backtrader as bt
import pandas as pd


class imodel(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def load(
        self,
        start_date: pd.Timestamp = pd.Timestamp("2023-01-01"),
        end_date: pd.Timestamp = pd.Timestamp("2024-01-01"),
    ) -> None:
        return NotImplementedError()

    @abc.abstractmethod
    def prices_format_backtrader(
        self,
    ) -> bt.feeds.PandasData:
        return NotImplementedError()
