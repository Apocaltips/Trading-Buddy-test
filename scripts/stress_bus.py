from __future__ import annotations

from datetime import datetime, timezone
import uuid

from brain.signal_bus import SignalBus


def make_signal():
    now = datetime.now(timezone.utc).isoformat()
    return {
        "id": str(uuid.uuid4()),
        "ts_utc": now,
        "source": "chart_engine",
        "instance": "stress",
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


def main(count: int = 1000) -> None:
    bus = SignalBus()
    inserted = 0
    for _ in range(count):
        if bus.push(make_signal()):
            inserted += 1
    print(f"Inserted {inserted} signals")


if __name__ == "__main__":
    main()
