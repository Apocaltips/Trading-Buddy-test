from __future__ import annotations

from brain.constants import API_URL, DB_PATH
from brain.data import fetch_ohlcv


def test_guardrail_constants():
    assert DB_PATH == "/shared_data/signals.db"
    assert API_URL == "http://ft_bot:8080/api/v1"


def test_guardrail_df_columns():
    df = fetch_ohlcv("BTC/USDT", limit=5, allow_fallback=True)
    assert list(df.columns) == ["date", "open", "high", "low", "close", "volume"]
