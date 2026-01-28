from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List

try:
    import yaml
except Exception:  # pragma: no cover - optional dependency
    yaml = None


@dataclass(frozen=True)
class StrategyInstance:
    strategy: str
    timeframe: str
    pair: str


@dataclass
class FleetConfig:
    rate_limit_per_min: int
    instance_cost_per_min: int
    confluence_min: int
    pairs: List[str]
    strategies: List[Dict[str, object]]


DEFAULT_CONFIG = {
    "rate_limit_per_min": 1200,
    "instance_cost_per_min": 1,
    "confluence_min": 70,
    "pairs": ["BTC/USDT", "ETH/USDT"],
    "strategies": [
        {"name": "trend_pullback", "timeframes": ["5m", "15m"]},
        {"name": "breakout_retest", "timeframes": ["5m"]},
    ],
}


def load_fleet_config(path: Path) -> FleetConfig:
    if not path.exists():
        data = DEFAULT_CONFIG
    else:
        if yaml is None:
            data = DEFAULT_CONFIG
        else:
            with path.open("r", encoding="utf-8") as handle:
                data = yaml.safe_load(handle) or DEFAULT_CONFIG

    return FleetConfig(
        rate_limit_per_min=int(data.get("rate_limit_per_min", 1200)),
        instance_cost_per_min=int(data.get("instance_cost_per_min", 1)),
        confluence_min=int(data.get("confluence_min", 70)),
        pairs=list(data.get("pairs", [])),
        strategies=list(data.get("strategies", [])),
    )


def build_instances(config: FleetConfig) -> List[StrategyInstance]:
    instances: List[StrategyInstance] = []
    for strategy in config.strategies:
        name = str(strategy.get("name"))
        timeframes = strategy.get("timeframes", [])
        for timeframe in timeframes:
            for pair in config.pairs:
                instances.append(StrategyInstance(strategy=name, timeframe=str(timeframe), pair=str(pair)))
    return instances


def budget_instances(instances: Iterable[StrategyInstance], rate_limit_per_min: int, instance_cost_per_min: int) -> List[StrategyInstance]:
    if rate_limit_per_min <= 0 or instance_cost_per_min <= 0:
        return []
    capacity = int(rate_limit_per_min * 0.8) // int(instance_cost_per_min)
    if capacity <= 0:
        return []
    return list(instances)[:capacity]
