# Runbook

## 0) Safety
- Do not modify live Tradegate on the Mac while the 10-hour run is active.
- Build and test on this Windows workspace.
- Dry-run only.

## 1) Build (high level)
- Implement BEADS tasks B1 through B12.

## 2) Plumbing Test (5-10 min)
- Start chart engine in shadow mode
- Start bus + gateway + Freqtrade dry-run
- Confirm signals flow and are executed

## 3) Run Until 10:00 AM MST
- Run shotgun test from current time to 10:00 AM MST
- Generate report and journal

## 4) Publish Results
- Save report under reports/
- Prepare comparison with 10-hour baseline
