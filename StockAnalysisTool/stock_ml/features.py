"""
Enhanced feature engineering utilities for Japanese stock ML.
Requires: pandas_ta >= 0.3.14
"""

from __future__ import annotations
import pandas as pd
import pandas_ta as ta


def make_features(df: pd.DataFrame, window: int = 5):
    """
    Parameters
    ----------
    df : pandas.DataFrame
        必須列: ['close', 'volume']  *index は不要（どちらでも可）
    window : int
        過去リターンのラグ数 (lag_1 .. lag_window)

    Returns
    -------
    features_df : pandas.DataFrame
        各特徴量と 'target', 'return' を含む DataFrame
    feature_cols : list[str]
        学習に使う列名リスト
    """
    df = df.copy()

    # ---------- ベースリターン ----------
    df["return"] = df["close"].pct_change()
    for i in range(1, window + 1):
        df[f"lag_{i}"] = df["return"].shift(i)

    # ---------- テクニカル指標 ----------
    df["rsi14"] = ta.rsi(df["close"], length=14)

    macd = ta.macd(df["close"], fast=12, slow=26, signal=9)
    if not macd.empty:
        df["macd_hist"] = macd["MACDh_12_26_9"]

    bb = ta.bbands(df["close"], length=20, std=2)
    if not bb.empty:
        df["bb_percent_b"] = (df["close"] - bb["BBL_20_2.0"]) / (
            bb["BBU_20_2.0"] - bb["BBL_20_2.0"]
        )

    sma20 = ta.sma(df["close"], length=20)
    df["sma20_ratio"] = (df["close"] / sma20) - 1

    vol_sma20 = ta.sma(df["volume"], length=20)
    df["vol_ratio"] = (df["volume"] / vol_sma20) - 1

    # ---------- 目的変数 ----------
    # 翌日の騰落率が +0.3% を超えたら 1、そうでなければ 0
    df["target"] = (df["return"].shift(-1) > 0.003).astype(int)

    # ---------- 後片付け ----------
    df.dropna(inplace=True)

    feature_cols = [
        *[f"lag_{i}" for i in range(1, window + 1)],
        "rsi14",
        "macd_hist",
        "bb_percent_b",
        "sma20_ratio",
        "vol_ratio",
    ]
    return df[feature_cols + ["target", "return"]], feature_cols
