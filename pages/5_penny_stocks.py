import streamlit as st
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.penny_scanner import scan_penny_movers, get_stock_due_diligence, get_quick_penny_movers, PENNY_STOCK_TICKERS
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Penny Stock Movers", page_icon="💰", layout="wide")

st.title("💰 Penny Stock Movers")

st.markdown("""
Track high-volume penny stock movers and perform due diligence analysis.

⚠️ **Risk Warning**: Penny stocks are highly volatile and risky. Only invest what you can afford to lose.
""")

# Tabs for Scanner and DD
tab1, tab2 = st.tabs(["🔍 Scanner", "🔎 Due Diligence"])

# ----- TAB 1: SCANNER -----
with tab1:
    st.subheader("📊 Scan for Active Penny Stocks")
    
    # Settings
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        scan_mode = st.selectbox(
            "Scan Mode",
            ["Quick Scan (15 stocks)", "Full Scan (50+ stocks)"],
            help="Quick is faster, Full is comprehensive"
        )
    
    with col2:
        max_price = st.slider("Max Price", 1.0, 20.0, 10.0, 0.5, help="Maximum stock price")
    
    with col3:
        min_volume = st.selectbox(
            "Min Volume",
            [500_000, 1_000_000, 2_000_000, 5_000_000],
            index=1,
            format_func=lambda x: f"{x:,}"
        )
    
    with col4:
        sort_by = st.selectbox(
            "Sort By",
            ["score", "change_1d", "change_5d", "change_20d", "volume_ratio"],
            format_func=lambda x: {
                "score": "Overall Score",
                "change_1d": "1-Day Change",
                "change_5d": "5-Day Change",
                "change_20d": "20-Day Change",
                "volume_ratio": "Volume Surge"
            }[x]
        )
    
    # Scan button
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("🚀 Scan Now", type="primary"):
            st.session_state['penny_scan_running'] = True
            st.session_state['penny_results'] = None
    
    with col2:
        if st.button("🗑️ Clear Results"):
            st.session_state['penny_scan_running'] = False
            st.session_state['penny_results'] = None
    
    # Run scan
    if st.session_state.get('penny_scan_running'):
        with st.spinner("Scanning for penny stock movers..."):
            try:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def update_progress(current, total):
                    progress_bar.progress(current / total)
                    status_text.text(f"Scanning... {current}/{total} stocks")
                
                # Run scan
                if scan_mode == "Quick Scan (15 stocks)":
                    results = get_quick_penny_movers(count=10)
                else:
                    results = scan_penny_movers(
                        tickers=PENNY_STOCK_TICKERS,
                        max_price=max_price,
                        min_volume=min_volume,
                        top_n=20,
                        sort_by=sort_by,
                        progress_callback=update_progress
                    )
                
                progress_bar.empty()
                status_text.empty()
                
                st.session_state['penny_results'] = results
                st.session_state['penny_scan_running'] = False
                
                if results:
                    st.success(f"✅ Found {len(results)} active penny stocks!")
                else:
                    st.warning("⚠️ No stocks matched your criteria.")
            
            except Exception as e:
                st.error(f"❌ Scan failed: {str(e)}")
                st.session_state['penny_scan_running'] = False
    
    # Display results
    if st.session_state.get('penny_results'):
        results = st.session_state['penny_results']
        
        st.markdown("---")
        
        # Summary table
        summary_data = []
        for r in results:
            emoji = "🔥" if abs(r['change_1d']) > 10 else "📈" if r['change_1d'] > 0 else "📉"
            
            summary_data.append({
                '': emoji,
                'Ticker': r['ticker'],
                'Price': f"${r['current_price']:.2f}",
                '1D %': f"{r['change_1d']:+.1f}%",
                '5D %': f"{r['change_5d']:+.1f}%",
                '20D %': f"{r['change_20d']:+.1f}%",
                'Volume': f"{r['volume']:,.0f}",
                'Vol Ratio': f"{r['volume_ratio']:.1f}x",
                'Trend': r['trend'],
                'Score': r['score']
            })
        
        df = pd.DataFrame(summary_data)
        
        # Color-code the dataframe
        st.dataframe(df, use_container_width=True, hide_index=True, height=400)
        
        # Top movers cards
        st.markdown("---")
        st.subheader("🔥 Top 3 Movers")
        
        cols = st.columns(3)
        for i, result in enumerate(results[:3]):
            with cols[i]:
                trend_color = "🟢" if "UP" in result['trend'] else "🔴" if "DOWN" in result['trend'] else "⚪"
                
                st.markdown(f"### {trend_color} {result['ticker']}")
                st.metric("Price", f"${result['current_price']:.2f}", f"{result['change_1d']:+.2f}%")
                st.metric("5-Day Change", f"{result['change_5d']:+.1f}%")
                st.metric("Volume Surge", f"{result['volume_ratio']:.1f}x")
                st.caption(f"Score: {result['score']}/15 | {result['trend']}")
                
                if st.button(f"📋 DD Report", key=f"dd_{result['ticker']}"):
                    st.session_state['dd_ticker'] = result['ticker']
                    st.info(f"💡 Switch to 'Due Diligence' tab to view full DD on {result['ticker']}")
        
        # Export
        st.markdown("---")
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Results (CSV)",
            data=csv,
            file_name="penny_stock_movers.csv",
            mime="text/csv"
        )
    
    else:
        st.info("👆 Click 'Scan Now' to find penny stock movers")

