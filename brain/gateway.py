from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Dict, List, Tuple
import time

import os
import requests

from .constants import API_URL
from .signal_bus import SignalBus


def _load_pair_map(path: Path) -> Dict[str, str]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


@dataclass
class GatewayResult:
    processed: int
    submitted: int
    rejected: int
    errors: List[str]


@dataclass
class ExecutionGateway:
    bus: SignalBus
    pair_map_path: Path
    api_url: str = API_URL
    max_retries: int = 3
    backoff_sec: float = 1.0

    def __post_init__(self) -> None:
        self.pair_map = _load_pair_map(self.pair_map_path)

    def _submit(self, pair: str, side: str) -> None:
        endpoint = "forcebuy" if side == "buy" else "forcesell"
        url = f"{self.api_url}/{endpoint}"
        username = os.getenv("FT_USERNAME")
        password = os.getenv("FT_PASSWORD")
        auth = (username, password) if username and password else None
        response = requests.post(url, json={"pair": pair}, timeout=10, auth=auth)
        response.raise_for_status()

    def _validate_mapping(self, symbol: str, pair: str) -> bool:
        mapped = self.pair_map.get(symbol)
        return bool(mapped and mapped == pair)

    def process_once(self, limit: int = 50) -> GatewayResult:
        errors: List[str] = []
        submitted = 0
        rejected = 0
        signals = self.bus.fetch_pending(limit=limit)

        for signal in signals:
            if not self._validate_mapping(str(signal.get("symbol")), str(signal.get("pair"))):
                rejected += 1
                errors.append(f"mapping_mismatch:{signal.get('symbol')}->{signal.get('pair')}")
                self.bus.mark_consumed([signal.get("id")])
                continue

            side = str(signal.get("side"))
            pair = str(signal.get("pair"))
            success = False
            for attempt in range(self.max_retries):
                try:
                    self._submit(pair, side)
                    success = True
                    submitted += 1
                    break
                except requests.RequestException as exc:
                    errors.append(f"submit_failed:{pair}:{exc}")
                    time.sleep(self.backoff_sec * (attempt + 1))

            self.bus.mark_consumed([signal.get("id")])
            if not success:
                rejected += 1

        return GatewayResult(
            processed=len(signals),
            submitted=submitted,
            rejected=rejected,
            errors=errors,
        )
