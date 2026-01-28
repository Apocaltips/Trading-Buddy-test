from __future__ import annotations

import json
from datetime import datetime, timezone
import uuid

from brain.gateway import ExecutionGateway
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


def test_gateway_process(monkeypatch, tmp_path):
    db_path = tmp_path / "signals.db"
    bus = SignalBus(db_path=db_path)
    signal = _signal()
    bus.push(signal)

    pair_map_path = tmp_path / "pair_map.json"
    pair_map_path.write_text(json.dumps({"BTC-USD": "BTC/USDT"}), encoding="utf-8")

    gateway = ExecutionGateway(bus=bus, pair_map_path=pair_map_path)

    def _noop_submit(pair: str, side: str) -> None:
        return None

    monkeypatch.setattr(gateway, "_submit", _noop_submit)

    result = gateway.process_once(limit=10)
    assert result.submitted == 1
    assert result.rejected == 0
