# Troubleshooting

## 401 Unauthorized (Freqtrade API)
Cause: API auth enabled but gateway not sending credentials.
Fix: Align gateway with Freqtrade username/password or disable auth for local testing.

## 429 Too Many Requests (Gemini / CoinGecko / Binance)
Cause: Public API rate limits, IP-based.
Fix:
- Reduce symbols/timeframes
- Increase cache TTL
- Run parallel tests from different public IPs

## No trades executed
Cause:
- TTL expired before execution
- Idempotency rejected duplicates
- Pair mapping missing
Fix:
- Check bus logs for rejects
- Validate mapping table

## Docker will not start
Fix:
- Ensure Docker Desktop is running
- Confirm WSL integration (Windows)

## Synthetic candles used (Trading Buddy)
Cause: Binance API failed -> fallback path
Fix: Disable fallback for live tests
