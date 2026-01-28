# Signal Schema

## Required Fields
- `id` (uuid)
- `ts_utc` (ISO 8601)
- `source` (e.g., "chart_engine")
- `instance` (e.g., "trend_pullback_5m")
- `strategy` (e.g., "breakout_retest")
- `symbol` (canonical, e.g., "BTC-USD")
- `pair` (execution pair, e.g., "BTC/USDT")
- `side` (`buy` | `sell`)
- `intent` (`enter` | `exit` | `reduce`)
- `timeframe` (e.g., "5m")
- `signal_bps`
- `price_snapshot`
- `ttl_sec`
- `chart_signal` (object)

## Required chart_signal Fields
- `pattern`
- `structure_level`
- `timeframes` (list)
- `confluence_score` (0-100)
- `invalidation_price`
- `lines` (list of {type, price, timeframe})

## Optional Fields
- `stop_loss` (decimal, e.g., 0.02)
- `take_profit` (decimal or bps)
- `notional_usd` or `qty`
- `vol_bps`
- `sentiment_score`
- `reason` (human readable)

## Example
```json
{
  "id": "1b3c1f8a-4b45-4c68-9f4e-4b9c7f5d0d7c",
  "ts_utc": "2026-01-28T04:52:10Z",
  "source": "chart_engine",
  "instance": "trend_pullback_5m",
  "strategy": "pullback_structure",
  "symbol": "BTC-USD",
  "pair": "BTC/USDT",
  "side": "buy",
  "intent": "enter",
  "timeframe": "5m",
  "signal_bps": -32.5,
  "price_snapshot": 88735.17,
  "ttl_sec": 120,
  "stop_loss": 0.025,
  "chart_signal": {
    "pattern": "breakout_retest",
    "structure_level": 88450.00,
    "timeframes": ["5m", "15m"],
    "confluence_score": 82,
    "invalidation_price": 88380.00,
    "lines": [
      {"type": "support", "price": 88450.0, "timeframe": "15m"},
      {"type": "trendline", "price": 88520.0, "timeframe": "5m"}
    ]
  },
  "reason": "breakout retest + trend alignment + vol ok"
}
```

## Mapping Rules
- `BTC-USD` -> `BTC/USDT`
- `ETH-USD` -> `ETH/USDT`
- All mappings in a single table; fail closed if unknown
