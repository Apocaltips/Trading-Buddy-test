# Risks and Mitigations

## R1 - API Rate Limits (Gemini/CoinGecko/Binance)
- Risk: 429s contaminate signals.
- Mitigation: run parallel tests from different public IPs or use cached/replay mode.

## R2 - Pair Mapping Errors
- Risk: signals rejected or executed on wrong market.
- Mitigation: strict mapping table + fail closed.

## R3 - Auth Mismatch
- Risk: Freqtrade returns 401.
- Mitigation: align API auth in execution gateway.

## R4 - Synthetic Fallback Data (Trading Buddy)
- Risk: non-live data invalidates test.
- Mitigation: disable fallback in live tests.

## R5 - Chart Overfitting
- Risk: too many patterns produce false positives.
- Mitigation: confluence threshold + A+ filter + journal review.

## R6 - Strategy Explosion
- Risk: too many instances exceed rate limit or produce noise.
- Mitigation: rate budgeter and per-pair caps.
