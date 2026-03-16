import streamlit as st
import sys
import os
import threading
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.paper_trader import PaperTradingPortfolio
from core.auto_agent import AutoTradingAgent
import pandas as pd

st.set_page_config(page_title="Paper Trading Agent", page_icon="🤖", layout="wide")

st.title("🤖 Paper Trading Agent")

st.markdown("""
Automated trading agent that monitors stocks and executes options trades based on algo_engine signals.
Uses virtual money to simulate real trading without risk.
""")

# Initialize session state
if 'portfolio' not in st.session_state:
    st.session_state['portfolio'] = None
if 'agent' not in st.session_state:
    st.session_state['agent'] = None
if 'agent_running' not in st.session_state:
    st.session_state['agent_running'] = False
if 'agent_thread' not in st.session_state:
    st.session_state['agent_thread'] = None

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["⚙️ Setup", "📊 Portfolio", "📈 Positions", "📜 Trade Log"])

# ----- TAB 1: SETUP -----
with tab1:
    st.subheader("🎯 Agent Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**💰 Portfolio Settings**")
        
        starting_cash = st.number_input(
            "Starting Cash",
            min_value=1000,
            max_value=1000000,
            value=10000,
            step=1000,
            help="Virtual money to start with"
        )
        
        max_positions = st.slider(
            "Max Open Positions",
            min_value=1,
            max_value=20,
            value=5,
            help="Maximum number of simultaneous positions"
        )
        
        position_size_pct = st.slider(
            "Max Position Size (%)",
            min_value=1,
            max_value=20,
            value=5,
            help="Maximum % of portfolio per position"
        )
        
        contracts_per_trade = st.number_input(
            "Contracts Per Trade",
            min_value=1,
            max_value=10,
            value=1,
            help="Number of option contracts to buy per signal"
        )
    
    with col2:
        st.markdown("**📡 Monitoring Settings**")
        
        tickers_input = st.text_area(
            "Tickers to Monitor",
            value="AAPL\nMSFT\nTSLA\nAMD\nNVDA",
            height=150,
            help="Enter one ticker per line"
        )
        
        check_interval = st.selectbox(
            "Check Interval",
            [60, 300, 600, 1800, 3600],
            index=1,
            format_func=lambda x: {
                60: "1 minute",
                300: "5 minutes",
                600: "10 minutes",
                1800: "30 minutes",
                3600: "1 hour"
            }[x]
        )
    
    st.markdown("---")
    
    # Control buttons
    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
    
    with col1:
        if st.button("🚀 Create Portfolio", type="primary", disabled=st.session_state['portfolio'] is not None):
            # Parse tickers
            tickers = [t.strip().upper() for t in tickers_input.split('\n') if t.strip()]
            
            if not tickers:
                st.error("Please enter at least one ticker")
            else:
                # Create portfolio
                portfolio = PaperTradingPortfolio(
                    starting_cash=starting_cash,
                    max_position_size=position_size_pct / 100,
                    max_positions=max_positions
                )
                
                # Create agent
                agent = AutoTradingAgent(
                    portfolio=portfolio,
                    tickers=tickers,
                    check_interval=check_interval,
                    position_size=contracts_per_trade
                )
                
                st.session_state['portfolio'] = portfolio
                st.session_state['agent'] = agent
                st.session_state['tickers'] = tickers
                
                st.success(f"✅ Portfolio created with ${starting_cash:,.0f}")
                st.rerun()
    
    with col2:
        if st.button("🗑️ Reset Portfolio", disabled=st.session_state['portfolio'] is None or st.session_state['agent_running']):
            st.session_state['portfolio'] = None
            st.session_state['agent'] = None
            st.session_state['agent_running'] = False
            st.success("Portfolio reset")
            st.rerun()
    
    with col3:
        if st.button("▶️ Start Agent", type="primary", 
                    disabled=st.session_state['portfolio'] is None or st.session_state['agent_running']):
            st.session_state['agent_running'] = True
            st.success("🤖 Agent started! Check the Trade Log tab for updates.")
            st.info("💡 The agent will check for signals every " + 
                   {60: "minute", 300: "5 minutes", 600: "10 minutes", 
                    1800: "30 minutes", 3600: "hour"}[check_interval])
    
    with col4:
        if st.button("⏹️ Stop Agent", disabled=not st.session_state['agent_running']):
            if st.session_state['agent']:
                st.session_state['agent'].stop()
            st.session_state['agent_running'] = False
            st.warning("Agent stopped")
            st.rerun()
    
    # Current status
    if st.session_state['portfolio']:
        st.markdown("---")
        st.info(f"📊 Portfolio Active | Monitoring: {', '.join(st.session_state.get('tickers', []))} | "
               f"Status: {'🟢 RUNNING' if st.session_state['agent_running'] else '🔴 STOPPED'}")

