from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
import json
from pathlib import Path
from typing import Dict, Iterable, List
import sqlite3

from .constants import DB_PATH
from .signal_schema import validate_signal


def _resolve_db_path() -> Path:
    if Path(DB_PATH).parent.is_dir():
        return Path(DB_PATH)
    return Path(__file__).resolve().parents[1] / "shared_data" / "signals.db"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_ts(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def _expired(ts: str, ttl_sec: int) -> bool:
    try:
        dt = _parse_ts(ts)
    except ValueError:
        return True
    return _utc_now() > dt + timedelta(seconds=int(ttl_sec))


@dataclass
class SignalBus:
    db_path: Path = _resolve_db_path()

    def _connect(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        conn.execute(
            "CREATE TABLE IF NOT EXISTS signal_bus ("
            "id TEXT PRIMARY KEY, "
            "ts_utc TEXT, "
            "source TEXT, "
            "instance TEXT, "
            "strategy TEXT, "
            "symbol TEXT, "
            "pair TEXT, "
            "side TEXT, "
            "intent TEXT, "
            "timeframe TEXT, "
            "signal_bps REAL, "
            "price_snapshot REAL, "
            "ttl_sec INTEGER, "
            "chart_signal_json TEXT, "
            "stop_loss REAL, "
            "take_profit REAL, "
            "notional_usd REAL, "
            "qty REAL, "
            "vol_bps REAL, "
            "sentiment_score REAL, "
            "reason TEXT, "
            "consumed INTEGER DEFAULT 0, "
            "inserted_at TEXT"
            ")"
        )
        conn.commit()
        return conn

    def push(self, signal: Dict[str, object]) -> bool:
        ok, errors = validate_signal(signal)
        if not ok:
            raise ValueError(f"Signal schema invalid: {errors}")
        if _expired(str(signal["ts_utc"]), int(signal["ttl_sec"])):
            return False

        payload = dict(signal)
        chart_signal = payload.get("chart_signal", {})
        payload["chart_signal_json"] = json.dumps(chart_signal, separators=(",", ":"))

        with self._connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO signal_bus ("
                "id, ts_utc, source, instance, strategy, symbol, pair, side, intent, timeframe, "
                "signal_bps, price_snapshot, ttl_sec, chart_signal_json, stop_loss, take_profit, "
                "notional_usd, qty, vol_bps, sentiment_score, reason, consumed, inserted_at"
                ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)"
                ,
                (
                    payload.get("id"),
                    payload.get("ts_utc"),
                    payload.get("source"),
                    payload.get("instance"),
                    payload.get("strategy"),
                    payload.get("symbol"),
                    payload.get("pair"),
                    payload.get("side"),
                    payload.get("intent"),
                    payload.get("timeframe"),
                    payload.get("signal_bps"),
                    payload.get("price_snapshot"),
                    payload.get("ttl_sec"),
                    payload.get("chart_signal_json"),
                    payload.get("stop_loss"),
                    payload.get("take_profit"),
                    payload.get("notional_usd"),
                    payload.get("qty"),
                    payload.get("vol_bps"),
                    payload.get("sentiment_score"),
                    payload.get("reason"),
                    _utc_now().isoformat(),
                ),
            )
            conn.commit()
            return conn.total_changes > 0

    def purge_expired(self) -> int:
        removed = 0
        with self._connect() as conn:
            cur = conn.execute(
                "SELECT id, ts_utc, ttl_sec FROM signal_bus WHERE consumed = 0"
            )
            rows = cur.fetchall()
            expired_ids = [row[0] for row in rows if _expired(row[1], row[2])]
            if expired_ids:
                conn.executemany(
                    "DELETE FROM signal_bus WHERE id = ?",
                    [(signal_id,) for signal_id in expired_ids],
                )
                removed = conn.total_changes
            conn.commit()
        return removed

    def fetch_pending(self, limit: int = 100) -> List[Dict[str, object]]:
        self.purge_expired()
        with self._connect() as conn:
            cur = conn.execute(
                "SELECT id, ts_utc, source, instance, strategy, symbol, pair, side, intent, timeframe, "
                "signal_bps, price_snapshot, ttl_sec, chart_signal_json, stop_loss, take_profit, "
                "notional_usd, qty, vol_bps, sentiment_score, reason "
                "FROM signal_bus WHERE consumed = 0 ORDER BY inserted_at ASC LIMIT ?",
                (int(limit),),
            )
            rows = cur.fetchall()

        signals: List[Dict[str, object]] = []
        for row in rows:
            chart_signal = {}
            try:
                chart_signal = json.loads(row[13] or "{}")
            except json.JSONDecodeError:
                chart_signal = {}
            signals.append(
                {
                    "id": row[0],
                    "ts_utc": row[1],
                    "source": row[2],
                    "instance": row[3],
                    "strategy": row[4],
                    "symbol": row[5],
                    "pair": row[6],
                    "side": row[7],
                    "intent": row[8],
                    "timeframe": row[9],
                    "signal_bps": row[10],
                    "price_snapshot": row[11],
                    "ttl_sec": row[12],
                    "chart_signal": chart_signal,
                    "stop_loss": row[14],
                    "take_profit": row[15],
                    "notional_usd": row[16],
                    "qty": row[17],
                    "vol_bps": row[18],
                    "sentiment_score": row[19],
                    "reason": row[20],
                }
            )
        return signals

    def mark_consumed(self, ids: Iterable[str]) -> int:
        ids = list(ids)
        if not ids:
            return 0
        with self._connect() as conn:
            conn.executemany(
                "UPDATE signal_bus SET consumed = 1 WHERE id = ?",
                [(signal_id,) for signal_id in ids],
            )
            conn.commit()
            return conn.total_changes
