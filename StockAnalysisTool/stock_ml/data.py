"""Price data retrieval and storage."""

import pandas as pd
import yfinance as yf
from sqlalchemy import insert, select
from .database import ENGINE, price_table


def fetch_price_df(ticker: str, period: str = "1y") -> pd.DataFrame:
    """Download price data from Yahoo Finance and format it."""
    ticker = ticker.upper()
    df = yf.download(ticker, period=period, auto_adjust=False, progress=False)
    if df.empty:
        raise ValueError(f"No data for {ticker}")

    # Flatten MultiIndex columns if present
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df.index = df.index.tz_localize(None)
    df.reset_index(inplace=True)

    df.rename(
        columns={
            "Date": "date",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Adj Close": "adj_close",
            "Volume": "volume",
        },
        inplace=True,
    )

    # Drop adj_close (not used)
    df = df.drop(columns=["adj_close"], errors="ignore")

    # Add ticker column
    df["ticker"] = ticker

    # Reorder columns
    df = df[["ticker", "date", "open", "high", "low", "close", "volume"]]
    return df


def save_price_df(df: pd.DataFrame) -> None:
    if df.empty:
        return
    with ENGINE.begin() as conn:
        conn.execute(
            insert(price_table).prefix_with("OR REPLACE"),
            df.to_dict("records"),
        )


def ensure_history_up_to_date(ticker: str, lookback_days: int = 365):
    """Ensure DB has at least lookback_days of data; otherwise fetch more."""
    ticker = ticker.upper()
    from datetime import date, timedelta

    with ENGINE.begin() as conn:
        latest_row = conn.execute(
            select(price_table.c.date)
            .where(price_table.c.ticker == ticker)
            .order_by(price_table.c.date.desc())
            .limit(1)
        ).first()
    if latest_row is None:
        # No data: fetch max
        df = fetch_price_df(ticker, period="max")
        save_price_df(df)
        return df
    latest_date = latest_row[0]
    days_missing = (date.today() - latest_date).days
    if days_missing > 1:
        df = fetch_price_df(ticker, period=f"{days_missing+10}d")
        save_price_df(df)
    # Optionally return recent slice
    import pandas as pd

    with ENGINE.begin() as conn:
        df_db = pd.read_sql_table("prices", conn)
    df_db = df_db[df_db["ticker"] == ticker]
    return df_db
