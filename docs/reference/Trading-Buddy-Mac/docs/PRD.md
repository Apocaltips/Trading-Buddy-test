# PRD — Tradegate × Trading‑Buddy Merge

**Owner:** Apocaltips
**Author:** Codex (Nova)
**Status:** Draft for approval
**Scope:** Docs + build plan only (no live changes yet)

## 1) Goal
Build a merged trading system that combines:
- Tradegate’s multi‑instance **signal generation + gating** (trend/vol/sentiment/chart), and
- Trading‑Buddy’s **execution body** (Freqtrade dry‑run), plus
- Clear monitoring + reporting to compare against the current 10‑hour baseline.

The merged system must be buildable **in isolation** (e.g., Windows PC) without touching the live Mac run, then deployable to Mac when ready.

## 2) Non‑Goals
- Live trading
- Full strategy optimization
- Rewriting Tradegate internals
- Building new ML models

## 3) Users & Use Cases
**Primary user:** Apocaltips
- Start a 2‑hour paper test with multiple instances/strategies
- Compare it to the 10‑hour Mac baseline

**Secondary user:** Another Codex CLI agent
- Pull this repo and start building with zero extra context

## 4) System Overview
### 4.1 Components
1) **Signal Engine (Tradegate)**
   - Multi‑instance strategy evaluation
   - Gating: trend, vol, sentiment, chart
   - Outputs standardized signals

2) **Signal Bus**
   - Durable queue (SQLite or file‑based)
   - TTL + idempotency

3) **Execution Gateway**
   - Pair mapping (USD → USDT)
   - Auth + rate limit handling
   - Submits trades to Freqtrade API

4) **Execution Body (Freqtrade)**
   - Dry‑run execution
   - Stop‑loss derived from bus signals

5) **Monitoring + Reporting**
   - Fleet status (Tradegate dashboard)
   - 2‑hour test report (PnL/hour, win rate, fee drag)

## 5) Functional Requirements
### 5.1 Signal Engine
- Preserve Tradegate gating logic
- Preserve multi‑instance configs
- Emit signal events **without** changing the running Mac system

### 5.2 Signal Bus
- Standard JSON schema with required fields
- TTL enforcement (drop expired signals)
- Idempotency (duplicate ID ignored)

### 5.3 Execution Gateway
- Pair mapping layer
- Submit to Freqtrade API
- Retry with backoff on transient errors

### 5.4 Execution Body
- Freqtrade in dry‑run mode
- Sidecar strategy reads bus signals
- Custom stoploss from signal payload

### 5.5 Reporting
- 2‑hour test report with:
  - Trades/hour
  - Net PnL/hour
  - Win rate
  - Fee drag %
  - Max drawdown

## 6) Non‑Functional Requirements
- **Isolation:** no changes to live Tradegate during the 10‑hour run
- **Reproducibility:** each test generates a report
- **Auditability:** every signal can be traced to execution outcome

## 7) Testing Requirements
- Unit tests for mapping + TTL + idempotency
- Integration test for bus → gateway → Freqtrade
- E2E 2‑hour dry‑run

## 8) Acceptance Criteria (Definition of Done)
- All required docs exist and are complete
- Signal bus operational
- Execution gateway submitting to Freqtrade
- 2‑hour test run produces report
- Comparison pack prepared for 10‑hour baseline

## 9) Constraints & Risks
- Public API rate limits (Gemini/CoinGecko/Binance) are IP‑based
- Running two live systems from same IP will contaminate data
- 2‑hour run is a smoke test; not statistically comparable to 10‑hour run

## 10) Out‑of‑Band Notes
If parallel live tests are required, **run the merged system from a different public IP** (Windows PC is suitable).

