import streamlit as st
import sys
import os
import threading
import time
import json
from pathlib import Path
import datetime as dt

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.paper_trader import PaperTradingPortfolio
from core.auto_agent import AutoTradingAgent
import pandas as pd

# Default portfolio save path
DEFAULT_PORTFOLIO_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'portfolio_state.json'
)

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
if 'tickers' not in st.session_state:
    st.session_state['tickers'] = []
if 'check_interval' not in st.session_state:
    st.session_state['check_interval'] = 300
if 'portfolio_loaded' not in st.session_state:
    st.session_state['portfolio_loaded'] = False

# Auto-load portfolio from saved state (only once per session)
if not st.session_state['portfolio_loaded'] and os.path.exists(DEFAULT_PORTFOLIO_PATH):
    try:
        portfolio = PaperTradingPortfolio.load_from_file(DEFAULT_PORTFOLIO_PATH)
        
        # Try to load agent config if exists
        config_path = DEFAULT_PORTFOLIO_PATH.replace('.json', '_config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                st.session_state['tickers'] = config.get('tickers', [])
                st.session_state['check_interval'] = config.get('check_interval', 300)
                position_size = config.get('position_size', 1)
                
                # Recreate agent with loaded config
                if st.session_state['tickers']:
                    # Define save callback
                    def save_portfolio():
                        try:
                            portfolio.save_to_file(DEFAULT_PORTFOLIO_PATH)
                        except Exception as e:
                            print(f"Auto-save error: {e}")
                    
                    agent = AutoTradingAgent(
                        portfolio=portfolio,
                        tickers=st.session_state['tickers'],
                        check_interval=st.session_state['check_interval'],
                        position_size=position_size,
                        save_callback=save_portfolio
                    )
                    st.session_state['agent'] = agent
        
        st.session_state['portfolio'] = portfolio
        st.session_state['portfolio_loaded'] = True
        st.success(f"✅ Portfolio loaded from saved state! ({os.path.basename(DEFAULT_PORTFOLIO_PATH)})")
    except Exception as e:
        st.warning(f"⚠️ Could not load saved portfolio: {str(e)}")

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
                
                # Define save callback
                def save_portfolio():
                    try:
                        portfolio.save_to_file(DEFAULT_PORTFOLIO_PATH)
                    except Exception as e:
                        print(f"Auto-save error: {e}")
                
                # Create agent
                agent = AutoTradingAgent(
                    portfolio=portfolio,
                    tickers=tickers,
                    check_interval=check_interval,
                    position_size=contracts_per_trade,
                    save_callback=save_portfolio
                )
                
                st.session_state['portfolio'] = portfolio
                st.session_state['agent'] = agent
                st.session_state['tickers'] = tickers
                st.session_state['check_interval'] = check_interval
                
                # Save portfolio and config immediately
                try:
                    portfolio.save_to_file(DEFAULT_PORTFOLIO_PATH)
                    # Save agent config separately
                    config_path = DEFAULT_PORTFOLIO_PATH.replace('.json', '_config.json')
                    with open(config_path, 'w') as f:
                        json.dump({
                            'tickers': tickers,
                            'check_interval': check_interval,
                            'position_size': contracts_per_trade
                        }, f)
                    st.success(f"✅ Portfolio created and saved with ${starting_cash:,.0f}")
                except Exception as e:
                    st.success(f"✅ Portfolio created with ${starting_cash:,.0f}")
                    st.warning(f"⚠️ Could not auto-save: {str(e)}")
                
                st.rerun()
    
    with col2:
        if st.button("🗑️ Reset Portfolio", disabled=st.session_state['portfolio'] is None or st.session_state['agent_running']):
            # Delete saved files
            if os.path.exists(DEFAULT_PORTFOLIO_PATH):
                os.remove(DEFAULT_PORTFOLIO_PATH)
            config_path = DEFAULT_PORTFOLIO_PATH.replace('.json', '_config.json')
            if os.path.exists(config_path):
                os.remove(config_path)
            
            st.session_state['portfolio'] = None
            st.session_state['agent'] = None
            st.session_state['agent_running'] = False
            st.session_state['portfolio_loaded'] = False
            st.success("Portfolio reset and saved state cleared")
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
    
    # Manual save/load section
    if st.session_state['portfolio']:
        st.markdown("---")
        st.markdown("**💾 Local Save/Load**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Save Portfolio", help="Manually save current portfolio state"):
                try:
                    portfolio = st.session_state['portfolio']
                    portfolio.save_to_file(DEFAULT_PORTFOLIO_PATH)
                    # Save agent config
                    config_path = DEFAULT_PORTFOLIO_PATH.replace('.json', '_config.json')
                    with open(config_path, 'w') as f:
                        json.dump({
                            'tickers': st.session_state.get('tickers', []),
                            'check_interval': st.session_state.get('check_interval', 300),
                            'position_size': st.session_state['agent'].position_size if st.session_state['agent'] else 1
                        }, f)
                    st.success(f"✅ Portfolio saved to {os.path.basename(DEFAULT_PORTFOLIO_PATH)}")
                except Exception as e:
                    st.error(f"❌ Save failed: {str(e)}")
        
        with col2:
            st.caption(f"📁 {os.path.basename(DEFAULT_PORTFOLIO_PATH)}")
            if os.path.exists(DEFAULT_PORTFOLIO_PATH):
                file_time = os.path.getmtime(DEFAULT_PORTFOLIO_PATH)
                from datetime import datetime
                st.caption(f"Last saved: {datetime.fromtimestamp(file_time).strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Supabase cloud sync section
        st.markdown("---")
        st.markdown("**☁️ Supabase Cloud Sync**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            supabase_url = st.text_input(
                "Supabase URL",
                value=os.getenv('SUPABASE_URL', ''),
                help="Your Supabase project URL",
                key="supabase_url",
                type="password"
            )
            supabase_key = st.text_input(
                "Supabase Key",
                value=os.getenv('SUPABASE_KEY', ''),
                help="Your Supabase API key",
                key="supabase_key",
                type="password"
            )
        
        with col2:
            portfolio_name = st.text_input(
                "Portfolio Name",
                value="default",
                help="Unique name for this portfolio",
                key="portfolio_name"
            )
            
            if st.button("☁️ Sync to Cloud", help="Save portfolio to Supabase"):
                with st.spinner("Syncing to Supabase..."):
                    try:
                        # Temporarily set env vars if provided
                        if supabase_url:
                            os.environ['SUPABASE_URL'] = supabase_url
                        if supabase_key:
                            os.environ['SUPABASE_KEY'] = supabase_key
                        
                        portfolio = st.session_state['portfolio']
                        
                        # Prepare agent config
                        agent_config = {
                            'tickers': st.session_state.get('tickers', []),
                            'check_interval': st.session_state.get('check_interval', 300),
                            'position_size': st.session_state['agent'].position_size if st.session_state.get('agent') else 1
                        }
                        
                        success, result = portfolio.save_to_supabase(portfolio_name, agent_config)
                        
                        if success:
                            st.success(f"✅ Synced to Supabase!")
                            st.info(f"💾 {result}")
                        else:
                            st.error(f"❌ Sync failed: {result}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        st.info("💡 Make sure you have SUPABASE_URL and SUPABASE_KEY set. See setup instructions below.")
            
            if st.button("📥 Load from Cloud", help="Load portfolio from Supabase"):
                with st.spinner("Loading from Supabase..."):
                    error_occurred = False
                    try:
                        # Temporarily set env vars if provided
                        if supabase_url:
                            os.environ['SUPABASE_URL'] = supabase_url
                        if supabase_key:
                            os.environ['SUPABASE_KEY'] = supabase_key
                        
                        # First check if the connection works
                        from core.supabase_sync import setup_supabase_sync
                        sync = setup_supabase_sync()
                        
                        if not sync:
                            st.error("❌ Failed to connect to Supabase. Check your credentials.")
                            st.info("💡 Make sure SUPABASE_URL and SUPABASE_KEY are set in .env or entered above.")
                            error_occurred = True
                        else:
                            # Try to load raw data first to see what's happening
                            data = sync.load_portfolio(portfolio_name)
                            
                            if not data:
                                st.warning(f"⚠️ No portfolio found with name '{portfolio_name}' in Supabase")
                                st.info("💡 Make sure you've saved a portfolio with 'Sync to Cloud' first.")
                                error_occurred = True
                            else:
                                # Now try to reconstruct the portfolio
                                from core.paper_trader import PaperTradingPortfolio
                                from core.auto_agent import AutoTradingAgent
                                
                                loaded_portfolio = PaperTradingPortfolio.load_from_supabase(portfolio_name)
                                
                                if not loaded_portfolio:
                                    st.error("❌ Failed to reconstruct portfolio from database")
                                    st.info("💡 Raw data was found but couldn't be loaded. Check console for details.")
                                    error_occurred = True
                                else:
                                    st.session_state['portfolio'] = loaded_portfolio
                                    
                                    # Get agent config from portfolio data
                                    if data['portfolio'].get('agent_config'):
                                        import json
                                        agent_config = json.loads(data['portfolio']['agent_config'])
                                        
                                        # Recreate agent with saved config
                                        tickers = agent_config.get('tickers', [])
                                        check_interval = agent_config.get('check_interval', 300)
                                        position_size = agent_config.get('position_size', 1)
                                        
                                        if tickers:
                                            # Define save callback
                                            def save_portfolio():
                                                try:
                                                    loaded_portfolio.save_to_file(DEFAULT_PORTFOLIO_PATH)
                                                except Exception as e:
                                                    print(f"Auto-save error: {e}")
                                            
                                            agent = AutoTradingAgent(
                                                portfolio=loaded_portfolio,
                                                tickers=tickers,
                                                check_interval=check_interval,
                                                position_size=position_size,
                                                save_callback=save_portfolio
                                            )
                                            
                                            st.session_state['agent'] = agent
                                            st.session_state['tickers'] = tickers
                                            st.session_state['check_interval'] = check_interval
                                    
                                    st.success(f"✅ Loaded portfolio from Supabase!")
                                    st.info(f"📊 Portfolio Value: ${loaded_portfolio.get_portfolio_value():,.2f} | Open Positions: {len(loaded_portfolio.get_open_positions())}")
                    
                    except Exception as e:
                        st.error(f"❌ Error loading from Supabase: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc(), language="python")
                        st.info("💡 Common fixes:\n- Run the migration SQL if agent_config column is missing\n- Check that your Supabase credentials are correct\n- Verify the portfolio name matches what you saved")
                        error_occurred = True
                    
                    # Only rerun if no error occurred and we successfully loaded
                    if not error_occurred:
                        st.rerun()
        
        # Setup instructions expander
        with st.expander("📖 Supabase Setup Instructions (Free - 2 minutes)"):
            st.markdown("""
            **Step 1: Create Free Supabase Account**
            1. Go to [supabase.com](https://supabase.com/)
            2. Click "Start your project"
            3. Sign in with GitHub (or email)
            
            **Step 2: Create New Project**
            1. Click "New Project"
            2. Choose organization (or create one)
            3. Enter project name (e.g., "algo-trader")
            4. Create a strong database password
            5. Choose region closest to you
            6. Click "Create new project" (wait ~2 minutes for setup)
            
            **Step 3: Get Your Credentials**
            1. Go to Project Settings (gear icon) > API
            2. Find "Project URL" - copy this
            3. Find "anon public" key under "Project API keys" - copy this
            
            **Step 4: Create Tables (Run SQL)**
            1. Go to SQL Editor (left sidebar)
            2. Click "New Query"
            3. Paste this SQL:
            
            ```sql
            -- Portfolios table
            CREATE TABLE IF NOT EXISTS portfolios (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                starting_cash NUMERIC NOT NULL,
                current_cash NUMERIC NOT NULL,
                max_position_size NUMERIC NOT NULL,
                max_positions INTEGER NOT NULL,
                agent_config TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            -- Positions table
            CREATE TABLE IF NOT EXISTS positions (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                portfolio_id UUID REFERENCES portfolios(id) ON DELETE CASCADE,
                ticker TEXT NOT NULL,
                option_type TEXT NOT NULL,
                strike NUMERIC NOT NULL,
                expiration TIMESTAMP WITH TIME ZONE NOT NULL,
                quantity INTEGER NOT NULL,
                entry_price NUMERIC NOT NULL,
                entry_date TIMESTAMP WITH TIME ZONE NOT NULL,
                exit_price NUMERIC,
                exit_date TIMESTAMP WITH TIME ZONE,
                status TEXT NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            -- Trades table
            CREATE TABLE IF NOT EXISTS trades (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                portfolio_id UUID REFERENCES portfolios(id) ON DELETE CASCADE,
                date TIMESTAMP WITH TIME ZONE NOT NULL,
                ticker TEXT,
                action TEXT,
                option_type TEXT,
                strike NUMERIC,
                quantity INTEGER,
                price NUMERIC,
                cost NUMERIC,
                pnl NUMERIC,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            -- Create indexes for better performance
            CREATE INDEX IF NOT EXISTS idx_positions_portfolio ON positions(portfolio_id);
            CREATE INDEX IF NOT EXISTS idx_trades_portfolio ON trades(portfolio_id);
            ```
            
            4. Click "Run" to create the tables
            
            **Step 5: Use Your Credentials**
            - Either paste them in the fields above, OR
            - Create a `.env` file in your project folder with:
            ```
            SUPABASE_URL=your_project_url_here
            SUPABASE_KEY=your_anon_key_here
            ```
            
            ---
            
            **⚠️ IMPORTANT: If you created tables before, run this migration:**
            
            If you already created the tables earlier (before agent_config was added), go to SQL Editor and run:
            
            ```sql
            ALTER TABLE portfolios ADD COLUMN IF NOT EXISTS agent_config TEXT;
            ```
            
            This adds support for saving your agent configuration (tickers, check interval, etc.) to the cloud.
            
            ---
            
            **That's it!** Click "☁️ Sync to Cloud" to save your portfolio. It's free up to 500MB!
            
            **Benefits over Google Sheets:**
            - ✅ No JSON credentials needed
            - ✅ Faster (real database vs spreadsheet)
            - ✅ More secure
            - ✅ Better for trading data
            - ✅ 2-minute setup vs 15 minutes
            """)
        
        # Current status
        st.markdown("---")
        status_text = '🟢 RUNNING' if st.session_state['agent_running'] else '🔴 STOPPED'
        tickers_str = ', '.join(st.session_state.get('tickers', []))
        st.info(f"📊 Portfolio Active | Monitoring: {tickers_str} | Status: {status_text}")

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
                # Convert timestamps to datetime if needed
                if isinstance(pos.entry_date, (int, float)):
                    entry_date = dt.datetime.fromtimestamp(pos.entry_date)
                else:
                    entry_date = pos.entry_date
                    
                if isinstance(pos.expiration, (int, float)):
                    expiration = dt.datetime.fromtimestamp(pos.expiration)
                else:
                    expiration = pos.expiration
                
                # Remove timezone info for comparison (if present)
                now = dt.datetime.now()
                if hasattr(entry_date, 'tzinfo') and entry_date.tzinfo is not None:
                    entry_date = entry_date.replace(tzinfo=None)
                if hasattr(expiration, 'tzinfo') and expiration.tzinfo is not None:
                    expiration = expiration.replace(tzinfo=None)
                
                days_held = (now - entry_date).days
                days_to_expiry = (expiration - now).days
                cost = pos.entry_price * pos.quantity * 100
                
                positions_data.append({
                    'Ticker': pos.ticker,
                    'Type': pos.option_type.upper(),
                    'Strike': f"${pos.strike:.2f}",
                    'Qty': pos.quantity,
                    'Entry Price': f"${pos.entry_price:.2f}",
                    'Entry Date': entry_date.strftime('%Y-%m-%d'),
                    'Days Held': days_held,
                    'Expiration': expiration.strftime('%Y-%m-%d'),
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
                # Convert timestamps to datetime if needed
                if isinstance(pos.entry_date, (int, float)):
                    entry_date = dt.datetime.fromtimestamp(pos.entry_date)
                else:
                    entry_date = pos.entry_date
                    
                if isinstance(pos.exit_date, (int, float)):
                    exit_date = dt.datetime.fromtimestamp(pos.exit_date)
                elif pos.exit_date is None:
                    exit_date = None
                else:
                    exit_date = pos.exit_date
                
                # Remove timezone info (if present)
                if hasattr(entry_date, 'tzinfo') and entry_date.tzinfo is not None:
                    entry_date = entry_date.replace(tzinfo=None)
                if exit_date and hasattr(exit_date, 'tzinfo') and exit_date.tzinfo is not None:
                    exit_date = exit_date.replace(tzinfo=None)
                
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
                    'Entry Date': entry_date.strftime('%Y-%m-%d'),
                    'Exit Date': exit_date.strftime('%Y-%m-%d') if exit_date else 'N/A'
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
                        # Auto-save after cycle
                        try:
                            st.session_state['portfolio'].save_to_file(DEFAULT_PORTFOLIO_PATH)
                        except:
                            pass
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
                    # Auto-save after cycle
                    try:
                        st.session_state['portfolio'].save_to_file(DEFAULT_PORTFOLIO_PATH)
                    except:
                        pass
                    st.rerun()
