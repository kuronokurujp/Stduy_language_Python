#!/usr/bin/env python
import numpy as np


# テスト解析クラスのインターフェイス
class IAnalyzer:
    @property
    def date_values(self) -> np.ndarray:
        raise NotImplementedError()

    @property
    def close_values(self) -> np.ndarray:
        raise NotImplementedError()

    @property
    def high_values(self) -> np.ndarray:
        raise NotImplementedError()

    @property
    def low_values(self) -> np.ndarray:
        raise NotImplementedError()

    @property
    def open_values(self) -> np.ndarray:
        raise NotImplementedError()

    @property
    def order_buy_signals(self) -> np.ndarray:
        raise NotImplementedError()

    @property
    def order_sell_signals(self) -> np.ndarray:
        raise NotImplementedError()

    @property
    def close_buy_signals(self) -> np.ndarray:
        raise NotImplementedError()

    @property
    def close_sell_signals(self) -> np.ndarray:
        raise NotImplementedError()

    # インジケーターグループを取得
    @property
    def ind_dict(self) -> dict[str, np.ndarray]:
        raise NotImplementedError()
