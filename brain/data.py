from __future__ import annotations

import os
from typing import List

import ccxt
import pandas as pd


def _fallback_ohlcv(limit: int) -> List[List[float]]:
    now = pd.Timestamp.utcnow().floor("min")
    rows = []
    price = 100.0
    for idx in range(limit):
        ts = now - pd.Timedelta(minutes=5 * (limit - idx))
        open_price = price
        close_price = price * 1.001
        high = max(open_price, close_price) * 1.001
        low = min(open_price, close_price) * 0.999
        volume = 1.0
        rows.append([int(ts.timestamp() * 1000), open_price, high, low, close_price, volume])
        price = close_price
    return rows


def fetch_ohlcv(
    pair: str,
    exchange_id: str = "kraken",
    timeframe: str = "5m",
    limit: int = 200,
    allow_fallback: bool = True,
) -> pd.DataFrame:
    exchange_class = getattr(ccxt, exchange_id)
    exchange = exchange_class({"enableRateLimit": True})
    try:
        ohlcv = exchange.fetch_ohlcv(pair, timeframe=timeframe, limit=limit)
    except Exception:
        if not allow_fallback or os.getenv("DISABLE_OHLCV_FALLBACK") == "1":
            raise
        ohlcv = _fallback_ohlcv(limit)

    df_candles = pd.DataFrame(
        ohlcv,
        columns=["date", "open", "high", "low", "close", "volume"],
    )
    df_candles["date"] = pd.to_datetime(df_candles["date"], unit="ms", utc=True)
    return df_candles
