"""
Automated Trading Agent - Executes trades based on algo_engine signals
"""

import sys
if sys.platform == "win32":
    try:
        import io
        if sys.stdout.encoding != 'utf-8':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

from core.data import load_history, get_current_price
from core.indicators import compute_indicators
from core.signals import generate_signal
from core.strategies import decide_action
from core.contracts import load_options_chain, find_best_option, get_next_week_expiration
from core.paper_trader import PaperTradingPortfolio
import pandas as pd
import time
import datetime as dt


class AutoTradingAgent:
    """Automated trading agent that follows algo_engine signals"""
    
    def __init__(self, portfolio, tickers, check_interval=300, position_size=1):
        """
        Args:
            portfolio: PaperTradingPortfolio instance
            tickers: List of tickers to monitor
            check_interval: Seconds between signal checks (default 5 min)
            position_size: Number of contracts per position
        """
        self.portfolio = portfolio
        self.tickers = tickers if isinstance(tickers, list) else [tickers]
        self.check_interval = check_interval
        self.position_size = position_size
        self.is_running = False
        self.last_signals = {}  # Track last signal per ticker to avoid duplicates
        self.log = []
        
    def log_message(self, message):
        """Add timestamped log message"""
        timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log.append(log_entry)
        print(log_entry)
        return log_entry
    
    def get_signal_for_ticker(self, ticker):
        """Get algo_engine signal for a ticker"""
        try:
            # Load data
            df = load_history(ticker, days=60)
            if df is None or len(df) < 20:
                return None, "Insufficient data"
            
            # Compute indicators
            df = compute_indicators(df)
            
            # Generate signal
            signal = generate_signal(df)
            
            # Decide action
            action = decide_action(signal)
            
            return action, signal
            
        except Exception as e:
            return None, f"Error: {str(e)}"
    
    def find_option_contract(self, ticker, action):
        """Find appropriate option contract for the action"""
        try:
            # Get current price for reference
            current_price = get_current_price(ticker)
            if not current_price:
                return None
            
            # Get next week expiration
            expiration = get_next_week_expiration(ticker)
            
            # Load options chain
            options_data = load_options_chain(ticker, expiration)
            if options_data is None:
                return None
            
            # Extract calls and puts from the dictionary
            df_calls = options_data.get('calls', pd.DataFrame())
            df_puts = options_data.get('puts', pd.DataFrame())
            
            # Choose contract based on action
            if action in ['BUY_CALL', 'SELL_CALL']:
                if len(df_calls) == 0:
                    return None
                
                # Use find_best_option helper (looks for OTM options with volume for buys)
                criteria = 'otm' if 'BUY' in action else 'volume'
                contract_df = find_best_option(options_data, option_type='call', criteria=criteria)
                
                if contract_df is not None and len(contract_df) > 0:
                    contract = contract_df.iloc[0]
                    return {
                        'ticker': ticker,
                        'option_type': 'call',
                        'strike': contract['strike'],
                        'expiration': expiration,
                        'price': contract['lastPrice'],
                        'volume': contract.get('volume', 0)
                    }
            
            elif action in ['BUY_PUT', 'SELL_PUT']:
                if len(df_puts) == 0:
                    return None
                
                # Use find_best_option helper
                criteria = 'otm' if 'BUY' in action else 'volume'
                contract_df = find_best_option(options_data, option_type='put', criteria=criteria)
                
                if contract_df is not None and len(contract_df) > 0:
                    contract = contract_df.iloc[0]
                    return {
                        'ticker': ticker,
                        'option_type': 'put',
                        'strike': contract['strike'],
                        'expiration': expiration,
                        'price': contract['lastPrice'],
                        'volume': contract.get('volume', 0)
                    }
            
            return None
            
        except Exception as e:
            self.log_message(f"Error finding contract for {ticker}: {str(e)}")
            return None
    
    def execute_signal(self, ticker, action, signal):
        """Execute a trading signal"""
        # Check if this is a new signal (avoid duplicate trades)
        if ticker in self.last_signals:
            if self.last_signals[ticker]['action'] == action:
                return False, "Signal already traded"
        
        # Only trade on BUY signals (for now)
        if action not in ['BUY_CALL', 'BUY_PUT']:
            self.log_message(f"{ticker}: {action} - Not a buy signal, skipping")
            return False, "Not a buy signal"
        
        # Find contract
        self.log_message(f"{ticker}: Finding option contract for {action}...")
        contract = self.find_option_contract(ticker, action)
        
        if not contract:
            self.log_message(f"{ticker}: No suitable contract found")
            return False, "No contract found"
        
        # Check if we can afford it
        cost = contract['price'] * self.position_size * 100
        can_open, reason = self.portfolio.can_open_position(cost)
        
        if not can_open:
            self.log_message(f"{ticker}: Cannot open position - {reason}")
            return False, reason
        
        # Open position
        success, result = self.portfolio.open_position(
            ticker=ticker,
            option_type=contract['option_type'],
            strike=contract['strike'],
            expiration=contract['expiration'],
            quantity=self.position_size,
            price=contract['price']
        )
        
        if success:
            self.log_message(
                f"✅ TRADE EXECUTED - {ticker} {action}\n"
                f"   Strike: ${contract['strike']:.2f}, Price: ${contract['price']:.2f}\n"
                f"   Cost: ${cost:.2f}, Cash Remaining: ${self.portfolio.cash:.2f}"
            )
            
            # Update last signal
            self.last_signals[ticker] = {
                'action': action,
                'signal': signal,
                'timestamp': dt.datetime.now()
            }
            
            return True, result
        else:
            self.log_message(f"{ticker}: Failed to open position - {result}")
            return False, result
    
    def check_exit_conditions(self):
        """Check if any open positions should be closed"""
        open_positions = self.portfolio.get_open_positions()
        
        for pos in open_positions:
            # Simple exit conditions:
            # 1. Expiration approaching (< 2 days)
            # 2. P&L target hit (50% gain or -30% loss)
            
            # Convert expiration to datetime if it's a timestamp
            if isinstance(pos.expiration, (int, float)):
                expiration_dt = dt.datetime.fromtimestamp(pos.expiration)
            else:
                expiration_dt = pos.expiration
            
            days_to_expiry = (expiration_dt - dt.datetime.now()).days
            
            # Get current option price (simplified - would need live data)
            # For now, just check expiration
            if days_to_expiry <= 1:
                # Close position at entry price (simplified)
                self.portfolio.close_position(pos, pos.entry_price)
                self.log_message(f"⚠️ CLOSED {pos.ticker} {pos.option_type} - Near expiration")
    
    def run_cycle(self):
        """Run one trading cycle - check all tickers"""
        self.log_message("=" * 60)
        self.log_message(f"Starting trading cycle - Monitoring {len(self.tickers)} tickers")
        self.log_message(f"Portfolio: ${self.portfolio.get_portfolio_value():.2f} "
                        f"(Cash: ${self.portfolio.cash:.2f}, Positions: {len(self.portfolio.get_open_positions())})")
        
        trades_executed = 0
        
        for ticker in self.tickers:
            try:
                # Get signal
                action, signal = self.get_signal_for_ticker(ticker)
                
                if action is None:
                    self.log_message(f"{ticker}: {signal}")
                    continue
                
                self.log_message(f"{ticker}: Signal = {action}")
                
                # Try to execute
                if action != 'NO_TRADE':
                    success, result = self.execute_signal(ticker, action, signal)
                    if success:
                        trades_executed += 1
                
            except Exception as e:
                self.log_message(f"{ticker}: Error - {str(e)}")
            
            # Small delay between tickers
            time.sleep(0.5)
        
        # Check exit conditions
        self.check_exit_conditions()
        
        self.log_message(f"Cycle complete - {trades_executed} trades executed")
        self.log_message("=" * 60)
        
        return trades_executed
    
    def start(self, max_cycles=None):
        """Start the automated trading agent"""
        self.is_running = True
        self.log_message("🤖 AUTO TRADING AGENT STARTED")
        self.log_message(f"Monitoring tickers: {', '.join(self.tickers)}")
        self.log_message(f"Check interval: {self.check_interval} seconds")
        
        cycle = 0
        
        while self.is_running:
            cycle += 1
            
            if max_cycles and cycle > max_cycles:
                self.log_message(f"Max cycles ({max_cycles}) reached")
                break
            
            try:
                self.run_cycle()
                
                # Wait for next cycle
                if self.is_running:
                    self.log_message(f"Waiting {self.check_interval} seconds until next check...")
                    time.sleep(self.check_interval)
                    
            except KeyboardInterrupt:
                self.log_message("Agent stopped by user")
                break
            except Exception as e:
                self.log_message(f"Error in cycle: {str(e)}")
                time.sleep(60)  # Wait a minute before retrying
        
        self.log_message("🛑 AUTO TRADING AGENT STOPPED")
        return self.portfolio.get_statistics()
    
    def stop(self):
        """Stop the agent"""
        self.is_running = False
