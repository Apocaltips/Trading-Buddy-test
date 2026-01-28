# Architecture

## Data Flow (High Level)
```
[Market Data APIs]
      |
      v
[Chart-First Signal Engine]
  - multi-instance strategies
  - multi-timeframe chart patterns
  - confluence scoring (chart + trend + vol + sentiment)
      |
      v
[Signal Bus]
  - TTL enforcement
  - idempotency
      |
      v
[Execution Gateway]
  - pair mapping (USD -> USDT)
  - auth + retry
      |
      v
[Freqtrade Body (dry-run)]
  - order execution
  - stoploss handling
      |
      v
[Reports + Journal]
```

## Component Responsibilities
### Chart-First Signal Engine
- Compute signals per instance
- Detect chart layers and patterns
- Emit standardized signal payloads with chart_signal details

### Signal Bus
- Store signals durably
- Enforce TTL and idempotency

### Execution Gateway
- Map symbols to exchange pair format
- Validate schema and TTL
- Submit to Freqtrade API

### Freqtrade Body
- Dry-run execution
- Pull stop_loss from signal bus payload

### Reporting Layer
- Build run report
- Output metrics for comparison

## Isolation Strategy
- Build and test in this Windows workspace
- No edits to live Tradegate during the 10-hour run
- Run in parallel only if using a different public IP
