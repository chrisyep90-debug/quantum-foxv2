
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
import time
import alpaca_trade_api as tradeapi
from datetime import datetime

st.set_page_config(page_title="Quantum Fox Live Trading", layout="wide")
st.title("🦊 Quantum Fox — Live Trading Dashboard")
st.caption("Use PAPER MODE for testing. Live mode will place real orders. Trade responsibly.")

# --- Sidebar: API keys and settings ---
st.sidebar.header("Broker Settings")
use_alpaca = st.sidebar.checkbox("Use Alpaca Broker (recommended)", True)
if use_alpaca:
    alpaca_key = st.sidebar.text_input("ALPACA API KEY", type="password")
    alpaca_secret = st.sidebar.text_input("ALPACA SECRET KEY", type="password")
    alpaca_env = st.sidebar.selectbox("Environment", ["paper", "live"])
    endpoint = "https://paper-api.alpaca.markets" if alpaca_env == "paper" else "https://api.alpaca.markets"
else:
    st.sidebar.info("Only Alpaca integration is implemented in this version.")

st.sidebar.markdown("---")
st.sidebar.markdown("⚠️ **IMPORTANT:** Use paper API keys if you are testing. Live trading risks real money.")
st.sidebar.markdown("Read the README included in the package for step-by-step guidance.")

# Connect to Alpaca if keys provided
api = None
if use_alpaca and alpaca_key and alpaca_secret:
    try:
        api = tradeapi.REST(alpaca_key, alpaca_secret, base_url=endpoint, api_version='v2')
        account = api.get_account()
        st.sidebar.success(f"Connected to Alpaca ({'PAPER' if alpaca_env=='paper' else 'LIVE'}) — Equity: ${float(account.equity):,.2f}")
    except Exception as e:
        st.sidebar.error(f"Alpaca connection error: {e}")

# --- Main UI ---
symbol = st.text_input("Stock symbol (e.g. AAPL)", value="AAPL").upper().strip()
col1, col2 = st.columns([2,1])

with col1:
    # Chart
    st.subheader(f"{symbol} — Price & Chart")
    period = st.selectbox("Chart period", ['5d','1mo','3mo','6mo','1y'], index=0)
    interval = st.selectbox("Interval", ['1m','5m','15m','1h','1d'], index=3)
    try:
        data = yf.download(symbol, period=period, interval=interval, progress=False)
        if not data.empty:
            fig = go.Figure(data=[go.Candlestick(x=data.index,
                                                 open=data['Open'], high=data['High'],
                                                 low=data['Low'], close=data['Close'])])
            fig.update_layout(height=500, title=f"{symbol} {period} {interval}", xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
            latest = data['Close'].iloc[-1]
            st.metric(label=f"{symbol} Price", value=f"${latest:.2f}")
        else:
            st.info("No data available for the selected period/interval.")
    except Exception as e:
        st.error(f"Chart error: {e}")

    # Trade signals (simple moving average crossover)
    st.subheader("Signal (SMA crossover)")
    try:
        hist = yf.download(symbol, period='2mo', interval='1d', progress=False)
        hist['SMA20'] = hist['Close'].rolling(20).mean()
        hist['SMA50'] = hist['Close'].rolling(50).mean()
        last = hist.dropna().iloc[-1]
        signal = 'HOLD'
        if last['SMA20'] > last['SMA50']:
            signal = 'BUY'
        elif last['SMA20'] < last['SMA50']:
            signal = 'SELL'
        st.info(f"SMA Signal: {signal}")
    except Exception as e:
        st.info("Not enough data for SMA signal.")

with col2:
    st.subheader("Order Panel")
    st.write("Choose order type and size. Use PAPER mode until you're fully confident.") 
    qty = st.number_input("Quantity (shares)", min_value=1, value=1)
    order_side = st.selectbox("Side", ['buy','sell'])
    order_type = st.selectbox("Order Type", ['market','limit'])
    limit_price = None
    if order_type == 'limit':
        limit_price = st.number_input("Limit price", format="%.2f")
    take_profit = st.number_input("Take profit target ($) — optional", format="%.2f", value=0.0)
    stop_loss = st.number_input("Stop loss ($) — optional", format="%.2f", value=0.0)
    if st.button("Place Order"):
        if api is None:
            st.error("Broker not connected. Enter Alpaca API keys in the sidebar.")
        else:
            try:
                if order_type == 'market':
                    order = api.submit_order(symbol=symbol, qty=qty, side=order_side, type='market', time_in_force='gtc')
                else:
                    order = api.submit_order(symbol=symbol, qty=qty, side=order_side, type='limit', time_in_force='gtc', limit_price=limit_price)
                st.success(f"Order submitted: id={order.id} status={order.status}")
                # Place OCO-ish TP/SL using conditional orders (Alpaca supports OCO via bracket orders in some SDKs)
                # We'll create simple child orders if user provided targets (note: paper mode only)
                if take_profit > 0 or stop_loss > 0:
                    try:
                        # For safety, we will create separate orders tied to the position using stop or limit
                        if take_profit > 0:
                            api.submit_order(symbol=symbol, qty=qty, side='sell' if order_side=='buy' else 'buy', type='limit', time_in_force='gtc', limit_price=take_profit)
                        if stop_loss > 0:
                            api.submit_order(symbol=symbol, qty=qty, side='sell' if order_side=='buy' else 'buy', type='stop', time_in_force='gtc', stop_price=stop_loss)
                        st.info('Take profit / Stop loss targets created as separate orders (paper testing recommended).')
                    except Exception as e2:
                        st.warning(f'Could not create TP/SL orders: {e2}')
            except Exception as e:
                st.error(f"Order error: {e}")

    st.markdown("---")
    st.subheader("Account & Positions")
    if api is not None:
        try:
            acc = api.get_account()
            st.write(f"Account status: {acc.status} — Cash: ${float(acc.cash):,.2f} — Buying Power: ${float(acc.buying_power):,.2f}")
            positions = api.list_positions()
            if positions:
                pos_df = pd.DataFrame([{'symbol':p.symbol,'qty':p.qty,'market_value':p.market_value,'avg_entry_price':p.avg_entry_price} for p in positions])
                st.table(pos_df)
            else:
                st.info('No open positions.')
        except Exception as e:
            st.error(f"Account error: {e}")
    else:
        st.info("Connect with Alpaca API keys to view account and place live/paper orders.")

st.markdown('---')
st.caption('Quantum Fox — Use responsibly. Always test in PAPER mode before going live.')
