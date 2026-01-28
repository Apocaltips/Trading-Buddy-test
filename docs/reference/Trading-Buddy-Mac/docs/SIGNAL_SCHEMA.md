# Signal Schema

## Required Fields
- `id` (uuid)
- `ts_utc` (ISO 8601)
- `source` (e.g., "tradegate")
- `instance` (e.g., "momo_risk")
- `strategy` (e.g., "revert-5m")
- `symbol` (canonical, e.g., "BTC-USD")
- `pair` (execution pair, e.g., "BTC/USDT")
- `side` (`buy` | `sell`)
- `intent` (`enter` | `exit` | `reduce`)
- `timeframe` (e.g., "5m")
- `signal_bps`
- `price_snapshot`
- `ttl_sec`

## Optional Fields
- `stop_loss` (decimal, e.g., 0.02)
- `take_profit` (decimal or bps)
- `notional_usd` or `qty`
- `vol_bps`
- `sentiment_score`
- `chart_signal`
- `reason` (human‑readable)

## Example
```json
{
  "id": "1b3c1f8a-4b45-4c68-9f4e-4b9c7f5d0d7c",
  "ts_utc": "2026-01-28T04:52:10Z",
  "source": "tradegate",
  "instance": "reversal",
  "strategy": "revert-5m",
  "symbol": "BTC-USD",
  "pair": "BTC/USDT",
  "side": "buy",
  "intent": "enter",
  "timeframe": "5m",
  "signal_bps": -32.5,
  "price_snapshot": 88735.17,
  "ttl_sec": 120,
  "stop_loss": 0.025,
  "reason": "reversion + chart support + vol ok"
}
```

## Mapping Rules
- `BTC-USD` → `BTC/USDT`
- `ETH-USD` → `ETH/USDT`
- All mappings in a single table; fail closed if unknown

