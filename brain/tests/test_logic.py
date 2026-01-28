from pathlib import Path
import sys

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

from brain.logic import analyze


def _sample_df(rows: int = 60) -> pd.DataFrame:
    data = []
    price = 100.0
    for idx in range(rows):
        data.append(
            {
                "date": pd.Timestamp("2024-01-01") + pd.Timedelta(minutes=5 * idx),
                "open": price,
                "high": price * 1.01,
                "low": price * 0.99,
                "close": price * 1.005,
                "volume": 1.0,
            }
        )
        price *= 1.001
    return pd.DataFrame(data)


def test_analyze_returns_signal_and_reason() -> None:
    df_candles = _sample_df()
    result = analyze(df_candles)
    assert "signal" in result
    assert "reason" in result
    assert isinstance(result["signal"], bool)
    assert isinstance(result["reason"], str)
