import streamlit as st
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data import load_history
from core.backtester import backtest
import pandas as pd

st.set_page_config(page_title="Backtester", page_icon="📊", layout="wide")

st.title("📊 Backtester")

st.markdown("""
Test your strategy on historical data to see how it would have performed.
""")

ticker = st.text_input("Ticker", "AAPL", help="Stock symbol to backtest").upper().strip()
days = st.slider("Days of History", 60, 365, 180, help="Number of days to backtest")

# Add validation
if ticker and not ticker.replace(".", "").replace("-", "").isalpha():
    st.warning("⚠️ Please enter a valid ticker symbol (letters only)")
    st.stop()

if st.button("🚀 Run Backtest", type="primary"):
    with st.spinner(f"Running backtest on {ticker}..."):
        try:
            # Load historical data
            df = load_history(ticker, days=days)
            
            if df is None or len(df) == 0:
                st.error(f"❌ No data found for {ticker}")
                st.info("Please check the ticker symbol and try again.")
                st.stop()
            
            st.info(f"Loaded {len(df)} days of data for {ticker}")
            
            # Run backtest
            trades = backtest(df)
            
            # Display results
            st.subheader("💰 Backtest Results")
            
            if trades and len(trades) > 0:
                total_pnl = sum(trades)
                avg_pnl = total_pnl / len(trades)
                winning_trades = len([t for t in trades if t > 0])
                losing_trades = len([t for t in trades if t < 0])
                win_rate = (winning_trades / len(trades)) * 100 if trades else 0
                
                # Metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Trades", len(trades))
                
                with col2:
                    pnl_color = "normal" if total_pnl >= 0 else "inverse"
                    st.metric("Total P&L", f"${total_pnl:.2f}", delta=f"{total_pnl:.2f}")
                
                with col3:
                    st.metric("Win Rate", f"{win_rate:.1f}%")
                
                with col4:
                    st.metric("Avg P&L per Trade", f"${avg_pnl:.2f}")
                
                # Additional metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Winning Trades", winning_trades)
                
                with col2:
                    st.metric("Losing Trades", losing_trades)
                
                with col3:
                    if trades:
                        best_trade = max(trades)
                        worst_trade = min(trades)
                        st.metric("Best Trade", f"${best_trade:.2f}")
                        st.metric("Worst Trade", f"${worst_trade:.2f}")
                
                # P&L Chart
                st.subheader("📈 Trade P&L Chart")
                
                # Create cumulative P&L
                cumulative_pnl = []
                running_total = 0
                for trade in trades:
                    running_total += trade
                    cumulative_pnl.append(running_total)
                
                pnl_df = pd.DataFrame({
                    "Trade #": range(1, len(trades) + 1),
                    "P&L": trades,
                    "Cumulative P&L": cumulative_pnl
                })
                
                st.line_chart(pnl_df.set_index("Trade #")["Cumulative P&L"])
                
                # Trade details
                with st.expander("📋 Trade Details"):
                    st.dataframe(pnl_df, use_container_width=True)
                
            else:
                st.warning("⚠️ No trades were executed during this period.")
                st.info("""
                This could mean:
                - The strategy didn't find any good entry/exit points
                - There wasn't enough data (need at least 50+ days)
                - Market conditions didn't meet strategy criteria
                
                Try:
                - Increasing the number of days
                - Selecting a different ticker
                - A more volatile stock
                """)
        
        except Exception as e:
            st.error(f"❌ An error occurred while backtesting {ticker}")
            st.exception(e)
            st.info("Please try again with a different ticker or time period.")

else:
    st.info("👆 Select a ticker and click Run Backtest to get started")
