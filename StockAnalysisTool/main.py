#!/usr/bin/env python
"""
Main Stock Price & Financial Statement Analysis Tool
===================================================

This file supersedes the previous *stock_analysis_tool.py* — the same functionality is now provided in **main.py** so you can simply run `python main.py ...`.
The implementation is based on the techniques discussed in the hand‑outs
"Pythonによる財務分析に挑戦、有価証券報告書のデータを扱うには" fileciteturn1file0turn1file1.

Features
--------
* **Price download** from Yahoo! Finance via **yfinance**
* **EDINET XBRL** download & parsing for key financial statement items
* **Valuation / profitability ratios** (PER, PBR, ROE, ROA, etc.)
* **Technical indicators** (SMA, EMA, RSI, MACD)
* **Matplotlib charting**
* **CLI** built with `click`

Quick start
~~~~~~~~~~~
```bash
pip install -U yfinance pandas matplotlib requests beautifulsoup4 lxml click tqdm

# Price only
python main.py price --ticker 6758.T --start 2024-01-01

# Full fundamental + technical analysis
python main.py full \
    --ticker 6758.T \
    --edinet-code E00060 \
    --shares-out 1268.0
```
"""

import datetime as _dt
import io
import os
import re
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, Optional

import click
import matplotlib.pyplot as _plt
import pandas as _pd
import requests
import yfinance as _yf
from bs4 import BeautifulSoup as _BS
from tqdm import tqdm

_EDINET_API = "https://disclosure.edinet-fsa.go.jp/api/v1/documents"
_SESSION = requests.Session()
_TIMEOUT = 60  # seconds

############################################################
# Utility helpers
############################################################

def _date(s: str) -> _dt.date:
    """Convert YYYY-MM-DD → date."""
    return _dt.datetime.strptime(s, "%Y-%m-%d").date()

############################################################
# Price data
############################################################

def fetch_price(ticker: str, start: str, end: Optional[str] = None) -> _pd.DataFrame:
    """Download OHLCV price data using yfinance."""
    df = _yf.download(ticker, start=start, end=end, progress=False, auto_adjust=False)
    df.index = _pd.to_datetime(df.index.date)
    return df

############################################################
# Financial statements from EDINET
############################################################

def _download_xbrl_zip(edinet_code: str, target_date: _dt.date) -> Path:
    """Download the latest securities report ZIP after target_date."""
    params = {
        "type": "2",  # securities report
        "date": target_date.strftime("%Y-%m-%d"),
        "edinetCode": edinet_code,
        "Subscription-Key": "",  # optional
    }
    res = _SESSION.get(_EDINET_API + ".json", params=params, timeout=_TIMEOUT)
    res.raise_for_status()
    meta = res.json()
    if not meta.get("results"):
        raise RuntimeError("No filings found for given EDINET code and date.")
    doc_id = meta["results"][0]["docID"]
    url = f"{_EDINET_API}/{doc_id}?type=1"
    r = _SESSION.get(url, timeout=_TIMEOUT)
    r.raise_for_status()
    tmp = Path(tempfile.gettempdir()) / f"{doc_id}.zip"
    tmp.write_bytes(r.content)
    return tmp


def _parse_xbrl_financials(zip_path: Path) -> Dict[str, float]:
    fields = {
        "Sales": ["Sales", "NetSales", "OperatingRevenue"],
        "OperatingIncome": ["OperatingIncome", "OperatingProfit"],
        "NetIncome": ["ProfitAttributableToOwnersOfParent", "NetIncome"],
        "TotalAssets": ["TotalAssets"],
        "Equity": ["Equity", "NetAssets"],
    }
    results: Dict[str, Optional[float]] = {k: None for k in fields}

    with zipfile.ZipFile(zip_path) as zf:
        xbrl_files = [n for n in zf.namelist() if n.endswith(".xbrl")]  # type: ignore
        if not xbrl_files:
            raise RuntimeError("No .xbrl file found in ZIP.")
        xbrl_name = max(xbrl_files, key=lambda n: zf.getinfo(n).file_size)
        txt = zf.read(xbrl_name).decode("utf-8", errors="ignore")
        soup = _BS(txt, "lxml")
        for key, tags in fields.items():
            for t in tags:
                el = soup.find(t)
                if el and el.text and re.match(r"^-?\d+(\.\d+)?$", el.text.strip()):
                    results[key] = float(el.text)
                    break
    return {k: v for k, v in results.items() if v is not None}


def fetch_financials(edinet_code: str, filing_date: Optional[str] = None) -> Dict[str, float]:
    base_date = _date(filing_date) if filing_date else _dt.date.today()
    zip_path = _download_xbrl_zip(edinet_code, base_date)
    data = _parse_xbrl_financials(zip_path)
    return data

