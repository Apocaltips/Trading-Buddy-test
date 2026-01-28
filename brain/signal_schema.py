from __future__ import annotations

from datetime import datetime
from typing import Dict, Iterable, List, Tuple
import uuid

REQUIRED_FIELDS = {
    "id",
    "ts_utc",
    "source",
    "instance",
    "strategy",
    "symbol",
    "pair",
    "side",
    "intent",
    "timeframe",
    "signal_bps",
    "price_snapshot",
    "ttl_sec",
    "chart_signal",
}

REQUIRED_CHART_FIELDS = {
    "pattern",
    "structure_level",
    "timeframes",
    "confluence_score",
    "invalidation_price",
    "lines",
}


def _is_iso8601(value: str) -> bool:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def _is_uuid(value: str) -> bool:
    try:
        uuid.UUID(str(value))
        return True
    except (ValueError, TypeError):
        return False


def validate_signal(signal: Dict[str, object]) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    missing = REQUIRED_FIELDS - set(signal.keys())
    if missing:
        errors.append(f"missing_fields: {sorted(missing)}")
        return False, errors

    if not _is_uuid(str(signal.get("id"))):
        errors.append("id_not_uuid")

    ts = str(signal.get("ts_utc"))
    if not _is_iso8601(ts):
        errors.append("ts_utc_not_iso8601")

    side = signal.get("side")
    if side not in {"buy", "sell"}:
        errors.append("side_invalid")

    intent = signal.get("intent")
    if intent not in {"enter", "exit", "reduce"}:
        errors.append("intent_invalid")

    chart_signal = signal.get("chart_signal")
    if not isinstance(chart_signal, dict):
        errors.append("chart_signal_missing_or_invalid")
        return False, errors

    missing_chart = REQUIRED_CHART_FIELDS - set(chart_signal.keys())
    if missing_chart:
        errors.append(f"chart_signal_missing_fields: {sorted(missing_chart)}")

    confluence = chart_signal.get("confluence_score")
    try:
        confluence_val = float(confluence)
        if confluence_val < 0 or confluence_val > 100:
            errors.append("confluence_out_of_range")
    except (TypeError, ValueError):
        errors.append("confluence_not_numeric")

    timeframes = chart_signal.get("timeframes")
    if not isinstance(timeframes, Iterable) or isinstance(timeframes, (str, bytes)):
        errors.append("timeframes_invalid")
    else:
        if len(list(timeframes)) == 0:
            errors.append("timeframes_empty")

    return len(errors) == 0, errors
