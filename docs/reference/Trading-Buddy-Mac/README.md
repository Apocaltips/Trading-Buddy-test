# Trading-Buddy-Mac

Docs-only repo for the Tradegate × Trading‑Buddy merge build.

This repo exists so any Codex CLI instance (Mac or Windows) can pull a **complete, in‑depth plan** and start building immediately **without touching the live 10‑hour test** on the Mac Studio.

## What’s in here
- `docs/PRD.md` — Product requirements and acceptance criteria.
- `docs/ARCHITECTURE.md` — System design + data flow.
- `docs/SIGNAL_SCHEMA.md` — Signal bus schema + examples.
- `docs/BEADS.md` — Task DAG (parallelizable work plan).
- `docs/TEST_PLAN.md` — Unit/integration/E2E tests.
- `docs/RUNBOOK.md` — How to build, run, and test safely.
- `docs/COMPARISON_PLAN.md` — Metrics for comparing 10‑hour vs 2‑hour runs.
- `docs/RISKS.md` — Known risks + mitigations.
- `docs/GETTING_STARTED_WINDOWS.md` — Quick start for Windows Codex CLI.
- `docs/TROUBLESHOOTING.md` — Common errors + fixes.
- `docs/ENV_VARS.md` — Environment variables.
- `docs/PREFLIGHT_CHECKLIST.md` — Pre‑test checklist.
- `docs/PAIR_MAPPING_TABLE.md` — USD → USDT map.
- `docs/REPORT_TEMPLATE.md` — 2‑hour report template.
- `beads/plan.yaml` — Machine‑readable BEADS plan.

## Golden Rules
1) **Do not modify live Tradegate while the 10‑hour run is active.**
2) **Build in an isolated workspace** (Windows machine is ideal for parallel live testing).
3) **Paper/dry‑run only** until results prove the merge is stable.

## Quick Start (for another Codex CLI)
1) Read `docs/PRD.md` and `docs/BEADS.md`.
2) Create a new workspace folder (example: `merge_lab/`).
3) Implement tasks from `beads/plan.yaml` in dependency order.
4) Run a **short plumbing test** (5–10 min).
5) Run a **2‑hour paper test** (if not sharing the Mac’s public IP).
6) Push results back to GitHub for review.
