from __future__ import annotations

from pathlib import Path

from brain.reporting import ReportBuilder, write_report


def test_reporting_output(tmp_path: Path):
    builder = ReportBuilder()
    builder.record_signal({"pattern": "test", "confluence_score": 80})
    builder.record_submission()
    metrics = builder.build()
    path = write_report(metrics, tmp_path, "test-report")
    assert path.exists()
