# Repository Guidelines

## Project Structure & Module Organization
- `freqtrade/` holds the execution "Body" configuration (`user_data/config.json`) and strategy logic (`user_data/strategies/SidecarStrat.py`).
- `brain/` contains the Streamlit UI (`app.py`), market data fetch (`data.py`), signal logic (`logic.py`), execution client (`execution.py`), and tests (`tests/`).
- `shared_data/` stores the shared SQLite DB (`signals.db`) and bootstrap script (`init_db.py`).
- `.beads/` tracks the task graph; `PROGRESS.log` records task completions.

## Build, Test, and Development Commands
- `docker compose up -d`: Start the Freqtrade body and the Brain container with a shared `/shared_data` volume.
- `python shared_data/init_db.py`: Initialize `shared_data/signals.db` locally.
- `streamlit run brain/app.py`: Run the TradeMate UI during development.
- `pytest brain/tests/test_logic.py`: Run the Brain logic unit test.

## Coding Style & Naming Conventions
- Python uses 4-space indentation and standard `snake_case` for functions and variables.
- Follow `STANDARDS.md` strictly: use `df_candles`/`df_indicators`, columns `date, open, high, low, close, volume`, and DB path `/shared_data/signals.db`.
- Keep side effects isolated: the Brain stages signals in SQLite, and executes trades only via the Freqtrade API (`http://ft_bot:8080/api/v1`).

## Testing Guidelines
- Tests live under `brain/tests/` and use `pytest`.
- Naming: `test_*.py` with plain `assert` checks.
- There is no coverage gate yet; keep tests small and fast.

## Commit & Pull Request Guidelines
- This repo has no established commit history yet. Use concise, imperative messages (e.g., `Add sidecar strategy`).
- PRs should include a summary, test evidence (command + result), and screenshots for UI changes when applicable.

## Security & Configuration Notes
- Do not commit exchange API keys or live trading credentials.
- Prefer environment variables or local config overrides for secrets.