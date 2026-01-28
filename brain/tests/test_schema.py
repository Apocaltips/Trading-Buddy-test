from __future__ import annotations

from datetime import datetime, timezone
import uuid

from brain.signal_schema import validate_signal


def _base_signal():
    now = datetime.now(timezone.utc).isoformat()
    return {
        "id": str(uuid.uuid4()),
        "ts_utc": now,
        "source": "chart_engine",
        "instance": "trend_pullback_5m",
        "strategy": "trend_pullback",
        "symbol": "BTC-USD",
        "pair": "BTC/USDT",
        "side": "buy",
        "intent": "enter",
        "timeframe": "5m",
        "signal_bps": -10.5,
        "price_snapshot": 100.0,
        "ttl_sec": 120,
        "chart_signal": {
            "pattern": "trend_pullback",
            "structure_level": 99.0,
            "timeframes": ["5m"],
            "confluence_score": 80,
            "invalidation_price": 98.0,
            "lines": [{"type": "support", "price": 99.0, "timeframe": "5m"}],
        },
    }


def test_validate_signal_ok():
    ok, errors = validate_signal(_base_signal())
    assert ok
    assert errors == []


def test_validate_signal_missing_fields():
    signal = _base_signal()
    signal.pop("pair")
    ok, errors = validate_signal(signal)
    assert not ok
    assert any("missing_fields" in err for err in errors)


def test_validate_signal_confluence_range():
    signal = _base_signal()
    signal["chart_signal"]["confluence_score"] = 120
    ok, errors = validate_signal(signal)
    assert not ok
    assert "confluence_out_of_range" in errors
