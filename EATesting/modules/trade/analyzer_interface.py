#!/usr/bin/env python
import abc
import numpy as np


# テスト解析クラスのインターフェイス
class IAnalyzer:
    def date_values(self) -> np.ndarray:
        raise NotImplementedError()

    def close_values(self) -> np.ndarray:
        raise NotImplementedError()

    def high_values(self) -> np.ndarray:
        raise NotImplementedError()

    def low_values(self) -> np.ndarray:
        raise NotImplementedError()

    def open_values(self) -> np.ndarray:
        raise NotImplementedError()
