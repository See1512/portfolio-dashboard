import streamlit as st, pandas as pd
from datetime import date, timedelta
from src import data_io, prices, analytics

# Set page title
st.set_page_config(page_title="Portfolio Analytics Dashboard", layout="wide")
st.title("📊 Overview")

with st.sidebar:
    st.header("Trade Data")
    trades_data = st.file_uploader("Upload trades data", type=["csv"])

    # Set date range 
    start = st.date_input("Start", value=date.today() - timedelta(days=365*3))
    end = st.date_input("End", value=date.today())

if not trades_data:
    st.info("Please upload your trades data as a .csv file with columns: date, ticker, side, qty, price.")
    st.stop()

# Ingest data from trades file
try:
    trades = data_io.read_trades(trades_data)
except Exception as e:
    st.error(f"Error reading trades data: {e}")
    st.stop()

tickers = sorted(trades["ticker"].unique())
if not tickers:
    st.warning("No tickers found in the trades data.")
    st.stop()

pos = analytics.reconstruct_pos(trades)
#st.write("Positions head:", pos.head())
#st.write("Positions tail:", pos.tail())
#st.write("Positions daily changes:", pos.diff().dropna().head())
panel = prices.get_price_on_date(tickers, start.isoformat(), end.isoformat())

# Align price panel to position dates
panel = panel.reindex(pos.index).ffill().bfill()
if panel.empty:
    st.error("No price data available. Please check tickers or date range.")
    st.stop()

# Compute equity curve
equity = analytics.portfolio_value(pos, panel)

# Save states for other pages
st.session_state["trades_df"] = trades
st.session_state["pos_df"] = pos
st.session_state["price_df"] = panel

# Key Performance Indicators
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Value", f"{equity.iloc[-1]:,.0f}")
col2.metric("Total TWR", f"{analytics.twr(equity)*100:,.2f}%")
col3.metric("Annualized Volatility", f"{analytics.annualized_volatility(equity)*100:.2f}%")
col4.metric("Max Drawdown", f"{analytics.max_drawdown(equity)*100:,.2f}%")

# Equity curve and drawdown charts
tab1, tab2 = st.tabs(["Equity Curve", "Drawdown"])
with tab1:
    st.line_chart(equity.rename("Portfolio Value"))
with tab2:
    drawdown = (equity - equity.cummax()) / equity.cummax()
    st.area_chart(drawdown.rename("Drawdown"))

#st.write("Equity head:", equity.head())
#st.write("Equity tail:", equity.tail())
#st.write("Daily returns:", equity.pct_change().dropna().head())

