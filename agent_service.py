"""
Standalone Trading Agent Service
Runs independently of Streamlit UI - can be deployed to cloud or run as background service
Reads config from Supabase, executes trades, writes results back to Supabase
"""
import os
import time
import logging
from datetime import datetime
from dotenv import load_dotenv
from core.paper_trader import PaperTradingPortfolio
from core.supabase_sync import setup_supabase_sync
import traceback

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CloudTradingAgent:
    """Autonomous trading agent that runs independently"""
    
    def __init__(self, portfolio_name: str):
        self.portfolio_name = portfolio_name
        self.portfolio = None
        self.agent_config = None
        self.sync = None
        self.running = False
        
    def load_from_cloud(self):
        """Load portfolio and configuration from Supabase"""
        try:
            logger.info(f"Loading portfolio '{self.portfolio_name}' from Supabase...")
            
            # Setup Supabase connection
            self.sync = setup_supabase_sync()
            if not self.sync:
                raise Exception("Failed to connect to Supabase")
            
            # Load portfolio data
            data = self.sync.load_portfolio(self.portfolio_name)
            if not data:
                raise Exception(f"Portfolio '{self.portfolio_name}' not found")
            
            # Reconstruct portfolio
            self.portfolio = PaperTradingPortfolio.load_from_supabase(self.portfolio_name)
            
            # Load agent configuration (use defaults if missing)
            # agent_config is inside data['portfolio'], not data directly
            agent_config_raw = data['portfolio'].get('agent_config') if 'portfolio' in data else None
            
            logger.info(f"Raw agent_config from Supabase: {agent_config_raw}")
            
            # Parse agent_config if it exists
            if agent_config_raw:
                if isinstance(agent_config_raw, str):
                    # Parse JSON string
                    import json
                    try:
                        self.agent_config = json.loads(agent_config_raw)
                    except json.JSONDecodeError:
                        logger.warning("Failed to parse agent_config JSON, using defaults")
                        self.agent_config = {}
                elif isinstance(agent_config_raw, dict):
                    self.agent_config = agent_config_raw
                else:
                    logger.warning(f"Unexpected agent_config type: {type(agent_config_raw)}, using defaults")
                    self.agent_config = {}
            else:
                logger.warning("No agent_config found in portfolio, using defaults")
                self.agent_config = {}
            
            # Set defaults for missing values
            if 'tickers' not in self.agent_config or not self.agent_config['tickers']:
                self.agent_config['tickers'] = ['AAPL', 'NVDA', 'TSLA']
                logger.warning(f"No tickers configured, using defaults: {self.agent_config['tickers']}")
            
            if 'check_interval' not in self.agent_config:
                self.agent_config['check_interval'] = 300  # 5 minutes
                logger.warning(f"No check_interval configured, using default: 300 seconds")
            
            if 'position_size' not in self.agent_config:
                self.agent_config['position_size'] = 1
                logger.warning(f"No position_size configured, using default: 1 contract")
            
            logger.info(f"✅ Loaded portfolio: ${self.portfolio.get_portfolio_value():,.2f}")
            logger.info(f"📊 Agent config: {self.agent_config}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load from cloud: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    def save_to_cloud(self):
        """Save portfolio state to Supabase"""
        try:
            success, result = self.portfolio.save_to_supabase(
                self.portfolio_name, 
                self.agent_config
            )
            if success:
                logger.info(f"💾 Synced to cloud: {result}")
            else:
                logger.error(f"Failed to sync: {result}")
            return success
        except Exception as e:
            logger.error(f"Error syncing to cloud: {str(e)}")
            return False
    
    def check_and_execute_trades(self):
        """Check for trading opportunities and execute trades"""
        try:
            tickers = self.agent_config.get('tickers', [])
            position_size = self.agent_config.get('position_size', 1)
            
            if not tickers:
                logger.warning("No tickers configured")
                return
            
            logger.info(f"🔍 Checking {len(tickers)} tickers for opportunities...")
            
            # Import trading logic (same as auto_agent)
            from core.data import load_history, get_current_price
            from core.indicators import compute_indicators
            from core.signals import generate_signal
            from core.strategies import decide_action
            from core.contracts import load_options_chain, find_best_option, get_next_week_expiration
            import pandas as pd
            import datetime as dt
            
            for ticker in tickers:
                try:
                    logger.info(f"Analyzing {ticker}...")
                    
                    # Load historical data
                    df = load_history(ticker, days=60)
                    if df is None or len(df) < 20:
                        logger.warning(f"Insufficient data for {ticker}")
                        continue
                    
                    # Compute indicators
                    df = compute_indicators(df)
                    
                    # Generate signal
                    signal = generate_signal(df)
                    
                    # Decide action
                    action = decide_action(signal)
                    
                    logger.info(f"{ticker}: Signal = {action}")
                    
                    if action in ['BUY_CALL', 'BUY_PUT']:
                        logger.info(f"🎯 {action} signal for {ticker}")
                        
                        # Get current price
                        current_price = get_current_price(ticker)
                        if not current_price:
                            logger.warning(f"No current price for {ticker}")
                            continue
                        
                        # Check if we already have an open position
                        has_position = any(
                            p.ticker == ticker and p.status == 'open' 
                            for p in self.portfolio.positions
                        )
                        
                        if has_position:
                            logger.info(f"Already have open position in {ticker}, skipping")
                            continue
                        
                        # Check if we can open a new position
                        open_count = len([p for p in self.portfolio.positions if p['status'] == 'open'])
                        if open_count >= self.portfolio.max_positions:
                            logger.info(f"Max positions reached ({self.portfolio.max_positions}), skipping")
                            continue
                        
                        # Get next week expiration
                        expiration = get_next_week_expiration(ticker)
                        if expiration is None:
                            logger.warning(f"No suitable expiration date found for {ticker}")
                            continue
                        
                        # Log expiration info
                        exp_date = dt.datetime.fromtimestamp(expiration)
                        days_until = (exp_date - dt.datetime.now()).days
                        logger.info(f"{ticker}: Using expiration {exp_date.strftime('%Y-%m-%d')} ({days_until} days away)")
                        
                        # Load options chain
                        options_data = load_options_chain(ticker, expiration)
                        if options_data is None:
                            logger.warning(f"No options data for {ticker}")
                            continue
                        
                        # Extract calls and puts
                        df_calls = options_data.get('calls', pd.DataFrame())
                        df_puts = options_data.get('puts', pd.DataFrame())
                        
                        # Find best contract
                        contract_df = None
                        option_type = None
                        
                        if action == 'BUY_CALL' and len(df_calls) > 0:
                            contract_df = find_best_option(options_data, option_type='call', criteria='otm')
                            option_type = 'call'
                        elif action == 'BUY_PUT' and len(df_puts) > 0:
                            contract_df = find_best_option(options_data, option_type='put', criteria='otm')
                            option_type = 'put'
                        
                        if contract_df is None or len(contract_df) == 0:
                            logger.warning(f"No suitable contract found for {ticker}")
                            continue
                        
                        contract = contract_df.iloc[0]
                        cost = contract['lastPrice'] * position_size * 100
                        
                        # Check if we can afford it
                        can_open, reason = self.portfolio.can_open_position(cost)
                        if not can_open:
                            logger.info(f"Cannot open position on {ticker}: {reason}")
                            continue
                        
                        # Open position
                        logger.info(f"🚀 Opening {action} on {ticker}:")
                        logger.info(f"   Strike: ${contract['strike']:.2f}")
                        logger.info(f"   Price: ${contract['lastPrice']:.2f}")
                        logger.info(f"   Cost: ${cost:.2f}")
                        
                        success, result = self.portfolio.open_position(
                            ticker=ticker,
                            option_type=option_type,
                            strike=contract['strike'],
                            expiration=expiration,
                            quantity=position_size,
                            price=contract['lastPrice']
                        )
                        
                        if success:
                            logger.info(f"✅ Position opened successfully")
                            logger.info(f"   Cash remaining: ${self.portfolio.cash:.2f}")
                            
                            # Save to cloud after trade
                            self.save_to_cloud()
                        else:
                            logger.error(f"Failed to open position: {result}")
                    
                except Exception as e:
                    logger.error(f"Error processing {ticker}: {str(e)}")
                    logger.error(traceback.format_exc())
                    continue
            
            # Check exit conditions for open positions
            logger.info("Checking exit conditions for open positions...")
            open_positions = [p for p in self.portfolio.positions if p.status == 'open']
            
            for pos in open_positions:
                try:
                    # Convert expiration to datetime if needed
                    if isinstance(pos.expiration, (int, float)):
                        expiration_dt = dt.datetime.fromtimestamp(pos.expiration)
                    else:
                        expiration_dt = pos.expiration
                    
                    days_to_expiry = (expiration_dt - dt.datetime.now()).days
                    
                    # Close if 1 day or less to expiration
                    if days_to_expiry <= 1:
                        logger.info(f"🔔 Closing {pos.ticker} {pos.option_type} - Near expiration ({days_to_expiry} days)")
                        
                        # Close at entry price (simplified - in production would get current price)
                        exit_success = self.portfolio.close_position(
                            ticker=pos.ticker,
                            strike=pos.strike,
                            option_type=pos.option_type,
                            expiration=pos.expiration,
                            exit_price=pos.entry_price
                        )
                        
                        if exit_success:
                            logger.info(f"✅ Position closed")
                            self.save_to_cloud()
                
                except Exception as e:
                    logger.error(f"Error checking exit for {getattr(pos, 'ticker', 'unknown')}: {str(e)}")
                    continue
            
            logger.info(f"📊 Portfolio value: ${self.portfolio.get_portfolio_value():,.2f}")
            logger.info(f"💰 Cash: ${self.portfolio.cash:.2f}")
            logger.info(f"📈 Open positions: {len(open_positions)}")
            
        except Exception as e:
            logger.error(f"Error in check_and_execute_trades: {str(e)}")
            logger.error(traceback.format_exc())
    
    def run(self):
        """Main loop - runs continuously"""
        logger.info("=" * 60)
        logger.info("🤖 Cloud Trading Agent Starting...")
        logger.info("=" * 60)
        
        # Load initial state
        if not self.load_from_cloud():
            logger.error("Failed to load from cloud. Exiting.")
            return
        
        self.running = True
        check_interval = self.agent_config.get('check_interval', 300)  # Default 5 minutes
        
        logger.info(f"⏱️  Check interval: {check_interval} seconds")
        logger.info(f"📊 Tickers: {', '.join(self.agent_config.get('tickers', []))}")
        logger.info(f"💰 Position size: {self.agent_config.get('position_size', 1)} contracts")
        logger.info("🟢 Agent is now running...")
        
        while self.running:
            try:
                # Execute trading logic
                self.check_and_execute_trades()
                
                # Wait for next check
                logger.info(f"⏳ Sleeping for {check_interval} seconds...")
                time.sleep(check_interval)
                
            except KeyboardInterrupt:
                logger.info("\n⚠️  Keyboard interrupt received. Shutting down...")
                self.stop()
                break
            except Exception as e:
                logger.error(f"Error in main loop: {str(e)}")
                logger.error(traceback.format_exc())
                logger.info(f"Retrying in {check_interval} seconds...")
                time.sleep(check_interval)
    
    def stop(self):
        """Stop the agent"""
        logger.info("🛑 Stopping agent...")
        self.running = False
        # Final sync to cloud
        if self.portfolio:
            self.save_to_cloud()
        logger.info("✅ Agent stopped")


def main():
    """Entry point for the service"""
    # Load environment variables
    load_dotenv()
    
    # Get portfolio name from environment or command line
    import sys
    if len(sys.argv) > 1:
        portfolio_name = sys.argv[1]
    else:
        portfolio_name = os.getenv('PORTFOLIO_NAME', 'default')
    
    logger.info(f"Portfolio: {portfolio_name}")
    
    # Create and run agent
    agent = CloudTradingAgent(portfolio_name)
    agent.run()


if __name__ == "__main__":
    main()
