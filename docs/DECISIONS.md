# Architecture Decisions

## D1 - Use repo root as merge workspace
- Avoids split context and matches docs.

## D2 - Chart-first signals
- Chart patterns drive signals; indicators are filters.

## D3 - Use signal bus with TTL + idempotency
- Decouples brain from body and avoids duplicate execution.

## D4 - Use Freqtrade for execution (dry-run)
- Reuses proven order handling logic.

## D5 - Run parallel tests from different public IPs
- Avoids shared API rate-limit collisions.
