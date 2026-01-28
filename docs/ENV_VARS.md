# Environment Variables

## Signal Engine
- `STRATEGY_FLEET_PATH` - path to strategy fleet YAML

## Signal Bus
- `BUS_PATH` - location of SQLite DB (default: /shared_data/signals.db)
- `BUS_TTL_SEC` - default TTL for signals

## Gateway
- `FT_API_URL` - Freqtrade API base URL (default: http://ft_bot:8080/api/v1)
- `FT_USERNAME` / `FT_PASSWORD` - API auth (if enabled)
- `PAIR_MAP_PATH` - JSON mapping for USD -> USDT

## Reporting
- `REPORT_OUT_DIR` - output folder for reports
