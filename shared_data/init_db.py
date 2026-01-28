#!/usr/bin/env python3
import sqlite3
from pathlib import Path

DB_PATH = "/shared_data/signals.db"


def resolve_db_path() -> Path:
    if Path(DB_PATH).parent.is_dir():
        return Path(DB_PATH)
    return Path(__file__).resolve().parent / "signals.db"


def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS active_signals ("
            "pair TEXT, "
            "stop_loss REAL, "
            "reason TEXT"
            ")"
        )
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


def main() -> None:
    init_db(resolve_db_path())


if __name__ == "__main__":
    main()
