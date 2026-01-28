from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Dict, List


@dataclass
class ReportMetrics:
    start_utc: str
    end_utc: str
    duration_sec: int
    trades_total: int
    trades_per_hour: float
    win_rate: float
    net_pnl: float
    net_pnl_per_hour: float
    fee_drag: float
    max_drawdown: float
    confluence_scores: List[float]
    pattern_counts: Dict[str, int]
    errors: List[str]


@dataclass
class ReportBuilder:
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    confluence_scores: List[float] = field(default_factory=list)
    pattern_counts: Counter = field(default_factory=Counter)
    errors: List[str] = field(default_factory=list)
    trades_total: int = 0

    def record_signal(self, chart_signal: Dict[str, object]) -> None:
        score = float(chart_signal.get("confluence_score", 0))
        self.confluence_scores.append(score)
        pattern = str(chart_signal.get("pattern", "unknown"))
        self.pattern_counts[pattern] += 1

    def record_submission(self) -> None:
        self.trades_total += 1

    def record_error(self, message: str) -> None:
        self.errors.append(message)

    def build(self) -> ReportMetrics:
        end_time = datetime.now(timezone.utc)
        duration_sec = int((end_time - self.start_time).total_seconds())
        trades_per_hour = self.trades_total / max(duration_sec / 3600, 1e-6)
        return ReportMetrics(
            start_utc=self.start_time.isoformat(),
            end_utc=end_time.isoformat(),
            duration_sec=duration_sec,
            trades_total=self.trades_total,
            trades_per_hour=round(trades_per_hour, 4),
            win_rate=0.0,
            net_pnl=0.0,
            net_pnl_per_hour=0.0,
            fee_drag=0.0,
            max_drawdown=0.0,
            confluence_scores=self.confluence_scores,
            pattern_counts=dict(self.pattern_counts),
            errors=self.errors,
        )


def write_report(metrics: ReportMetrics, out_dir: Path, test_name: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    json_path = out_dir / f"{test_name}-{timestamp}.json"
    md_path = out_dir / f"{test_name}-{timestamp}.md"

    json_path.write_text(json.dumps(metrics.__dict__, indent=2), encoding="utf-8")

    md_lines = [
        "# Test Report",
        "",
        f"Start (UTC): {metrics.start_utc}",
        f"End (UTC): {metrics.end_utc}",
        f"Duration (sec): {metrics.duration_sec}",
        "",
        "## Summary Metrics",
        f"- Trades total: {metrics.trades_total}",
        f"- Trades/hour: {metrics.trades_per_hour}",
        f"- Win rate: {metrics.win_rate}",
        f"- Net PnL: {metrics.net_pnl}",
        f"- Net PnL/hour: {metrics.net_pnl_per_hour}",
        f"- Fee drag: {metrics.fee_drag}",
        f"- Max drawdown: {metrics.max_drawdown}",
        "",
        "## Chart Metrics",
        f"- Confluence scores: {metrics.confluence_scores}",
        f"- Pattern counts: {metrics.pattern_counts}",
        "",
        "## Errors",
    ]

    if metrics.errors:
        md_lines.extend([f"- {err}" for err in metrics.errors])
    else:
        md_lines.append("- None")

    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    return json_path
