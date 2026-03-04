import streamlit as st

st.set_page_config(page_title="Live Trading", page_icon="⚡", layout="wide")

st.title("⚡ Live Trading (Alpaca/Tradier)")

st.markdown("""
Connect your brokerage account to execute trades automatically based on 
algorithmic signals.
""")

st.warning("⚠️ **Live trading is not enabled yet.** Add your API keys below for future integration.")

# Broker selection
broker = st.selectbox(
    "Select Broker",
    ["Alpaca", "Tradier", "Interactive Brokers (Coming Soon)"],
    help="Choose your brokerage platform"
)

st.subheader(f"🔑 {broker} API Configuration")

if broker == "Alpaca":
    st.markdown("""
    **Get your Alpaca API keys:**
    1. Sign up at [alpaca.markets](https://alpaca.markets)
    2. Go to Paper Trading or Live Trading dashboard
    3. Generate API Key and Secret
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        alpaca_key = st.text_input("Alpaca API Key", type="password", help="Your Alpaca API Key ID")
    
    with col2:
        alpaca_secret = st.text_input("Alpaca Secret Key", type="password", help="Your Alpaca Secret Key")
    
    paper_trading = st.checkbox("Use Paper Trading (Recommended for testing)", value=True)
    
    if alpaca_key and alpaca_secret:
        if st.button("✅ Verify Credentials"):
            st.success("✅ API keys saved (not verified yet - integration coming soon)")
            st.info("🔧 In the next update, we'll add: Account balance check, Position monitoring, Automated order execution")

elif broker == "Tradier":
    st.markdown("""
    **Get your Tradier API key:**
    1. Sign up at [tradier.com](https://tradier.com)
    2. Go to Settings > API Access
    3. Generate Access Token
    """)
    
    tradier_token = st.text_input("Tradier Access Token", type="password")
    
    if tradier_token:
        if st.button("✅ Verify Credentials"):
            st.success("✅ API token saved (not verified yet - integration coming soon)")

else:
    st.info("Interactive Brokers integration coming in a future update!")

# Features preview
st.markdown("---")
st.subheader("🚀 Coming Soon Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **💰 Account Management**
    - Real-time balance
    - Buying power
    - Position tracking
    - P&L monitoring
    """)

with col2:
    st.markdown("""
    **🤖 Auto-Trading**
    - Execute on signals
    - Risk management
    - Position sizing
    - Stop-loss orders
    """)

with col3:
    st.markdown("""
    **📊 Analytics**
    - Trade history
    - Performance metrics
    - Win/loss analysis
    - ROI tracking
    """)
