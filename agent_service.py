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
            
            # Load agent configuration
            self.agent_config = data.get('agent_config', {})
            if not self.agent_config:
                raise Exception("No agent configuration found in portfolio")
            
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
            
            # Import trading logic
            from core.strategies import BullCallSpreadStrategy
            from core.signals import OptionsSignalGenerator
            from core.data import get_stock_data, get_near_money_options
            
            strategy = BullCallSpreadStrategy()
            signal_gen = OptionsSignalGenerator(strategy)
            
            for ticker in tickers:
                try:
                    logger.info(f"Analyzing {ticker}...")
                    
                    # Get current stock data
                    stock_data = get_stock_data(ticker, period='3mo')
                    if stock_data is None or stock_data.empty:
                        logger.warning(f"No data for {ticker}")
                        continue
                    
                    # Generate signal
                    signal = signal_gen.generate_signal(stock_data)
                    
                    if signal and signal.signal_type in ['BUY', 'STRONG_BUY']:
                        logger.info(f"🎯 {signal.signal_type} signal for {ticker} (confidence: {signal.confidence:.1%})")
                        
                        # Get options chain
                        options = get_near_money_options(ticker)
                        if options is None or options.empty:
                            logger.warning(f"No options data for {ticker}")
                            continue
                        
                        # Check if we already have an open position
                        has_position = any(
                            p['ticker'] == ticker and p['status'] == 'open' 
                            for p in self.portfolio.positions
                        )
                        
                        if has_position:
                            logger.info(f"Already have open position in {ticker}, skipping")
                            continue
                        
                        # Check if we can open a new position
                        if len([p for p in self.portfolio.positions if p['status'] == 'open']) >= self.portfolio.max_positions:
                            logger.info(f"Max positions reached ({self.portfolio.max_positions}), skipping")
                            continue
                        
                        # Find suitable bull call spread
                        calls = options[options['type'] == 'call'].copy()
                        if len(calls) < 2:
                            continue
                        
                        # Get next week's expiration (at least 3 days away)
                        from core.execution import get_next_week_expiration
                        expiration = get_next_week_expiration(calls)
                        
                        # Filter by expiration
                        calls = calls[calls['expiration'] == expiration]
                        if len(calls) < 2:
                            continue
                        
                        # Sort by strike
                        calls = calls.sort_values('strike')
                        
                        # Find ITM and OTM strikes
                        current_price = stock_data['Close'].iloc[-1]
                        itm_calls = calls[calls['strike'] < current_price]
                        otm_calls = calls[calls['strike'] > current_price]
                        
                        if len(itm_calls) > 0 and len(otm_calls) > 0:
                            # Select strikes
                            long_strike = itm_calls.iloc[-1]['strike']  # Closest ITM
                            short_strike = otm_calls.iloc[0]['strike']  # Closest OTM
                            
                            long_option = itm_calls[itm_calls['strike'] == long_strike].iloc[0]
                            short_option = otm_calls[otm_calls['strike'] == short_strike].iloc[0]
                            
                            # Calculate spread cost
                            spread_cost = (long_option['lastPrice'] - short_option['lastPrice']) * 100 * position_size
                            
                            # Check if we have enough cash
                            if spread_cost > self.portfolio.current_cash:
                                logger.info(f"Insufficient cash for {ticker} (need ${spread_cost:,.2f})")
                                continue
                            
                            # Execute the spread
                            logger.info(f"🚀 Opening bull call spread on {ticker}:")
                            logger.info(f"   Long {long_strike}C @ ${long_option['lastPrice']:.2f}")
                            logger.info(f"   Short {short_strike}C @ ${short_option['lastPrice']:.2f}")
                            logger.info(f"   Net cost: ${spread_cost:,.2f}")
                            
                            # Buy long call
                            self.portfolio.open_position(
                                ticker=ticker,
                                option_type='call',
                                strike=long_strike,
                                expiration=expiration,
                                quantity=position_size,
                                entry_price=long_option['lastPrice']
                            )
                            
                            # Sell short call
                            self.portfolio.open_position(
                                ticker=ticker,
                                option_type='call',
                                strike=short_strike,
                                expiration=expiration,
                                quantity=-position_size,  # Negative for short
                                entry_price=short_option['lastPrice']
                            )
                            
                            logger.info(f"✅ Position opened successfully")
                            
                            # Save to cloud after trade
                            self.save_to_cloud()
                    
                    # Check for exit signals on open positions
                    open_positions = [p for p in self.portfolio.positions if p['ticker'] == ticker and p['status'] == 'open']
                    
                    for pos in open_positions:
                        # Get current option price
                        options = get_near_money_options(ticker)
                        if options is None or options.empty:
                            continue
                        
                        matching_option = options[
                            (options['type'] == pos['option_type']) &
                            (options['strike'] == pos['strike']) &
                            (options['expiration'] == pos['expiration'])
                        ]
                        
                        if not matching_option.empty:
                            current_price = matching_option.iloc[0]['lastPrice']
                            entry_price = pos['entry_price']
                            
                            # Calculate P&L percentage
                            if pos['quantity'] > 0:  # Long position
                                pnl_pct = (current_price - entry_price) / entry_price if entry_price > 0 else 0
                            else:  # Short position
                                pnl_pct = (entry_price - current_price) / entry_price if entry_price > 0 else 0
                            
                            # Exit conditions: 50% profit or 30% loss
                            should_exit = False
                            exit_reason = ""
                            
                            if pnl_pct >= 0.50:
                                should_exit = True
                                exit_reason = "50% profit target"
                            elif pnl_pct <= -0.30:
                                should_exit = True
                                exit_reason = "30% stop loss"
                            
                            # Check expiration (close if within 1 day)
                            days_to_expiry = (pos['expiration'] - datetime.now()).days
                            if days_to_expiry <= 1:
                                should_exit = True
                                exit_reason = "expiration approaching"
                            
                            if should_exit:
                                logger.info(f"🔔 Closing position on {ticker} {pos['strike']}{pos['option_type'][0].upper()} - {exit_reason}")
                                logger.info(f"   P&L: {pnl_pct:.1%}")
                                
                                exit_success = self.portfolio.close_position(
                                    ticker=ticker,
                                    strike=pos['strike'],
                                    option_type=pos['option_type'],
                                    expiration=pos['expiration'],
                                    exit_price=current_price
                                )
                                
                                if exit_success:
                                    logger.info(f"✅ Position closed")
                                    self.save_to_cloud()
                
                except Exception as e:
                    logger.error(f"Error processing {ticker}: {str(e)}")
                    logger.error(traceback.format_exc())
                    continue
            
            logger.info(f"📊 Portfolio value: ${self.portfolio.get_portfolio_value():,.2f}")
            
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
