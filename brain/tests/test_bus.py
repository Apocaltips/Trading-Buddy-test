from __future__ import annotations

from datetime import datetime, timezone
import uuid

from brain.signal_bus import SignalBus


def _signal():
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


def test_bus_idempotency(tmp_path):
    db_path = tmp_path / "signals.db"
    bus = SignalBus(db_path=db_path)
    signal = _signal()
    first = bus.push(signal)
    second = bus.push(signal)
    assert first is True
    assert second is False


def test_bus_fetch(tmp_path):
    db_path = tmp_path / "signals.db"
    bus = SignalBus(db_path=db_path)
    signal = _signal()
    bus.push(signal)
    pending = bus.fetch_pending()
    assert len(pending) == 1
    assert pending[0]["id"] == signal["id"]
