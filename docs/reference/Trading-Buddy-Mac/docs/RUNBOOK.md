# Runbook

## 0) Safety
- Do **not** modify live Tradegate on Mac while 10‑hour test runs.
- Build in isolated workspace (Windows PC preferred for parallel live test).

## 1) Build (high‑level)
- Create `merge_lab/`
- Implement BEADS tasks B1–B8

## 2) Plumbing Test (5–10 min)
- Start signal engine in shadow mode
- Start bus + gateway + Freqtrade dry‑run
- Confirm signals flow and are executed

## 3) 2‑Hour Paper Test
- Run merged system for 2 hours
- Generate report

## 4) Publish Results
- Push report to GitHub
- Prepare comparison with 10‑hour baseline

