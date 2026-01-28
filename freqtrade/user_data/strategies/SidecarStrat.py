from datetime import datetime
from typing import Any, Optional

import sqlite3

from pandas import DataFrame
from freqtrade.persistence import Trade
from freqtrade.strategy import IStrategy

DB_PATH = "/shared_data/signals.db"


class SidecarStrat(IStrategy):
    timeframe = "5m"
    minimal_roi = {"0": 0.0}
    stoploss = -0.99
    use_custom_stoploss = True
    process_only_new_candles = True
    startup_candle_count = 50

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["enter_long"] = 0
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["exit_long"] = 0
        return dataframe

    def custom_stoploss(
        self,
        pair: str,
        trade: Trade,
        current_time: datetime,
        current_rate: float,
        current_profit: float,
        **kwargs: Any,
    ) -> float:
        db_stop = self._fetch_stop_loss(pair)
        if db_stop is None:
            return self.stoploss
        try:
            db_stop = float(db_stop)
        except (TypeError, ValueError):
            return self.stoploss
        if db_stop <= 0:
            return self.stoploss
        return -abs(db_stop)

    def _fetch_stop_loss(self, pair: str) -> Optional[float]:
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute(
                "SELECT stop_loss FROM active_signals WHERE pair = ? LIMIT 1",
                (pair,),
            )
            row = cur.fetchone()
        except sqlite3.Error:
            return None
        finally:
            if conn is not None:
                try:
                    conn.close()
                except sqlite3.Error:
                    pass
        if not row:
            return None
        return row[0]