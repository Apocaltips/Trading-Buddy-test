# PRD - Tradegate x Trading Buddy Merge (Chart-First)

Owner: Apocaltips
Author: Codex (Nova)
Status: Draft for approval
Scope: Build plan + implementation for merged system (dry-run only)

## 1) Goal
Build a merged trading system that combines:
- Tradegate-style multi-instance signal generation with chart-first gating, and
- Trading Buddy execution (Freqtrade dry-run), plus
- Monitoring and reporting to compare against the current 10-hour Mac baseline.

The merged system must be buildable in isolation on this Windows PC without touching the live Mac Studio run.

## 2) Non-Goals
- Live trading
- Full strategy optimization
- New ML models
- Rewriting Tradegate internals

## 3) Baseline + Success Criteria
Baseline: 10-hour Mac paper run.
Success means:
- 2-hour dry-run on this PC completes without errors
- Reports are generated and reproducible
- Guardrails prevent context drift and unsafe behavior

## 4) Constraints
- API rate limits are IP-based. Parallel runs must use different public IPs.
- No changes to live Tradegate on the Mac while the 10-hour run is active.
- Must follow STANDARDS.md naming + paths.
- Brain never trades via CCXT directly. Only Freqtrade API.

## 5) System Overview
### 5.1 Components
1) Chart-First Signal Engine
   - Multi-instance strategy evaluation
   - Multi-timeframe chart patterns and line-based structure
   - Confluence scoring (chart + trend + vol + sentiment)

2) Signal Bus
   - SQLite queue with TTL and idempotency

3) Execution Gateway
   - Pair mapping (USD -> USDT)
   - TTL enforcement + retry with backoff
   - Freqtrade API submission

4) Execution Body (Freqtrade)
   - Dry-run execution
   - Stop-loss derived from signal payload

5) Reporting + Journal
   - 2-hour test report
   - Trade journaling with chart reason codes

## 6) Functional Requirements
### 6.1 Chart-First Signal Engine
The engine must be chart-driven and explainable.
Required chart layers (minimum v1):
- Swing support/resistance lines (recent highs/lows)
- Trendlines and channels
- EMA 20/50/200 alignment
- VWAP and simple pivot points
- Fibonacci retracement levels (0.382, 0.5, 0.618)

Required chart patterns (minimum v1):
- Breakout + retest
- Pullback to structure
- Range bounce
- Divergence reversal
- Volatility squeeze release

Chart signals must include invalidation level and confluence score.
Indicators may be used as filters only (not the primary trigger).

### 6.2 Strategy Fleet (Shotgun)
We will test as many instances as the rate-limit budget allows, using a config-driven fleet.
A rate budgeter will compute max instances from the exchange rate limit and scale up until 80% of the budget.

Initial strategy matrix (v1):
- Trend pullback (5m, 15m) - EMA alignment + structure
- Breakout + retest (5m) - range break + volume
- Range bounce (15m) - S/R lines
- Mean reversion (5m) - BB + RSI filter
- VWAP reversion (1m, 5m)
- Momentum continuation (5m) - HH/HL + trendline
- Divergence reversal (15m)
- Volatility squeeze (15m) - BB squeeze release
- Support/resistance flip (5m)
- Channel bounce (15m)

Instances are expanded across a configurable pair list (top liquid USDT pairs).

### 6.3 Signal Schema (Required Fields)
Each signal is a JSON payload with required fields:
- id (uuid)
- ts_utc (ISO 8601)
- source ("tradegate" or "chart_engine")
- instance
- strategy
- symbol (e.g., "BTC-USD")
- pair (e.g., "BTC/USDT")
- side (buy | sell)
- intent (enter | exit | reduce)
- timeframe
- signal_bps
- price_snapshot
- ttl_sec
- chart_signal (object; required)

Required chart_signal fields:
- pattern
- structure_level
- timeframes (list)
- confluence_score (0-100)
- invalidation_price
- lines (list of {type, price, timeframe})

Optional:
- stop_loss
- take_profit
- notional_usd or qty
- vol_bps
- sentiment_score
- reason (human readable)

### 6.4 Signal Bus
- Store signals durably in SQLite
- TTL enforcement (drop expired)
- Idempotency (duplicate ID ignored)
- Fail closed if schema invalid

### 6.5 Execution Gateway
- Enforce mapping and TTL
- Retry with backoff on transient errors
- Log all rejects with reason

### 6.6 Freqtrade Consumer
- Dry-run only
- Reads bus signals
- Uses stop_loss from payload

### 6.7 Reporting + Journal
- 2-hour report must include:
  - Trades/hour
  - Net PnL/hour
  - Win rate
  - Fee drag percent
  - Max drawdown
  - Confluence score distribution
  - Top chart patterns by outcome

## 7) Guardrails to Prevent Context Drift
- Follow STANDARDS.md exactly:
  - df_candles and df_indicators
  - Columns: date, open, high, low, close, volume
  - DB path: /shared_data/signals.db
  - Freqtrade API: http://ft_bot:8080/api/v1
- No new trading endpoints; only Freqtrade API
- If chart_signal is missing or invalid, drop signal
- If pair mapping is unknown, fail closed
- All code changes must add/update tests
- Every completed task appends to PROGRESS.log
- Only these new top-level folders allowed: docs, beads, configs, scripts, reports

## 8) Testing Requirements
### Unit Tests
- Signal schema validation
- Chart pattern detection
- Confluence scoring
- TTL enforcement
- Idempotency (duplicate IDs ignored)
- Pair mapping table
- Rate budgeter

### Guardrail Tests
- Validate required columns and df_* names
- Validate DB path and Freqtrade API constants
- Ensure Brain never executes trades via CCXT

### Integration Tests
- Signal -> bus -> gateway -> Freqtrade API (mocked)
- Sidecar consumes bus entries and applies stop_loss

### E2E
- 5-10 minute plumbing test
- 2-hour shotgun dry-run with multiple instances

## 9) Acceptance Criteria (Definition of Done)
- Chart-first signals are generated and explainable
- Signal bus operational with TTL + idempotency
- Execution gateway submits to Freqtrade
- 2-hour report generated under reports/
- Comparison pack ready vs 10-hour baseline

## 10) Run Schedule (Target)
- Next 2-hour test should finish by 9:00 AM MST tomorrow.
- Target start time: 7:00 AM MST.