# ----- TAB 2: PORTFOLIO -----
with tab2:
    if st.session_state['portfolio'] is None:
        st.info("👈 Create a portfolio in the Setup tab to get started")
    else:
        portfolio = st.session_state['portfolio']
        
        # Key metrics
        stats = portfolio.get_statistics()
        portfolio_value = portfolio.get_portfolio_value()
        total_return = ((portfolio_value - portfolio.starting_cash) / portfolio.starting_cash * 100)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Portfolio Value", f"${portfolio_value:,.2f}", 
                     f"{total_return:+.2f}%")
        
        with col2:
            st.metric("Cash", f"${portfolio.cash:,.2f}")
        
        with col3:
            st.metric("Open Positions", len(portfolio.get_open_positions()))
        
        with col4:
            st.metric("Total Trades", stats['total_trades'])
        
        st.markdown("---")
        
        # Statistics
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Performance Stats")
            
            # Create metrics dataframe
            metrics_data = {
                'Metric': [
                    'Win Rate',
                    'Winning Trades',
                    'Losing Trades',
                    'Total P&L',
                    'Avg P&L',
                    'Best Trade',
                    'Worst Trade'
                ],
                'Value': [
                    f"{stats['win_rate']:.1f}%",
                    stats['winning_trades'],
                    stats['losing_trades'],
                    f"${stats['total_pnl']:,.2f}",
                    f"${stats['avg_pnl']:,.2f}",
                    f"${stats['best_trade']:,.2f}",
                    f"${stats['worst_trade']:,.2f}"
                ]
            }
            
            st.dataframe(pd.DataFrame(metrics_data), use_container_width=True, hide_index=True)
        
        with col2:
            st.subheader("💼 Portfolio Allocation")
            
            open_positions = portfolio.get_open_positions()
            
            if open_positions:
                # Calculate allocation by ticker
                allocation = {}
                for pos in open_positions:
                    value = pos.entry_price * pos.quantity * 100
                    if pos.ticker in allocation:
                        allocation[pos.ticker] += value
                    else:
                        allocation[pos.ticker] = value
                
                # Add cash
                allocation['CASH'] = portfolio.cash
                
                # Create pie chart data
                alloc_df = pd.DataFrame([
                    {'Asset': k, 'Value': v, 'Percentage': v/portfolio_value*100}
                    for k, v in allocation.items()
                ])
                
                st.dataframe(alloc_df, use_container_width=True, hide_index=True)
            else:
                st.info("No open positions yet")

# ----- TAB 3: POSITIONS -----
with tab3:
    if st.session_state['portfolio'] is None:
        st.info("👈 Create a portfolio in the Setup tab to get started")
    else:
        portfolio = st.session_state['portfolio']
        
        st.subheader("📈 Open Positions")
        
        open_positions = portfolio.get_open_positions()
        
        if open_positions:
            positions_data = []
            
            for pos in open_positions:
                days_held = (pd.Timestamp.now() - pos.entry_date).days
                days_to_expiry = (pos.expiration - pd.Timestamp.now()).days
                cost = pos.entry_price * pos.quantity * 100
                
                positions_data.append({
                    'Ticker': pos.ticker,
                    'Type': pos.option_type.upper(),
                    'Strike': f"${pos.strike:.2f}",
                    'Qty': pos.quantity,
                    'Entry Price': f"${pos.entry_price:.2f}",
                    'Entry Date': pos.entry_date.strftime('%Y-%m-%d'),
                    'Days Held': days_held,
                    'Expiration': pos.expiration.strftime('%Y-%m-%d'),
                    'Days to Expiry': days_to_expiry,
                    'Cost': f"${cost:.2f}"
                })
            
            df = pd.DataFrame(positions_data)
            st.dataframe(df, use_container_width=True, hide_index=True, height=400)
        else:
            st.info("No open positions")
        
        # Closed positions
        st.markdown("---")
        st.subheader("📋 Closed Positions (Last 20)")
        
        closed_positions = portfolio.get_closed_positions()[-20:]  # Last 20
        
        if closed_positions:
            closed_data = []
            
            for pos in closed_positions:
                pnl = pos.get_pnl()
                pnl_pct = pos.get_pnl_percent()
                
                closed_data.append({
                    'Ticker': pos.ticker,
                    'Type': pos.option_type.upper(),
                    'Strike': f"${pos.strike:.2f}",
                    'Qty': pos.quantity,
                    'Entry': f"${pos.entry_price:.2f}",
                    'Exit': f"${pos.exit_price:.2f}",
                    'P&L': f"${pnl:.2f}",
                    'P&L %': f"{pnl_pct:+.1f}%",
                    'Entry Date': pos.entry_date.strftime('%Y-%m-%d'),
                    'Exit Date': pos.exit_date.strftime('%Y-%m-%d') if pos.exit_date else 'N/A'
                })
            
            df = pd.DataFrame(closed_data)
            st.dataframe(df, use_container_width=True, hide_index=True, height=400)
        else:
            st.info("No closed positions yet")

# ----- TAB 4: TRADE LOG -----
with tab4:
    if st.session_state['agent'] is None:
        st.info("👈 Create a portfolio in the Setup tab to get started")
    else:
        agent = st.session_state['agent']
        
        st.subheader("📜 Agent Activity Log")
        
        # Run agent cycles if running
        if st.session_state['agent_running']:
            with st.container():
                st.info("🤖 Agent is running... Checking signals automatically")
                
                # Show last cycle time
                if agent.log:
                    st.caption(f"Last activity: {agent.log[-1]}")
                
                # Run a cycle (non-blocking check)
                if st.button("🔄 Force Check Now"):
                    with st.spinner("Running cycle..."):
                        agent.run_cycle()
                        st.rerun()
        
        # Display log
        if agent.log:
            log_text = "\n".join(agent.log[-100:])  # Last 100 lines
            st.text_area("Activity Log", value=log_text, height=500, disabled=True)
        else:
            st.info("No activity yet. Start the agent to begin monitoring.")
        
        # Manual cycle trigger for debugging
        if not st.session_state['agent_running']:
            st.markdown("---")
            if st.button("🔧 Run Test Cycle (Manual)", help="Run one check cycle manually"):
                with st.spinner("Running test cycle..."):
                    agent.run_cycle()
                    st.rerun()
