# Test Plan

## Unit Tests
- Signal schema validation
- TTL enforcement
- Idempotency (duplicate IDs ignored)
- Pair mapping table (USD → USDT)

## Integration Tests
- Signal written → bus → gateway picks up
- Gateway → Freqtrade API returns success
- Auth configuration validated (no 401)

## E2E
- 5–10 min plumbing test (low load)
- 2‑hour dry‑run test across multiple instances

## Required Artifacts
- `reports/merged-2h-<timestamp>.json`
- `reports/merged-2h-<timestamp>.md`

