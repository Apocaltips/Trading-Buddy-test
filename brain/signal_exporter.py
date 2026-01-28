from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Dict, Optional
import uuid

from .signal_bus import SignalBus
from .signal_schema import validate_signal


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_pair_map(path: Path) -> Dict[str, str]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def pair_to_symbol(pair: str, pair_map: Dict[str, str]) -> Optional[str]:
    for symbol, mapped_pair in pair_map.items():
        if mapped_pair == pair:
            return symbol
    return None


def build_signal(
    *,
    instance: str,
    strategy: str,
    pair: str,
    timeframe: str,
    side: str,
    price_snapshot: float,
    chart_signal: Dict[str, object],
    signal_bps: float,
    ttl_sec: int,
    pair_map: Dict[str, str],
    stop_loss: Optional[float] = None,
    reason: Optional[str] = None,
) -> Dict[str, object]:
    symbol = pair_to_symbol(pair, pair_map)
    if symbol is None:
        raise ValueError(f"No mapping for pair: {pair}")

    payload: Dict[str, object] = {
        "id": str(uuid.uuid4()),
        "ts_utc": _utc_now(),
        "source": "chart_engine",
        "instance": instance,
        "strategy": strategy,
        "symbol": symbol,
        "pair": pair,
        "side": side,
        "intent": "enter",
        "timeframe": timeframe,
        "signal_bps": signal_bps,
        "price_snapshot": price_snapshot,
        "ttl_sec": ttl_sec,
        "chart_signal": chart_signal,
    }

    if stop_loss is not None:
        payload["stop_loss"] = stop_loss
    if reason:
        payload["reason"] = reason

    ok, errors = validate_signal(payload)
    if not ok:
        raise ValueError(f"Signal schema invalid: {errors}")

    return payload


class SignalExporter:
    def __init__(self, bus: SignalBus, pair_map_path: Path) -> None:
        self.bus = bus
        self.pair_map = _load_pair_map(pair_map_path)

    def export(self, signal: Dict[str, object]) -> bool:
        return self.bus.push(signal)
