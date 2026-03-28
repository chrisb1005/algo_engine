"""
Paper Trading Engine - Simulated options trading with virtual money
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

import pandas as pd
import datetime as dt
import json
import os


class Position:
    """Represents an open options position"""
    
    def __init__(self, ticker, option_type, strike, expiration, quantity, entry_price, entry_date):
        self.ticker = ticker
        self.option_type = option_type  # 'call' or 'put'
        self.strike = strike
        self.expiration = expiration
        self.quantity = quantity
        self.entry_price = entry_price
        self.entry_date = entry_date
        self.exit_price = None
        self.exit_date = None
        self.status = 'open'  # 'open' or 'closed'
        
    def close(self, exit_price, exit_date):
        """Close the position"""
        self.exit_price = exit_price
        self.exit_date = exit_date
        self.status = 'closed'
        
    def get_pnl(self, current_price=None):
        """Calculate P&L for the position"""
        if self.status == 'closed':
            price_diff = self.exit_price - self.entry_price
        else:
            if current_price is None:
                return 0
            price_diff = current_price - self.entry_price
        
        return price_diff * self.quantity * 100  # Options are 100 shares per contract
    
    def get_pnl_percent(self, current_price=None):
        """Calculate P&L percentage"""
        if self.entry_price == 0:
            return 0
        
        if self.status == 'closed':
            return ((self.exit_price - self.entry_price) / self.entry_price) * 100
        else:
            if current_price is None:
                return 0
            return ((current_price - self.entry_price) / self.entry_price) * 100
    
    def to_dict(self):
        """Convert to dictionary for serialization"""
        return {
            'ticker': self.ticker,
            'option_type': self.option_type,
            'strike': self.strike,
            'expiration': self.expiration.isoformat() if isinstance(self.expiration, dt.datetime) else self.expiration,
            'quantity': self.quantity,
            'entry_price': self.entry_price,
            'entry_date': self.entry_date.isoformat() if isinstance(self.entry_date, dt.datetime) else self.entry_date,
            'exit_price': self.exit_price,
            'exit_date': self.exit_date.isoformat() if isinstance(self.exit_date, dt.datetime) and self.exit_date else self.exit_date,
            'status': self.status
        }
    
    @staticmethod
    def from_dict(data):
        """Create Position from dictionary"""
        pos = Position(
            ticker=data['ticker'],
            option_type=data['option_type'],
            strike=data['strike'],
            expiration=dt.datetime.fromisoformat(data['expiration']) if isinstance(data['expiration'], str) else data['expiration'],
            quantity=data['quantity'],
            entry_price=data['entry_price'],
            entry_date=dt.datetime.fromisoformat(data['entry_date']) if isinstance(data['entry_date'], str) else data['entry_date']
        )
        pos.exit_price = data.get('exit_price')
        pos.exit_date = dt.datetime.fromisoformat(data['exit_date']) if data.get('exit_date') and isinstance(data['exit_date'], str) else data.get('exit_date')
        pos.status = data.get('status', 'open')
        return pos


class PaperTradingPortfolio:
    """Paper trading portfolio with virtual money"""
    
    def __init__(self, starting_cash=10000, max_position_size=0.05, max_positions=10):
        self.starting_cash = starting_cash
        self.cash = starting_cash
        self.max_position_size = max_position_size  # Max % of portfolio per position
        self.max_positions = max_positions  # Max number of open positions
        self.positions = []  # All positions (open + closed)
        self.trade_history = []
        
    def get_open_positions(self):
        """Get all open positions"""
        return [p for p in self.positions if p.status == 'open']
    
    def get_closed_positions(self):
        """Get all closed positions"""
        return [p for p in self.positions if p.status == 'closed']
    
    def get_portfolio_value(self, current_prices=None):
        """Calculate total portfolio value"""
        total = self.cash
        
        if current_prices:
            for pos in self.get_open_positions():
                key = f"{pos.ticker}_{pos.option_type}_{pos.strike}"
                if key in current_prices:
                    total += (current_prices[key] * pos.quantity * 100)
        
        return total
    
    def get_total_pnl(self):
        """Get total realized P&L from closed positions"""
        return sum(p.get_pnl() for p in self.get_closed_positions())
    
    def get_unrealized_pnl(self, current_prices=None):
        """Get unrealized P&L from open positions"""
        if not current_prices:
            return 0
        
        total = 0
        for pos in self.get_open_positions():
            key = f"{pos.ticker}_{pos.option_type}_{pos.strike}"
            if key in current_prices:
                total += pos.get_pnl(current_prices[key])
        
        return total
    
    def can_open_position(self, cost):
        """Check if we can afford to open a position"""
        # Check cash
        if cost > self.cash:
            return False, "Insufficient cash"
        
        # Check max positions
        if len(self.get_open_positions()) >= self.max_positions:
            return False, f"Max positions ({self.max_positions}) reached"
        
        # Check position size limit
        portfolio_value = self.get_portfolio_value()
        if cost > portfolio_value * self.max_position_size:
            return False, f"Position size exceeds {self.max_position_size*100}% limit"
        
        return True, "OK"
    
    def open_position(self, ticker, option_type, strike, expiration, quantity, price):
        """Open a new position"""
        cost = price * quantity * 100
        
        can_open, reason = self.can_open_position(cost)
        if not can_open:
            return False, reason
        
        # Create position
        position = Position(
            ticker=ticker,
            option_type=option_type,
            strike=strike,
            expiration=expiration,
            quantity=quantity,
            entry_price=price,
            entry_date=dt.datetime.now()
        )
        
        # Deduct cash
        self.cash -= cost
        
        # Add to positions
        self.positions.append(position)
        
        # Log trade
        self.trade_history.append({
            'date': dt.datetime.now(),
            'action': 'BUY',
            'ticker': ticker,
            'option_type': option_type,
            'strike': strike,
            'quantity': quantity,
            'price': price,
            'cost': cost
        })
        
        return True, position
    
    def close_position(self, position, exit_price):
        """Close an existing position"""
        if position.status == 'closed':
            return False, "Position already closed"
        
        # Close position
        position.close(exit_price, dt.datetime.now())
        
        # Add cash back
        proceeds = exit_price * position.quantity * 100
        self.cash += proceeds
        
        # Log trade
        self.trade_history.append({
            'date': dt.datetime.now(),
            'action': 'SELL',
            'ticker': position.ticker,
            'option_type': position.option_type,
            'strike': position.strike,
            'quantity': position.quantity,
            'price': exit_price,
            'proceeds': proceeds,
            'pnl': position.get_pnl()
        })
        
        return True, f"Position closed. P&L: ${position.get_pnl():.2f}"
    
    def close_all_positions(self, current_prices):
        """Close all open positions"""
        closed = 0
        for pos in self.get_open_positions():
            key = f"{pos.ticker}_{pos.option_type}_{pos.strike}"
            if key in current_prices:
                self.close_position(pos, current_prices[key])
                closed += 1
        
        return closed
    
    def get_statistics(self):
        """Get portfolio statistics"""
        closed = self.get_closed_positions()
        
        if not closed:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'avg_pnl': 0,
                'best_trade': 0,
                'worst_trade': 0
            }
        
        pnls = [p.get_pnl() for p in closed]
        winning = [p for p in pnls if p > 0]
        losing = [p for p in pnls if p < 0]
        
        return {
            'total_trades': len(closed),
            'winning_trades': len(winning),
            'losing_trades': len(losing),
            'win_rate': (len(winning) / len(closed) * 100) if closed else 0,
            'total_pnl': sum(pnls),
            'avg_pnl': sum(pnls) / len(pnls) if pnls else 0,
            'best_trade': max(pnls) if pnls else 0,
            'worst_trade': min(pnls) if pnls else 0
        }
    
    def save_to_file(self, filepath):
        """Save portfolio state to JSON file"""
        data = {
            'starting_cash': self.starting_cash,
            'cash': self.cash,
            'max_position_size': self.max_position_size,
            'max_positions': self.max_positions,
            'positions': [p.to_dict() for p in self.positions],
            'trade_history': [
                {**t, 'date': t['date'].isoformat() if isinstance(t['date'], dt.datetime) else t['date']}
                for t in self.trade_history
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def save_to_supabase(self, portfolio_name: str = "default", agent_config: dict = None):
        """
        Save portfolio to Supabase
        
        Args:
            portfolio_name: Unique name for this portfolio
            agent_config: Optional dict with agent configuration (tickers, check_interval, position_size)
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            from core.supabase_sync import setup_supabase_sync
            
            sync = setup_supabase_sync()
            if sync is None:
                return False, "Supabase sync not configured. Set SUPABASE_URL and SUPABASE_KEY environment variables."
            
            success, result = sync.save_portfolio(self, portfolio_name, agent_config)
            return success, result
            
        except Exception as e:
            return False, f"Error syncing to Supabase: {str(e)}"
    
    @staticmethod
    def load_from_supabase(portfolio_name: str = "default"):
        """
        Load portfolio from Supabase
        
        Args:
            portfolio_name: Name of the portfolio to load
            
        Returns:
            PaperTradingPortfolio instance or None
        """
        try:
            from core.supabase_sync import setup_supabase_sync
            from core.paper_trader import Position
            
            sync = setup_supabase_sync()
            if sync is None:
                return None
            
            data = sync.load_portfolio(portfolio_name)
            if not data:
                return None
            
            portfolio_data = data['portfolio']
            
            portfolio = PaperTradingPortfolio(
                starting_cash=portfolio_data['starting_cash'],
                max_position_size=portfolio_data['max_position_size'],
                max_positions=portfolio_data['max_positions']
            )
            portfolio.cash = portfolio_data['current_cash']
            
            # Restore positions
            for pos_data in data['positions']:
                # Parse datetimes and strip timezone info for consistency
                expiration = dt.datetime.fromisoformat(pos_data['expiration'])
                if hasattr(expiration, 'tzinfo') and expiration.tzinfo is not None:
                    expiration = expiration.replace(tzinfo=None)
                
                entry_date = dt.datetime.fromisoformat(pos_data['entry_date'])
                if hasattr(entry_date, 'tzinfo') and entry_date.tzinfo is not None:
                    entry_date = entry_date.replace(tzinfo=None)
                
                pos = Position(
                    ticker=pos_data['ticker'],
                    option_type=pos_data['option_type'],
                    strike=pos_data['strike'],
                    expiration=expiration,
                    quantity=pos_data['quantity'],
                    entry_price=pos_data['entry_price'],
                    entry_date=entry_date
                )
                if pos_data['exit_price']:
                    pos.exit_price = pos_data['exit_price']
                if pos_data['exit_date']:
                    exit_date = dt.datetime.fromisoformat(pos_data['exit_date'])
                    if hasattr(exit_date, 'tzinfo') and exit_date.tzinfo is not None:
                        exit_date = exit_date.replace(tzinfo=None)
                    pos.exit_date = exit_date
                pos.status = pos_data['status']
                portfolio.positions.append(pos)
            
            # Restore trade history
            for trade_data in data['trades']:
                trade_date = dt.datetime.fromisoformat(trade_data['date'])
                if hasattr(trade_date, 'tzinfo') and trade_date.tzinfo is not None:
                    trade_date = trade_date.replace(tzinfo=None)
                
                trade = {
                    'date': trade_date,
                    'ticker': trade_data['ticker'],
                    'action': trade_data['action'],
                    'option_type': trade_data['option_type'],
                    'strike': trade_data['strike'],
                    'quantity': trade_data['quantity'],
                    'price': trade_data['price'],
                    'cost': trade_data['cost'],
                    'pnl': trade_data['pnl']
                }
                portfolio.trade_history.append(trade)
            
            return portfolio
            
        except Exception as e:
            print(f"Error loading from Supabase: {str(e)}")
            return None
    
    def save_to_google_sheets(self, credentials_path=None):
        """
        Save portfolio to Google Sheets (deprecated - use save_to_supabase)
        
        Args:
            credentials_path: Path to Google credentials JSON file
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            from core.sheets_sync import setup_google_sheets_sync
            
            sync = setup_google_sheets_sync(credentials_path)
            if sync is None:
                return False, "Google Sheets sync not configured"
            
            success, result = sync.save_portfolio(self)
            return success, result
            
        except Exception as e:
            return False, f"Error syncing to Google Sheets: {str(e)}"
    
    @staticmethod
    def load_from_file(filepath):
        """Load portfolio from JSON file"""
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        portfolio = PaperTradingPortfolio(
            starting_cash=data['starting_cash'],
            max_position_size=data['max_position_size'],
            max_positions=data['max_positions']
        )
        portfolio.cash = data['cash']
        portfolio.positions = [Position.from_dict(p) for p in data['positions']]
        portfolio.trade_history = [
            {**t, 'date': dt.datetime.fromisoformat(t['date']) if isinstance(t['date'], str) else t['date']}
            for t in data['trade_history']
        ]
        
        return portfolio
