from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import sqlite3
import requests

from .constants import API_URL, DB_PATH


def _resolve_db_path() -> Path:
    if Path(DB_PATH).parent.is_dir():
        return Path(DB_PATH)
    return Path(__file__).resolve().parents[1] / "shared_data" / "signals.db"


@dataclass
class ExecutionClient:
    db_path: Path = _resolve_db_path()
    api_url: str = API_URL

    def stage_signal(self, pair: str, stop_loss: float, reason: str) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS active_signals ("
                "pair TEXT, "
                "stop_loss REAL, "
                "reason TEXT"
                ")"
            )
            conn.execute("DELETE FROM active_signals WHERE pair = ?", (pair,))
            conn.execute(
                "INSERT INTO active_signals (pair, stop_loss, reason) VALUES (?, ?, ?)",
                (pair, float(stop_loss), reason),
            )
            conn.commit()

    def trigger_buy(self, pair: str) -> Dict[str, Any]:
        url = f"{self.api_url}/forcebuy"
        response = requests.post(url, json={"pair": pair}, timeout=10)
        response.raise_for_status()
        try:
            return response.json()
        except ValueError:
            return {"status": "ok", "text": response.text}
