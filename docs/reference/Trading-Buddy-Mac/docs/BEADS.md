# BEADS Plan (Task DAG)

## Legend
- **B#** = bead/task
- **Depends on** = prerequisites

## Beads
**B1 — Workspace Setup**
- Create isolated build folder (e.g., `merge_lab/`).
- Clone required repos.
- No changes to live Mac Tradegate.

**B2 — Signal Schema + Mapping Spec**
- Finalize JSON schema and USD→USDT mapping table.

**B3 — Signal Bus Implementation**
- SQLite or file‑based queue with TTL + idempotency.

**B4 — Tradegate Signal Export Adapter**
- Emit signals into bus in shadow mode.

**B5 — Execution Gateway**
- Mapping + TTL enforcement + retry strategy.

**B6 — Freqtrade Consumer**
- Sidecar strategy reads bus and executes (dry‑run).

**B7 — Reporting + Metrics**
- 2‑hour report generator.

**B8 — Runbook + Safety**
- Start/stop commands, health checks.

## Dependencies
- B3 depends on B2
- B4 depends on B2
- B5 depends on B2 + B3
- B6 depends on B3 + B5
- B7 depends on B4 + B5 + B6
- B8 can run in parallel and finalize last

