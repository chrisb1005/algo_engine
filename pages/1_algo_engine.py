import streamlit as st
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data import load_history, get_current_price
from core.indicators import compute_indicators
from core.signals import generate_signal
from core.strategies import decide_action
from core.contracts import choose_contract
import pandas as pd

st.set_page_config(page_title="Algo Engine", page_icon="🔍", layout="wide")

st.title("🔍 Algo Engine — Signals & Recommendations")

st.markdown("""
This engine analyzes stock data, computes technical indicators, generates signals, 
and recommends option trading strategies.
""")

# Input section
col1, col2 = st.columns([2, 1])

with col1:
    ticker = st.text_input("Enter Ticker", "AAPL", help="Stock symbol (e.g., AAPL, MSFT, TSLA)").upper().strip()

with col2:
    days = st.selectbox("Analysis Period", [30, 60, 90, 180], index=1)

# Add validation
if ticker and not ticker.replace(".", "").replace("-", "").isalpha():
    st.warning("⚠️ Please enter a valid ticker symbol (letters only)")
    st.stop()

if st.button("🔍 Analyze", type="primary"):
    with st.spinner(f"Analyzing {ticker}..."):
        try:
            # Load data (request extra to account for indicator computation)
            # MA50 needs 50 days, so we add buffer
            data_days = days + 40
            df = load_history(ticker, days=data_days)
            
            if df is None or len(df) == 0:
                st.error(f"❌ No data found for {ticker}")
                st.info("Please check the ticker symbol and try again.")
                st.stop()
            
            # Get current price
            current_price = get_current_price(ticker)
            
            # Compute indicators
            df = compute_indicators(df)
            df_clean = df.dropna()
            
            if len(df_clean) == 0:
                st.error("Not enough data to compute indicators")
                st.info(f"Loaded {len(df)} rows but need at least 50 for indicators. Try a longer time period.")
                st.stop()
            
            # Generate signal
            sig = generate_signal(df_clean)
            
            # Get action recommendation
            action = decide_action(sig)
            
            # Display current price
            st.metric(label=f"{ticker} Current Price", value=f"${current_price:.2f}" if current_price else "N/A")
            
            # Display signals
            st.subheader("📊 Technical Signals")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                trend_color = "🟢" if sig.get("trend") == "Bullish" else "🔴"
                st.metric("Trend", sig.get("trend", "N/A"), delta=trend_color)
            
            with col2:
                rsi = sig.get("rsi", 0)
                rsi_status = "Oversold" if rsi < 30 else "Overbought" if rsi > 70 else "Neutral"
                st.metric("RSI", f"{rsi:.1f}", delta=rsi_status)
            
            with col3:
                vol = sig.get("vol", 0)
                st.metric("Volatility", f"{vol:.2f}%")
            
            with col4:
                momentum = sig.get("momentum", 0)
                mom_arrow = "📈" if momentum > 0 else "📉"
                st.metric("Momentum", f"{momentum*100:.2f}%", delta=mom_arrow)
            
            # Strategy recommendation
            st.subheader("💡 Strategy Recommendation")
            
            action_emoji = {
                "BUY_CALL": "📈 🟢",
                "BUY_PUT": "📉 🔴",
                "SELL_CALL": "🎯 🟡",
                "SELL_PUT": "🎯 🟡",
                "NO_TRADE": "⏸️ ⚪"
            }
            
            action_description = {
                "BUY_CALL": "Bullish momentum - Consider buying call options",
                "BUY_PUT": "Bearish momentum - Consider buying put options",
                "SELL_CALL": "Overbought conditions - Consider selling covered calls",
                "SELL_PUT": "Oversold conditions - Consider selling cash-secured puts",
                "NO_TRADE": "No clear signal - Stay on the sidelines"
            }
            
            st.markdown(f"### {action_emoji.get(action, '')} {action}")
            st.info(action_description.get(action, ""))
            
            # Get contract suggestion if action is not NO_TRADE
            if action != "NO_TRADE":
                st.subheader("📋 Suggested Contract")
                
                with st.spinner("Finding optimal contract..."):
                    try:
                        contract = choose_contract(ticker, action)
                        
                        if contract:
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Contract Symbol", contract["symbol"])
                                st.metric("Strike Price", f"${contract['strike']:.2f}")
                                st.metric("Days to Expiration", contract['days_to_expiration'])
                            
                            with col2:
                                st.metric("Last Price", f"${contract['last_price']:.2f}")
                                st.metric("Bid/Ask", f"${contract['bid']:.2f} / ${contract['ask']:.2f}")
                                st.metric("Volume", f"{int(contract['volume']):,}")
                            
                            with col3:
                                st.metric("Open Interest", f"{int(contract['open_interest']):,}")
                                st.metric("Implied Volatility", f"{contract['implied_volatility']*100:.1f}%")
                                itm_status = "✅ Yes" if contract['in_the_money'] else "❌ No"
                                st.metric("In The Money", itm_status)
                            
                            # Contract details
                            with st.expander("📝 Contract Details"):
                                st.json(contract)
                        else:
                            st.warning(f"⚠️ Could not find a suitable {action} contract for {ticker}. This can happen if:")
                            st.markdown("""
                            - Options data is temporarily unavailable
                            - The ticker doesn't have options trading
                            - No contracts match the criteria
                            
                            Try refreshing in a moment or select a different ticker.
                            """)
                    
                    except Exception as contract_error:
                        st.error(f"⚠️ Error loading contract: {str(contract_error)}")
                        st.info("The analysis is still valid - just couldn't load contract details.")
            
            # Show recent price data
            with st.expander("📈 Recent Price Data"):
                st.dataframe(df_clean.tail(10).iloc[::-1], use_container_width=True)
            
            # Price chart
            st.subheader("📉 Price Chart")
            chart_data = df[["Close"]].tail(60)
            st.line_chart(chart_data)
        
        except Exception as e:
            st.error(f"❌ An error occurred while analyzing {ticker}")
            st.exception(e)
            st.info("Please try again or select a different ticker.")

else:
    st.info("👆 Enter a ticker symbol and click Analyze to get started")
