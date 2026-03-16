import streamlit as st

st.set_page_config(
    page_title="Options Algo Terminal", 
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Options Algo Trading Terminal")

st.markdown("""
### Welcome to the Options Algo Trading Terminal! 🚀

This platform provides automated algorithmic trading signals and backtesting 
for options trading strategies.

#### 🛠️ Features:

**🔍 Algo Engine** - Get real-time trading signals and option recommendations
- Technical analysis with RSI, moving averages, and momentum indicators
- Automated strategy recommendations (BUY_CALL, BUY_PUT, etc.)
- Contract selection with optimal strike prices and expirations

**📊 Backtester** - Test strategies on historical data
- Simulate trading performance over time
- Track P&L, win rates, and trade statistics
- Validate strategy effectiveness before going live

**🔎 Stock Suggester** - Discover weekly options trading opportunities
- Scan the market for affordable options ($10-30 per contract)
- Filter by liquidity, volatility, and technical signals
- Get ranked recommendations with best contracts
- Quick scan (10 stocks) or full market scan (50+ stocks)

**💰 Penny Stock Movers** - Track high-volume penny stocks and perform DD
- Real-time scanner for penny stocks under $10
- Sort by momentum, volume surge, or overall score
- Comprehensive due diligence reports with charts
- Risk assessment and opportunity identification

**🤖 Paper Trading Agent** - Automated trading with virtual money
- Set up portfolio with fake money ($1K-$1M)
- Agent monitors stocks and executes based on algo_engine signals
- Track positions, P&L, and trade history in real-time
- Test strategies without risk before going live

**⚡ Live Trading** - Execute trades automatically (Coming Soon)
- Integration with Alpaca and Tradier APIs
- Automated order execution based on signals
- Real-time position monitoring

---

### 👉 Get Started

Use the **sidebar** on the left to navigate between different modules.

**For Analysis:**
1. Click on **🔍 Algo Engine** in the sidebar
2. Enter a ticker symbol (e.g., AAPL, MSFT, TSLA)
3. Click Analyze to get trading signals

**For Paper Trading:**
1. Click on **🤖 Paper Trading Agent** in the sidebar
2. Configure your virtual portfolio ($10K recommended)
3. Add tickers to monitor and start the agent
4. Watch it trade automatically based on signals!

---

### ⚠️ Disclaimer

This tool is for educational and research purposes only. Always do your own 
research and consult with a financial advisor before making investment decisions.
Past performance does not guarantee future results.
""")

# Status indicators
st.sidebar.success("System Online ✅")

with st.sidebar:
    st.markdown("---")
    st.markdown("### 📊 System Status")
    st.markdown("🟢 Data Feed: Active")
    st.markdown("🟢 Indicators: Active")
    st.markdown("🟢 Signals: Active")
    st.markdown("� Paper Trading: Active")
    st.markdown("�🔴 Live Trading: Disabled")
