from __future__ import annotations

import argparse
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
import time

from brain.chart_engine import analyze_chart
from brain.data import fetch_ohlcv
from brain.gateway import ExecutionGateway
from brain.reporting import ReportBuilder, write_report
from brain.signal_bus import SignalBus
from brain.signal_exporter import SignalExporter, build_signal
from brain.strategy_fleet import build_instances, budget_instances, load_fleet_config


def _signal_bps(df_candles):
    if len(df_candles) < 2:
        return 0.0
    prev_close = float(df_candles["close"].iloc[-2])
    last_close = float(df_candles["close"].iloc[-1])
    if prev_close == 0:
        return 0.0
    return (last_close - prev_close) / prev_close * 10000


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration-min", type=int, required=True)
    parser.add_argument("--fleet-config", type=str, default="configs/strategy_fleet.yaml")
    parser.add_argument("--pair-map", type=str, default="configs/pair_map.json")
    parser.add_argument("--ttl-sec", type=int, default=120)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    fleet_path = root / args.fleet_config
    pair_map_path = root / args.pair_map

    config = load_fleet_config(fleet_path)
    instances = build_instances(config)
    instances = budget_instances(instances, config.rate_limit_per_min, config.instance_cost_per_min)

    bus = SignalBus()
    exporter = SignalExporter(bus, pair_map_path)
    gateway = ExecutionGateway(bus=bus, pair_map_path=pair_map_path)
    reporter = ReportBuilder()

    start_time = datetime.now(timezone.utc)
    end_time = start_time + timedelta(minutes=args.duration_min)

    allow_fallback = os.getenv("DISABLE_OHLCV_FALLBACK") != "1"

    while datetime.now(timezone.utc) < end_time:
        loop_start = time.time()
        for inst in instances:
            try:
                df_candles = fetch_ohlcv(inst.pair, timeframe=inst.timeframe, limit=250, allow_fallback=allow_fallback)
            except Exception as exc:
                reporter.record_error(f"fetch_failed:{inst.pair}:{inst.timeframe}:{exc}")
                continue

            result = analyze_chart(df_candles, inst.timeframe, inst.strategy)
            if not result.chart_signal:
                continue

            reporter.record_signal(result.chart_signal)
            confluence = float(result.chart_signal.get("confluence_score", 0))
            if not result.signal or confluence < config.confluence_min:
                continue

            price_snapshot = float(df_candles["close"].iloc[-1])
            invalidation = float(result.chart_signal.get("invalidation_price", 0))
            stop_loss = None
            if invalidation > 0 and price_snapshot > 0:
                stop_loss = abs(price_snapshot - invalidation) / price_snapshot

            try:
                signal = build_signal(
                    instance=f"{inst.strategy}_{inst.timeframe}",
                    strategy=inst.strategy,
                    pair=inst.pair,
                    timeframe=inst.timeframe,
                    side=result.side,
                    price_snapshot=price_snapshot,
                    chart_signal=result.chart_signal,
                    signal_bps=_signal_bps(df_candles),
                    ttl_sec=args.ttl_sec,
                    pair_map=exporter.pair_map,
                    stop_loss=stop_loss,
                    reason=f"{inst.strategy} chart signal",
                )
                exporter.export(signal)
            except Exception as exc:
                reporter.record_error(f"export_failed:{inst.pair}:{inst.timeframe}:{exc}")

        gateway_result = gateway.process_once(limit=200)
        for _ in range(gateway_result.submitted):
            reporter.record_submission()
        for err in gateway_result.errors:
            reporter.record_error(err)

        elapsed = time.time() - loop_start
        sleep_for = max(0, 60 - elapsed)
        time.sleep(sleep_for)

    metrics = reporter.build()
    write_report(metrics, root / "reports", "merged-until-10am")


if __name__ == "__main__":
    main()
