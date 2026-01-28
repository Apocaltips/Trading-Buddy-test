from __future__ import annotations

from brain.strategy_fleet import FleetConfig, build_instances, budget_instances


def test_budget_instances():
    config = FleetConfig(
        rate_limit_per_min=100,
        instance_cost_per_min=5,
        confluence_min=70,
        pairs=["BTC/USDT", "ETH/USDT"],
        strategies=[{"name": "trend_pullback", "timeframes": ["5m", "15m"]}],
    )
    instances = build_instances(config)
    capped = budget_instances(instances, config.rate_limit_per_min, config.instance_cost_per_min)
    assert len(capped) <= len(instances)
    expected = min(len(instances), int(100 * 0.8) // 5)
    assert len(capped) == expected