############################################################
# Metrics & Indicators
############################################################

def calc_ratios(price: float, shares_out: float, fin: Dict[str, float]) -> Dict[str, float]:
    ratios = {}
    if fin.get("NetIncome") and shares_out:
        ratios["PER"] = (price * shares_out) / fin["NetIncome"]
    if fin.get("Equity"):
        ratios["PBR"] = (price * shares_out) / fin["Equity"]
        if fin.get("NetIncome"):
            ratios["ROE"] = fin["NetIncome"] / fin["Equity"]
    if fin.get("TotalAssets") and fin.get("NetIncome"):
        ratios["ROA"] = fin["NetIncome"] / fin["TotalAssets"]
    return ratios


def sma(series: _pd.Series, window: int = 25) -> _pd.Series:
    return series.rolling(window).mean()

def ema(series: _pd.Series, window: int = 12) -> _pd.Series:
    return series.ewm(span=window, adjust=False).mean()

def rsi(series: _pd.Series, window: int = 14) -> _pd.Series:
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    ma_up = up.rolling(window).mean()
    ma_down = down.rolling(window).mean()
    rs = ma_up / ma_down
    return 100 - (100 / (1 + rs))

def macd(series: _pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    ema_fast = ema(series, fast)
    ema_slow = ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal)
    hist = macd_line - signal_line
    return macd_line, signal_line, hist

############################################################
# Plotting
############################################################

def plot_price(df: _pd.DataFrame, title: str = "Price Chart", show: bool = True):
    _plt.figure(figsize=(10, 6))
    _plt.plot(df.index, df["Close"], label="Close")
    _plt.plot(df.index, sma(df["Close"], 25), label="SMA25")
    _plt.plot(df.index, sma(df["Close"], 75), label="SMA75")
    _plt.legend()
    _plt.title(title)
    _plt.xlabel("Date")
    _plt.ylabel("Price")
    if show:
        _plt.show()

############################################################
# CLI definitions
############################################################

@click.group()
def cli():
    "Stock analysis commands."


@cli.command()
@click.option("--ticker", required=True, help="Yahoo! Finance ticker, e.g. 6758.T")
@click.option("--start", required=True, help="Start date YYYY-MM-DD")
@click.option("--end", default=None, help="End date YYYY-MM-DD")
@click.option("--show/--no-show", default=True)
@click.option("--save", is_flag=True, help="Save price CSV to file")
def price(ticker, start, end, show, save):
    "Download price and plot simple chart."
    df = fetch_price(ticker, start, end)
    if save:
        out = Path(f"{ticker}_prices.csv")
        df.to_csv(out, index_label="Date")
        click.echo(f"Saved: {out}")
    plot_price(df, f"{ticker} Price", show=show)


@cli.command()
@click.option("--ticker", required=True)
@click.option("--edinet-code", required=True, help="EDINET code for issuer")
@click.option("--start", default="2024-01-01")
@click.option("--end", default=None)
@click.option("--shares-out", type=float, default=None, help="Shares outstanding in millions")
@click.option("--show/--no-show", default=True)
@click.option("--save", is_flag=True)
def full(ticker, edinet_code, start, end, shares_out, show, save):
    click.echo("Fetching price data…")
    df = fetch_price(ticker, start, end)

    click.echo("Fetching financial statements…")
    fin = fetch_financials(edinet_code)

    latest_close = df["Close"].iloc[-1]
    ratios = {}
    if shares_out:
        ratios = calc_ratios(latest_close, shares_out * 1_000_000, fin)

    click.echo("Calculating technical indicators…")
    df["SMA25"] = sma(df["Close"], 25)
    df["RSI"] = rsi(df["Close"], 14)
    macd_line, signal_line, hist = macd(df["Close"])
    df["MACD"] = macd_line
    df["MACDSignal"] = signal_line

    if save:
        Path("output").mkdir(exist_ok=True)
        df.to_csv(Path("output") / f"{ticker}_analysis.csv", index_label="Date")
        _pd.Series(fin).to_csv(Path("output") / f"{ticker}_financials.csv", header=["Value"])
        _pd.Series(ratios).to_csv(Path("output") / f"{ticker}_ratios.csv", header=["Value"])
        click.echo("Saved analysis to ./output directory")

    click.echo("Plotting…")
    plot_price(df, f"{ticker} Technical Chart", show=show)
    if ratios:
        click.echo("Valuation/Profitability Ratios:")
        for k, v in ratios.items():
            click.echo(f"  {k}: {v:.2f}")
    else:
        click.echo("Shares outstanding not provided → ratio calc skipped")


if __name__ == "__main__":
    cli()
