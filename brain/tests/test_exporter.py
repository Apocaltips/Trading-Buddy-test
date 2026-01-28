from __future__ import annotations

import json
from datetime import datetime, timezone

from brain.signal_bus import SignalBus
from brain.signal_exporter import SignalExporter, build_signal


def test_exporter_push(tmp_path):
    db_path = tmp_path / "signals.db"
    bus = SignalBus(db_path=db_path)

    pair_map_path = tmp_path / "pair_map.json"
    pair_map_path.write_text(json.dumps({"BTC-USD": "BTC/USDT"}), encoding="utf-8")

    exporter = SignalExporter(bus, pair_map_path)

    signal = build_signal(
        instance="trend_pullback_5m",
        strategy="trend_pullback",
        pair="BTC/USDT",
        timeframe="5m",
        side="buy",
        price_snapshot=100.0,
        chart_signal={
            "pattern": "trend_pullback",
            "structure_level": 99.0,
            "timeframes": ["5m"],
            "confluence_score": 80,
            "invalidation_price": 98.0,
            "lines": [{"type": "support", "price": 99.0, "timeframe": "5m"}],
        },
        signal_bps=-10.0,
        ttl_sec=120,
        pair_map=exporter.pair_map,
        stop_loss=0.02,
        reason="test",
    )

    assert exporter.export(signal) is True