# ----- TAB 2: DUE DILIGENCE -----
with tab2:
    st.subheader("🔎 Due Diligence Analysis")
    
    # Ticker input
    col1, col2 = st.columns([2, 1])
    
    with col1:
        dd_ticker = st.text_input(
            "Enter Ticker for DD",
            value=st.session_state.get('dd_ticker', ''),
            placeholder="e.g., SNDL, PLUG, NIO",
            help="Enter a penny stock ticker to analyze"
        ).upper().strip()
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        analyze_btn = st.button("📊 Analyze", type="primary")
    
    if analyze_btn and dd_ticker:
        st.session_state['dd_ticker'] = dd_ticker
        
        with st.spinner(f"Performing due diligence on {dd_ticker}..."):
            try:
                dd_data = get_stock_due_diligence(dd_ticker)
                
                if 'error' in dd_data:
                    st.error(f"❌ {dd_data['error']}")
                else:
                    st.session_state['dd_data'] = dd_data
                    
            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")
    
    # Display DD data
    if st.session_state.get('dd_data'):
        dd = st.session_state['dd_data']
        
        st.markdown("---")
        st.subheader(f"📋 Due Diligence: {dd['ticker']}")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Current Price", f"${dd['current_price']:.2f}")
        
        with col2:
            change_1d = dd['price_changes'].get('1d', {}).get('change_pct', 0)
            st.metric("1-Day Change", f"{change_1d:+.2f}%", delta=f"{change_1d:+.2f}%")
        
        with col3:
            change_5d = dd['price_changes'].get('5d', {}).get('change_pct', 0)
            st.metric("5-Day Change", f"{change_5d:+.2f}%", delta=f"{change_5d:+.2f}%")
        
        with col4:
            st.metric("RSI", f"{dd['technicals']['rsi']:.1f}", 
                     delta="Overbought" if dd['technicals']['rsi'] > 70 else "Oversold" if dd['technicals']['rsi'] < 30 else "Neutral")
        
        # Price chart
        st.markdown("---")
        st.subheader("📈 Price Chart (3 Months)")
        
        df_chart = dd['data']
        
        fig = go.Figure()
        
        # Candlestick chart
        fig.add_trace(go.Candlestick(
            x=df_chart.index,
            open=df_chart['Open'],
            high=df_chart['High'],
            low=df_chart['Low'],
            close=df_chart['Close'],
            name='Price'
        ))
        
        # Add MA20
        fig.add_trace(go.Scatter(
            x=df_chart.index,
            y=[dd['technicals']['ma20']] * len(df_chart),
            mode='lines',
            name='MA20',
            line=dict(color='orange', dash='dash')
        ))
        
        # Add MA50
        fig.add_trace(go.Scatter(
            x=df_chart.index,
            y=[dd['technicals']['ma50']] * len(df_chart),
            mode='lines',
            name='MA50',
            line=dict(color='blue', dash='dash')
        ))
        
        fig.update_layout(
            title=f"{dd['ticker']} - Price Action",
            yaxis_title='Price ($)',
            xaxis_title='Date',
            height=500,
            xaxis_rangeslider_visible=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Volume chart
        fig_vol = go.Figure()
        
        fig_vol.add_trace(go.Bar(
            x=df_chart.index,
            y=df_chart['Volume'],
            name='Volume',
            marker_color='lightblue'
        ))
        
        fig_vol.add_hline(
            y=dd['volume']['avg_overall'],
            line_dash="dash",
            line_color="red",
            annotation_text="Avg Volume"
        )
        
        fig_vol.update_layout(
            title="Volume",
            yaxis_title='Volume',
            xaxis_title='Date',
            height=250
        )
        
        st.plotly_chart(fig_vol, use_container_width=True)
        
        # Detailed analysis
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Volume Analysis")
            st.metric("Current Volume", f"{dd['volume']['current']:,.0f}")
            st.metric("5-Day Avg", f"{dd['volume']['avg_5d']:,.0f}")
            st.metric("20-Day Avg", f"{dd['volume']['avg_20d']:,.0f}")
            st.caption(f"Trend: **{dd['volume']['trend']}**")
        
        with col2:
            st.subheader("📏 Price Levels")
            st.metric("52-Week High", f"${dd['price_levels']['high_52w']:.2f}")
            st.metric("52-Week Low", f"${dd['price_levels']['low_52w']:.2f}")
            st.metric("Position in Range", f"{dd['price_levels']['position_in_range']:.1f}%")
            
            if dd['price_levels']['position_in_range'] < 30:
                st.caption("🔵 Near lows - potential support")
            elif dd['price_levels']['position_in_range'] > 70:
                st.caption("🔴 Near highs - potential resistance")
        
        # Opportunities
        st.markdown("---")
        st.subheader("💡 Opportunities & Signals")
        
        if dd['opportunities']:
            for opp in dd['opportunities']:
                st.info(opp)
        else:
            st.info("No clear opportunities identified at this time.")
        
        # Risk factors
        st.markdown("---")
        st.subheader("⚠️ Risk Factors")
        
        if dd['risk_factors']:
            for risk in dd['risk_factors']:
                st.warning(risk)
        else:
            st.success("✅ No major risk flags detected")
        
        # Technical summary
        st.markdown("---")
        st.subheader("🎯 Technical Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("RSI (14)", f"{dd['technicals']['rsi']:.1f}")
            if dd['technicals']['rsi'] < 30:
                st.caption("🟢 Oversold territory")
            elif dd['technicals']['rsi'] > 70:
                st.caption("🔴 Overbought territory")
            else:
                st.caption("⚪ Neutral zone")
        
        with col2:
            st.metric("Volatility", f"{dd['technicals']['volatility']*100:.2f}%")
            if dd['technicals']['volatility'] > 0.05:
                st.caption("🔥 Very high volatility")
            elif dd['technicals']['volatility'] > 0.03:
                st.caption("⚡ High volatility")
            else:
                st.caption("📊 Moderate volatility")
        
        with col3:
            st.metric("Momentum", f"{dd['technicals']['momentum']*100:+.2f}%")
            if dd['technicals']['momentum'] > 0:
                st.caption("📈 Positive momentum")
            else:
                st.caption("📉 Negative momentum")
        
        # Price history table
        st.markdown("---")
        st.subheader("📅 Price Change History")
        
        changes_data = []
        for period, data in dd['price_changes'].items():
            changes_data.append({
                'Period': period.upper(),
                'Old Price': f"${data['old_price']:.2f}",
                'Change %': f"{data['change_pct']:+.2f}%",
                'Trend': '📈' if data['change_pct'] > 0 else '📉'
            })
        
        st.dataframe(pd.DataFrame(changes_data), use_container_width=True, hide_index=True)
    
    else:
        st.info("👆 Enter a ticker symbol and click 'Analyze' to perform due diligence")
        
        st.markdown("---")
        st.markdown("""
        ### 📚 Due Diligence Includes:
        
        - **Price Analysis**: Charts, moving averages, support/resistance levels
        - **Volume Analysis**: Current vs average volume, trends, surges
        - **Technical Indicators**: RSI, momentum, volatility metrics
        - **Risk Assessment**: Price level warnings, liquidity concerns
        - **Opportunity Signals**: Oversold/overbought conditions, momentum shifts
        - **Historical Performance**: 1-day, 5-day, 20-day, 30-day, 60-day changes
        
        ### ⚠️ Remember:
        - Penny stocks are extremely risky and volatile
        - Never invest more than you can afford to lose
        - Always use stop losses to limit downside
        - Do your own research beyond this tool
        - Past performance ≠ future results
        """)
