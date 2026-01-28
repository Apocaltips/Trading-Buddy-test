from __future__ import annotations

from typing import List

import pandas as pd
import streamlit as st

from brain.data import fetch_ohlcv
from brain.logic import analyze
from brain.execution import ExecutionClient


st.set_page_config(page_title="TradeMate", layout="wide")
st.title("TradeMate War Room")

with st.sidebar:
    st.header("Settings")
    pairs_raw = st.text_area("Pairs (comma-separated)", "BTC/USDT, ETH/USDT")
    timeframe = st.selectbox("Timeframe", ["5m", "15m", "1h"], index=0)
    limit = st.number_input("Candles", min_value=50, max_value=500, value=200, step=50)
    stop_loss = st.number_input(
        "Stop Loss (decimal)",
        min_value=0.001,
        max_value=0.2,
        value=0.02,
        step=0.001,
        format="%.3f",
    )
    scan_clicked = st.button("Scan")


def _parse_pairs(raw: str) -> List[str]:
    return [pair.strip() for pair in raw.split(",") if pair.strip()]


tab_scanner, tab_monitor = st.tabs(["Scanner", "Monitor"])

with tab_scanner:
    if scan_clicked:
        results = []
        for pair in _parse_pairs(pairs_raw):
            try:
                df_candles = fetch_ohlcv(pair, timeframe=timeframe, limit=int(limit))
                analysis = analyze(df_candles)
                results.append(
                    {
                        "pair": pair,
                        "signal": analysis["signal"],
                        "reason": analysis["reason"],
                    }
                )
            except Exception as exc:
                results.append(
                    {
                        "pair": pair,
                        "signal": False,
                        "reason": f"Error: {exc}",
                    }
                )
        st.session_state["scan_results"] = results

    results = st.session_state.get("scan_results", [])
    if results:
        df_results = pd.DataFrame(results)
        st.dataframe(df_results, use_container_width=True)

        st.subheader("Trade Actions")
        client = ExecutionClient()
        for row in results:
            pair = row["pair"]
            reason = row["reason"]
            signal = bool(row["signal"])
            cols = st.columns([2, 6, 2])
            cols[0].markdown(f"**{pair}**")
            cols[1].markdown(reason)
            if cols[2].button("EXECUTE", key=f"trade_{pair}", disabled=not signal):
                try:
                    client.stage_signal(pair=pair, stop_loss=float(stop_loss), reason=reason)
                    response = client.trigger_buy(pair=pair)
                    st.success(f"Triggered buy for {pair}: {response}")
                except Exception as exc:
                    st.error(f"Trade failed for {pair}: {exc}")
    else:
        st.info("Run a scan to see trade opportunities.")

with tab_monitor:
    st.info("Monitor view coming next. Connect to Freqtrade API for live PnL.")