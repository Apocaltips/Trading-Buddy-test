# Architecture Decisions

## D1 — Build in isolated workspace
- Prevents contamination of live 10‑hour run.

## D2 — Use signal bus with TTL + idempotency
- Decouples brain from body and avoids duplicate execution.

## D3 — Use Freqtrade for execution (dry‑run)
- Reuses proven order handling logic.

## D4 — Run parallel tests from different public IPs
- Avoids shared API rate‑limit collisions.

