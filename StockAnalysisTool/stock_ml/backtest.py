"""
Backtesting utilities with walk-forward cross-validation
"""

from __future__ import annotations
import pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
from .data import ensure_history_up_to_date
from .features import make_features
from .model import SimpleMLP
from .model_lgb import train_lgb


# ---------------------------------------------------------------------
# 1. モデルを一時的に学習
# ---------------------------------------------------------------------
def _train_temp_model(df: pd.DataFrame, lag: int, n_epochs: int = 15):
    data, feat_cols = make_features(df, window=lag)
    if data.empty:
        raise ValueError
    model = train_lgb(data, feat_cols)
    return model, feat_cols

    data, feature_cols = make_features(df, window=lag)
    if data.empty:
        raise ValueError("Not enough training data")

    x = torch.tensor(data[feature_cols].values, dtype=torch.float32)
    y = torch.tensor(data["target"].values, dtype=torch.float32)
    loader = DataLoader(TensorDataset(x, y), batch_size=32, shuffle=True)

    model = SimpleMLP(len(feature_cols))
    criterion = nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)  # L2

    model.train()
    for _ in range(n_epochs):
        for xb, yb in loader:
            optimizer.zero_grad()
            loss = criterion(model(xb), yb)
            loss.backward()
            optimizer.step()

    model.eval()
    return model, feature_cols


# ---------------------------------------------------------------------
# 2. シグナル戦略をシミュレート
# ---------------------------------------------------------------------
def _simulate_strategy(test_df, feat_cols, model, cost=0.002, threshold=0.6):
    capital = 1.0
    for i in range(len(test_df) - 1):
        x = torch.tensor(test_df.iloc[i][feat_cols].values, dtype=torch.float32)
#        prob = model(x).item()
        prob = model.predict(x)[0]
        if prob > threshold:
            capital *= 1 + test_df.iloc[i + 1]["return"] - cost
    return capital


# ---------------------------------------------------------------------
# 3. ウォークフォワードで複数期間を平均化
# ---------------------------------------------------------------------
def walk_forward_backtest(
    df: pd.DataFrame,
    lag: int,
    train_days: int = 252,
    test_days: int = 60,
    step: int = 60,
):
    """
    Returns
    -------
    strategy_mean, buyhold_mean : float
    """
    results = []
    start = 0
    while start + train_days + lag + test_days <= len(df):
        train_df = df.iloc[start : start + train_days]
        test_slice = df.iloc[start + train_days : start + train_days + test_days + lag]
        start += step

        test_feat, feat_cols = make_features(test_slice.copy(), window=lag)
        if test_feat.empty:
            continue

        try:
            model, feat_cols = _train_temp_model(train_df, lag)
        except ValueError:
            continue

        strat = _simulate_strategy(test_feat, feat_cols, model)
        bh = (1 + test_feat["return"]).cumprod().iloc[-1]
        results.append((strat, bh))

    if not results:
        return 1.0, 1.0

    strat_avg = sum(r[0] for r in results) / len(results)
    bh_avg = sum(r[1] for r in results) / len(results)
    return strat_avg, bh_avg


# ---------------------------------------------------------------------
# 4. 外部 API: run_backtests
# ---------------------------------------------------------------------
def run_backtests(
    ticker: str,
    train_windows: list[int] | None = None,
    lags: list[int] | None = None,
    test_days: int = 60,
):
    """
    Returns
    -------
    List[dict] each with keys:
        train_days, lag, strategy_mult, buy_hold_mult, excess
    """
    if train_windows is None:
        train_windows = [252, 504, 756]  # 1y, 2y, 3y
    if lags is None:
        lags = [5, 10]

    need_days = max(train_windows) + test_days + max(lags) + 5
    df = ensure_history_up_to_date(ticker, lookback_days=need_days)
    df.sort_values("date", inplace=True)
    df["return"] = df["close"].pct_change()

    results = []
    for train_len in train_windows:
        for lag in lags:
            if len(df) < train_len + test_days + lag:
                continue
            strat, bh = walk_forward_backtest(
                df.copy(), lag, train_days=train_len, test_days=test_days
            )
            results.append(
                {
                    "train_days": train_len,
                    "lag": lag,
                    "strategy_mult": strat,
                    "buy_hold_mult": bh,
                    "excess": strat - bh,
                }
            )

    results.sort(key=lambda r: r["excess"], reverse=True)
    return results
