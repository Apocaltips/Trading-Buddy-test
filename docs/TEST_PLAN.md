# Test Plan

## Unit Tests
- Signal schema validation (including chart_signal)
- Chart pattern detection
- Confluence scoring
- TTL enforcement
- Idempotency (duplicate IDs ignored)
- Pair mapping table (USD -> USDT)
- Rate budgeter (80 percent cap)

## Guardrail Tests
- Required columns and df_* names
- DB path and Freqtrade API constants
- Ensure Brain never trades via CCXT

## Integration Tests
- Signal -> bus -> gateway -> Freqtrade API (mocked)
- Sidecar reads bus and applies stop_loss

## E2E
- 5-10 minute plumbing test (low load)
- Run until target end time (10:00 AM MST) with shotgun fleet

## Required Artifacts
- `reports/merged-<timestamp>.json`
- `reports/merged-<timestamp>.md`
