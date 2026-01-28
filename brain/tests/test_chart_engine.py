from __future__ import annotations

import pandas as pd

from brain.chart_engine import analyze_chart


def _trend_df(rows: int = 250) -> pd.DataFrame:
    data = {
        "date": pd.date_range("2024-01-01", periods=rows, freq="5min"),
        "open": [],
        "high": [],
        "low": [],
        "close": [],
        "volume": [],
    }
    price = 100.0
    for _ in range(rows):
        open_price = price
        close_price = price * 1.001
        high = max(open_price, close_price) * 1.001
        low = min(open_price, close_price) * 0.999
        volume = 100.0
        data["open"].append(open_price)
        data["close"].append(close_price)
        data["high"].append(high)
        data["low"].append(low)
        data["volume"].append(volume)
        price = close_price
    return pd.DataFrame(data)


def test_chart_engine_basic():
    df = _trend_df()
    result = analyze_chart(df, "5m", "momentum_continuation")
    assert isinstance(result.chart_signal, dict)
    assert "confluence_score" in result.chart_signal
