import streamlit as st
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.scanner import scan_market, get_quick_recommendations, POPULAR_TICKERS
import pandas as pd

st.set_page_config(page_title="Stock Suggester", page_icon="🔎", layout="wide")

st.title("🔎 Stock Suggester - Weekly Options Scanner")

st.markdown("""
Find the best stocks for weekly options trading based on:
- **Affordable contracts** ($10-30 per option)
- **High liquidity** (good volume on both stock and options)
- **Optimal volatility** (not too low, not too high)
- **Trading signals** (bonus for clear entry signals)
""")

# Settings
st.sidebar.header("⚙️ Scan Settings")

scan_type = st.sidebar.radio(
    "Scan Type",
    ["Quick Scan (10 stocks)", "Full Scan (50+ stocks)"],
    help="Quick scan is faster, Full scan is more comprehensive"
)

min_price = st.sidebar.slider("Min Option Price", 5, 25, 10, help="Minimum price per contract")
max_price = st.sidebar.slider("Max Option Price", 15, 50, 30, help="Maximum price per contract")

top_n = st.sidebar.slider("Number of Results", 5, 20, 10, help="How many top stocks to show")

# Scan button
col1, col2 = st.columns([1, 3])

with col1:
    if st.button("🚀 Start Scan", type="primary"):
        st.session_state['scan_running'] = True
        st.session_state['scan_results'] = None

with col2:
    if st.button("🗑️ Clear Results"):
        st.session_state['scan_running'] = False
        st.session_state['scan_results'] = None

# Run scan
if st.session_state.get('scan_running'):
    with st.spinner("Scanning market for opportunities..."):
        try:
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def update_progress(current, total):
                progress = current / total
                progress_bar.progress(progress)
                status_text.text(f"Scanning... {current}/{total} stocks")
            
            # Run scan
            if scan_type == "Quick Scan (10 stocks)":
                results = get_quick_recommendations(count=top_n)
            else:
                results = scan_market(
                    tickers=POPULAR_TICKERS,
                    min_price=min_price,
                    max_price=max_price,
                    top_n=top_n,
                    progress_callback=update_progress
                )
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            st.session_state['scan_results'] = results
            st.session_state['scan_running'] = False
            
            if results:
                st.success(f"✅ Found {len(results)} great opportunities!")
            else:
                st.warning("⚠️ No stocks matched your criteria. Try adjusting the price range.")
        
        except Exception as e:
            st.error(f"❌ Scan failed: {str(e)}")
            st.session_state['scan_running'] = False

# Display results
if st.session_state.get('scan_results'):
    results = st.session_state['scan_results']
    
    st.markdown("---")
    st.subheader("📊 Top Opportunities")
    
    # Create summary table
    summary_data = []
    for r in results:
        summary_data.append({
            'Ticker': r['ticker'],
            'Score': r['score'],
            'Price': f"${r['current_price']:.2f}",
            'Volatility': f"{r['volatility']*100:.2f}%",
            'Avg Volume': f"{r['avg_volume']:,.0f}",
            'Affordable Calls': r['affordable_calls'],
            'Affordable Puts': r['affordable_puts'],
            'Signal': r['action']
        })
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    # Detailed cards for top 3
    st.markdown("---")
    st.subheader("🎯 Top 3 Detailed Analysis")
    
    for i, result in enumerate(results[:3]):
        with st.expander(f"#{i+1} - {result['ticker']} (Score: {result['score']}/15)", expanded=(i==0)):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**📈 Stock Info**")
                st.metric("Current Price", f"${result['current_price']:.2f}")
                st.metric("Daily Volatility", f"{result['volatility']*100:.2f}%")
                st.metric("Avg Volume", f"{result['avg_volume']:,.0f}")
            
            with col2:
                st.markdown("**📞 Call Options**")
                if result['best_call']:
                    st.metric("Best Call Strike", f"${result['best_call']['strike']:.2f}")
                    st.metric("Call Price", f"${result['best_call']['price']:.2f}")
                    st.metric("Call Volume", f"{int(result['best_call']['volume']):,}")
                else:
                    st.info("No affordable calls found")
            
            with col3:
                st.markdown("**📉 Put Options**")
                if result['best_put']:
                    st.metric("Best Put Strike", f"${result['best_put']['strike']:.2f}")
                    st.metric("Put Price", f"${result['best_put']['price']:.2f}")
                    st.metric("Put Volume", f"{int(result['best_put']['volume']):,}")
                else:
                    st.info("No affordable puts found")
            
            # Strategy recommendation
            st.markdown("**💡 Strategy Recommendation**")
            
            action_emoji = {
                "BUY_CALL": "📈 🟢 Bullish - Consider buying calls",
                "BUY_PUT": "📉 🔴 Bearish - Consider buying puts",
                "SELL_CALL": "🎯 🟡 Overbought - Consider selling calls",
                "SELL_PUT": "🎯 🟡 Oversold - Consider selling puts",
                "NO_TRADE": "⏸️ ⚪ No clear signal - Wait for setup"
            }
            
            st.info(action_emoji.get(result['action'], result['action']))
            
            # Quick analyze button
            if st.button(f"🔍 Full Analysis of {result['ticker']}", key=f"analyze_{result['ticker']}"):
                st.info(f"💡 Tip: Go to the Algo Engine page and enter '{result['ticker']}' for detailed analysis!")
    
    # Export option
    st.markdown("---")
    st.subheader("💾 Export Results")
    
    csv = summary_df.to_csv(index=False)
    st.download_button(
        label="📥 Download as CSV",
        data=csv,
        file_name="stock_suggestions.csv",
        mime="text/csv"
    )

else:
    # Show instructions
    st.info("👆 Click 'Start Scan' to find the best weekly options trading opportunities!")
    
    st.markdown("---")
    st.subheader("📚 How It Works")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🔍 Scanning Process**
        1. Checks stock liquidity
        2. Finds weekly options
        3. Filters by price range
        4. Analyzes technical signals
        5. Scores each stock
        """)
    
    with col2:
        st.markdown("""
        **📊 Scoring Factors**
        - ⭐ Volatility (5 pts)
        - ⭐ Volume (5 pts)
        - ⭐ Options availability (5 pts)
        - ⭐ Clear signals (2 bonus pts)
        - **Max Score: 17**
        """)
    
    with col3:
        st.markdown("""
        **💰 Price Range**
        - Default: $10-30 per contract
        - Adjustable in settings
        - Considers both calls & puts
        - Requires volume > 100
        """)
    
    st.markdown("---")
    st.markdown("""
    ### 🎯 What Makes a Good Candidate?
    
    The scanner looks for stocks that are:
    - **Liquid**: High daily trading volume (>1M shares)
    - **Active Options**: Weekly expirations with good volume
    - **Affordable**: Options priced for retail traders ($10-30)
    - **Volatile (but not too much)**: Sweet spot for weekly trades
    - **Signal-Ready**: Current technical setup favoring a trade
    
    ### ⚡ Quick vs Full Scan
    
    - **Quick Scan**: Checks 10 most popular liquid stocks (~30 seconds)
    - **Full Scan**: Comprehensive scan of 50+ stocks (~2-3 minutes)
    
    ### 💡 Tips
    
    - Run scans during market hours for best data
    - Lower price ranges ($10-20) = Less risk, more options
    - Higher scores (12+) = Better overall candidates
    - Always verify with full analysis in Algo Engine
    """)
