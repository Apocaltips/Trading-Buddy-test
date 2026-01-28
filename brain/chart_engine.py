from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import pandas as pd


@dataclass
class ChartSignalResult:
    signal: bool
    side: str
    chart_signal: Dict[str, object]


def _ema(series: pd.Series, length: int) -> pd.Series:
    return series.ewm(span=length, adjust=False).mean()


def _vwap(df: pd.DataFrame) -> pd.Series:
    typical = (df["high"] + df["low"] + df["close"]) / 3
    return (typical * df["volume"]).cumsum() / df["volume"].cumsum()


def _bollinger_width(series: pd.Series, length: int = 20) -> pd.Series:
    sma = series.rolling(length).mean()
    std = series.rolling(length).std()
    upper = sma + 2 * std
    lower = sma - 2 * std
    return (upper - lower) / sma.replace(0, pd.NA)


def _support_resistance(df: pd.DataFrame, window: int = 20) -> Tuple[float, float]:
    support = float(df["low"].tail(window).min())
    resistance = float(df["high"].tail(window).max())
    return support, resistance


def _trend_alignment(df: pd.DataFrame) -> bool:
    ema20 = _ema(df["close"], 20).iloc[-1]
    ema50 = _ema(df["close"], 50).iloc[-1]
    ema200 = _ema(df["close"], 200).iloc[-1]
    return bool(ema20 > ema50 > ema200)


def _volume_spike(df: pd.DataFrame, window: int = 20) -> bool:
    if len(df) < window + 1:
        return False
    avg_vol = df["volume"].tail(window).mean()
    return bool(df["volume"].iloc[-1] > avg_vol * 1.5)


def _divergence_reversal(df: pd.DataFrame) -> bool:
    if len(df) < 20:
        return False
    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / 14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / 14, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, pd.NA)
    rsi = (100 - (100 / (1 + rs))).fillna(0)
    price_low = df["low"].tail(10).min()
    prev_price_low = df["low"].iloc[-20:-10].min()
    rsi_low = rsi.tail(10).min()
    prev_rsi_low = rsi.iloc[-20:-10].min()
    return bool(price_low < prev_price_low and rsi_low > prev_rsi_low)


def _volatility_squeeze(df: pd.DataFrame) -> bool:
    width = _bollinger_width(df["close"], 20)
    if len(width) < 25:
        return False
    recent = width.iloc[-1]
    prior = width.iloc[-20:-5].mean()
    return bool(recent > prior * 1.2 and prior < width.mean())


def _breakout_retest(df: pd.DataFrame, resistance: float) -> bool:
    last_close = float(df["close"].iloc[-1])
    prev_close = float(df["close"].iloc[-2])
    last_low = float(df["low"].iloc[-1])
    broke_out = prev_close <= resistance and last_close > resistance * 1.002
    retest = last_low <= resistance * 1.003
    return bool(broke_out and retest)


def _pullback_to_structure(df: pd.DataFrame, support: float) -> bool:
    last_close = float(df["close"].iloc[-1])
    return bool(last_close <= support * 1.01)


def _range_bounce(df: pd.DataFrame, support: float, resistance: float) -> bool:
    last_close = float(df["close"].iloc[-1])
    return bool(abs(last_close - support) <= (resistance - support) * 0.05)


def _mean_reversion(df: pd.DataFrame) -> bool:
    sma = df["close"].rolling(20).mean().iloc[-1]
    last_close = float(df["close"].iloc[-1])
    return bool(last_close < sma * 0.98)


def _vwap_reversion(df: pd.DataFrame) -> bool:
    vwap = _vwap(df).iloc[-1]
    last_close = float(df["close"].iloc[-1])
    return bool(last_close < vwap * 0.99)


def _momentum_continuation(df: pd.DataFrame) -> bool:
    return bool(_trend_alignment(df))


def _sr_flip(df: pd.DataFrame, resistance: float) -> bool:
    last_close = float(df["close"].iloc[-1])
    return bool(last_close > resistance * 1.001)


def _channel_bounce(df: pd.DataFrame, support: float, resistance: float) -> bool:
    last_close = float(df["close"].iloc[-1])
    channel_width = resistance - support
    return bool(last_close <= support + channel_width * 0.1)


def analyze_chart(df_candles: pd.DataFrame, timeframe: str, strategy: str) -> ChartSignalResult:
    if df_candles.empty:
        return ChartSignalResult(False, "buy", {})

    df_indicators = df_candles.copy()

    support, resistance = _support_resistance(df_indicators)
    trend_ok = _trend_alignment(df_indicators)
    vol_spike = _volume_spike(df_indicators)
    vwap_val = float(_vwap(df_indicators).iloc[-1])

    pattern_map = {
        "trend_pullback": lambda: _pullback_to_structure(df_indicators, support),
        "breakout_retest": lambda: _breakout_retest(df_indicators, resistance),
        "range_bounce": lambda: _range_bounce(df_indicators, support, resistance),
        "mean_reversion": lambda: _mean_reversion(df_indicators),
        "vwap_reversion": lambda: _vwap_reversion(df_indicators),
        "momentum_continuation": lambda: _momentum_continuation(df_indicators),
        "divergence_reversal": lambda: _divergence_reversal(df_indicators),
        "volatility_squeeze": lambda: _volatility_squeeze(df_indicators),
        "sr_flip": lambda: _sr_flip(df_indicators, resistance),
        "channel_bounce": lambda: _channel_bounce(df_indicators, support, resistance),
    }

    pattern_func = pattern_map.get(strategy, lambda: False)
    pattern_hit = bool(pattern_func())

    confluence = 0
    if pattern_hit:
        confluence += 50
    if trend_ok:
        confluence += 20
    if vol_spike:
        confluence += 10
    last_close = float(df_indicators["close"].iloc[-1])
    if last_close >= vwap_val:
        confluence += 10
    if abs(last_close - support) / max(last_close, 1) < 0.01:
        confluence += 10

    confluence = min(confluence, 100)

    chart_signal = {
        "pattern": strategy,
        "structure_level": round(support, 6),
        "timeframes": [timeframe],
        "confluence_score": confluence,
        "invalidation_price": round(support * 0.995, 6),
        "lines": [
            {"type": "support", "price": round(support, 6), "timeframe": timeframe},
            {"type": "resistance", "price": round(resistance, 6), "timeframe": timeframe},
            {"type": "vwap", "price": round(vwap_val, 6), "timeframe": timeframe},
        ],
    }

    return ChartSignalResult(pattern_hit, "buy", chart_signal)
