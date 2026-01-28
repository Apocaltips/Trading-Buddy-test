from __future__ import annotations

from typing import Dict

import pandas as pd

try:
    import pandas_ta as ta
except Exception:  # pragma: no cover - optional dependency
    ta = None


def _ema(series: pd.Series, length: int) -> pd.Series:
    return series.ewm(span=length, adjust=False).mean()


def _rsi(series: pd.Series, length: int) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / length, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / length, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, pd.NA)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(0)


def analyze(df_candles: pd.DataFrame) -> Dict[str, object]:
    if df_candles.empty:
        return {"signal": False, "reason": "No data provided"}

    df_indicators = df_candles.copy()

    if ta is not None:
        df_indicators["rsi"] = ta.rsi(df_indicators["close"], length=14)
        df_indicators["ema_fast"] = ta.ema(df_indicators["close"], length=12)
        df_indicators["ema_slow"] = ta.ema(df_indicators["close"], length=26)
    else:
        df_indicators["rsi"] = _rsi(df_indicators["close"], length=14)
        df_indicators["ema_fast"] = _ema(df_indicators["close"], length=12)
        df_indicators["ema_slow"] = _ema(df_indicators["close"], length=26)

    latest = df_indicators.iloc[-1]
    signal = bool(latest["rsi"] < 30 and latest["ema_fast"] > latest["ema_slow"])

    if signal:
        reason = "RSI below 30 with EMA fast above EMA slow"
    else:
        reason = "No signal: RSI/EMA conditions not met"

    return {"signal": signal, "reason": reason}