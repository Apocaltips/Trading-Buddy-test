# TradeMate Master Protocol

## 1. Variable Naming (Strict Enforcement)
To prevent context drift, you must use these exact variable names:
- **DataFrames:** `df_candles` (raw), `df_indicators` (processed).
- **Columns:** `['date', 'open', 'high', 'low', 'close', 'volume']`.
- **Pairs:** Must use slash format: `'BTC/USDT'`.
- **Paths:**
  - Shared DB: `/shared_data/signals.db`
  - Freqtrade API: `http://ft_bot:8080/api/v1`

## 2. Architecture Constraints
- **Separation of Concerns:** The Brain (Streamlit) does NOT execute trades directly via CCXT. It MUST use the Freqtrade API.
- **The Synapse:** Dynamic Stop-Losses must be written to the Shared DB *before* calling the API.

## 3. Progress Logging
After completing a task, you MUST append a new line to `PROGRESS.log` in this JSON format:
`{"timestamp": "...", "task_id": "...", "status": "success", "files_modified": [...]}`