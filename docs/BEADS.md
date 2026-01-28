# BEADS Plan (Task DAG) - Tradegate x Trading Buddy Merge

Legend:
- B# = bead/task
- Depends on = prerequisites

## Beads
B1 - Root Refactor + Merge Layout
- Create/verify folders: docs, beads, configs, scripts, reports
- Move merge planning into repo root
Output: docs/PRD.md, docs/BEADS.md, beads/plan.yaml
Test: Test-Path docs/PRD.md; Test-Path beads/plan.yaml

B2 - Guardrails + Schema + Mapping Spec
Depends on: B1
- Finalize signal schema with required chart_signal object
- Define USD->USDT mapping table
- Add schema validator + guardrail constants
Output: brain/signal_schema.py, configs/pair_map.json
Test: pytest brain/tests/test_schema.py

B3 - Strategy Fleet + Rate Budgeter (Shotgun)
Depends on: B2
- Create configs/strategy_fleet.yaml (many instances)
- Implement rate-limit budgeter (80% cap)
- Add instance manager to scale based on budget
Output: brain/strategy_fleet.py, configs/strategy_fleet.yaml
Test: pytest brain/tests/test_budgeter.py

B4 - Chart Engine (Chart-First)
Depends on: B2
- Build chart layer detection (S/R, trendlines, channels, EMAs, VWAP, Fib)
- Build pattern detectors (breakout, pullback, range, divergence, squeeze)
- Produce chart_signal + confluence score
Output: brain/chart_engine.py
Test: pytest brain/tests/test_chart_engine.py

B5 - Signal Bus (SQLite)
Depends on: B2
- Create signal_bus table with TTL + idempotency
- Implement push/pull/ack APIs
Output: brain/signal_bus.py, shared_data/signals.db
Test: pytest brain/tests/test_bus.py

B6 - Signal Export Adapter (Shadow Mode)
Depends on: B4, B5
- Emit signals from chart engine into bus without touching live Mac
- Ensure schema validation before write
Output: brain/signal_exporter.py
Test: pytest brain/tests/test_exporter.py

B7 - Execution Gateway
Depends on: B2, B5
- Enforce mapping + TTL
- Retry with backoff
- Submit to Freqtrade API
Output: brain/gateway.py
Test: pytest brain/tests/test_gateway.py

B8 - Freqtrade Consumer
Depends on: B5, B7
- Update SidecarStrat to consume bus signals
- Apply stop_loss from payload
Output: freqtrade/user_data/strategies/SidecarStrat.py
Test: pytest brain/tests/test_sidecar.py

B9 - Reporting + Journal
Depends on: B6, B7, B8
- Generate 2-hour report with chart metrics
- Journal outcomes and confluence scores
Output: brain/reporting.py, reports/
Test: pytest brain/tests/test_reporting.py

B10 - Guardrail Tests
Depends on: B2, B5, B7, B8
- Enforce STANDARDS.md constants and names
- Ensure no direct CCXT trading
Output: brain/tests/test_guardrails.py
Test: pytest brain/tests/test_guardrails.py

B11 - Runbook + Scheduler
Depends on: B9, B10
- Add scripts to run plumbing test and 2-hour shotgun test
- Schedule run to finish by 9:00 AM MST
Output: scripts/run_plumbing_test.ps1, scripts/run_2h_test.ps1
Test: powershell -File scripts/run_plumbing_test.ps1

B12 - Stress + Comparison Pack
Depends on: B9
- Stress test rate limits and queue overflow
- Produce comparison pack vs 10-hour baseline
Output: reports/comparison/
Test: powershell -File scripts/build_comparison.ps1
