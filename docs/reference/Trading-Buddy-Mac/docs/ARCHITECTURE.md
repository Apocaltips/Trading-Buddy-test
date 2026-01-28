# Architecture

## Data Flow (High‑Level)
```
[Market Data APIs]
      |
      v
[Tradegate Signal Engine]
  - multi-instance strategies
  - trend/vol/sentiment/chart gating
      |
      v
[Signal Bus]
  - TTL
  - idempotency
      |
      v
[Execution Gateway]
  - pair mapping (USD → USDT)
  - auth + retry
      |
      v
[Freqtrade Body (dry-run)]
  - order execution
  - stoploss handling
      |
      v
[Reports + Dashboards]
```

## Component Responsibilities
### Tradegate Signal Engine
- Compute signals per instance
- Apply gating
- Emit standardized signal payloads

### Signal Bus
- Store signals durably
- Ensure **exactly‑once** execution via idempotency

### Execution Gateway
- Map symbols to exchange pair format
- Enforce TTL
- Submit to Freqtrade API

### Freqtrade Body
- Dry‑run execution
- Pull stop‑loss from signal bus

### Reporting Layer
- Build 2‑hour test report
- Output metrics for comparison

## Isolation Strategy
- Build and test in a **separate workspace**
- No edits to live Tradegate during 10‑hour run
- Use Windows PC for live 2‑hour test in parallel (different public IP)

