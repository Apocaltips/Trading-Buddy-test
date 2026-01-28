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
        conn.commit()


def main() -> None:
    init_db(resolve_db_path())


if __name__ == "__main__":
    main()