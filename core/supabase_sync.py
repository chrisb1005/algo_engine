"""
Supabase integration for paper trading portfolio
Syncs portfolio data to/from Supabase (free PostgreSQL backend)
"""

import os
from supabase import create_client, Client
import datetime as dt
import json
from typing import Optional, Dict, List


class SupabasePortfolioSync:
    """Sync paper trading portfolio with Supabase"""
    
    def __init__(self, url: str = None, key: str = None):
        """
        Initialize Supabase sync
        
        Args:
            url: Supabase project URL (or set SUPABASE_URL env var)
            key: Supabase API key (or set SUPABASE_KEY env var)
        """
        self.url = url or os.getenv('SUPABASE_URL')
        self.key = key or os.getenv('SUPABASE_KEY')
        
        if not self.url or not self.key:
            raise ValueError("Supabase URL and KEY required. Set SUPABASE_URL and SUPABASE_KEY environment variables.")
        
        self.client: Client = create_client(self.url, self.key)
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Ensure required tables exist (will be created via Supabase dashboard)"""
        # Tables are created via Supabase SQL editor or migrations
        # This is just a check/documentation of expected schema
        self.tables = {
            'portfolios': ['id', 'created_at', 'starting_cash', 'current_cash', 'max_position_size', 'max_positions'],
            'positions': ['id', 'portfolio_id', 'ticker', 'option_type', 'strike', 'expiration', 
                         'quantity', 'entry_price', 'entry_date', 'exit_price', 'exit_date', 'status'],
            'trades': ['id', 'portfolio_id', 'date', 'ticker', 'action', 'option_type', 
                      'strike', 'quantity', 'price', 'cost', 'pnl']
        }
    
    def save_portfolio(self, portfolio, portfolio_name: str = "default", agent_config: dict = None):
        """
        Save portfolio to Supabase
        
        Args:
            portfolio: PaperTradingPortfolio instance
            portfolio_name: Unique name for this portfolio
            agent_config: Optional dict with tickers, check_interval, position_size
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Check if portfolio exists
            existing = self.client.table('portfolios').select('id').eq('name', portfolio_name).execute()
            
            portfolio_data = {
                'name': portfolio_name,
                'starting_cash': portfolio.starting_cash,
                'current_cash': portfolio.cash,
                'max_position_size': portfolio.max_position_size,
                'max_positions': portfolio.max_positions,
                'updated_at': dt.datetime.now().isoformat()
            }
            
            # Add agent config if provided
            if agent_config:
                import json
                portfolio_data['agent_config'] = json.dumps(agent_config)
            
            if existing.data:
                # Update existing portfolio
                portfolio_id = existing.data[0]['id']
                self.client.table('portfolios').update(portfolio_data).eq('id', portfolio_id).execute()
            else:
                # Create new portfolio
                result = self.client.table('portfolios').insert(portfolio_data).execute()
                portfolio_id = result.data[0]['id']
            
            # Delete old positions and trades for this portfolio
            self.client.table('positions').delete().eq('portfolio_id', portfolio_id).execute()
            self.client.table('trades').delete().eq('portfolio_id', portfolio_id).execute()
            
            # Save positions
            if portfolio.positions:
                positions_data = []
                for pos in portfolio.positions:
                    # Convert timestamps to ISO format
                    exp_date = dt.datetime.fromtimestamp(pos.expiration).isoformat() if isinstance(pos.expiration, (int, float)) else pos.expiration.isoformat()
                    entry_date = dt.datetime.fromtimestamp(pos.entry_date).isoformat() if isinstance(pos.entry_date, (int, float)) else pos.entry_date.isoformat()
                    exit_date = None
                    if pos.exit_date:
                        exit_date = dt.datetime.fromtimestamp(pos.exit_date).isoformat() if isinstance(pos.exit_date, (int, float)) else pos.exit_date.isoformat()
                    
                    positions_data.append({
                        'portfolio_id': portfolio_id,
                        'ticker': pos.ticker,
                        'option_type': pos.option_type,
                        'strike': float(pos.strike),
                        'expiration': exp_date,
                        'quantity': pos.quantity,
                        'entry_price': float(pos.entry_price),
                        'entry_date': entry_date,
                        'exit_price': float(pos.exit_price) if pos.exit_price else None,
                        'exit_date': exit_date,
                        'status': pos.status
                    })
                
                self.client.table('positions').insert(positions_data).execute()
            
            # Save trade history
            if portfolio.trade_history:
                trades_data = []
                for trade in portfolio.trade_history:
                    trade_date = trade['date'].isoformat() if isinstance(trade['date'], dt.datetime) else trade['date']
                    
                    trades_data.append({
                        'portfolio_id': portfolio_id,
                        'date': trade_date,
                        'ticker': trade.get('ticker', ''),
                        'action': trade.get('action', ''),
                        'option_type': trade.get('option_type', ''),
                        'strike': float(trade.get('strike', 0)) if trade.get('strike') else None,
                        'quantity': trade.get('quantity', 0),
                        'price': float(trade.get('price', 0)) if trade.get('price') else None,
                        'cost': float(trade.get('cost', 0)) if trade.get('cost') else None,
                        'pnl': float(trade.get('pnl', 0)) if trade.get('pnl') else None
                    })
                
                self.client.table('trades').insert(trades_data).execute()
            
            return True, f"Portfolio synced to Supabase (portfolio_id: {portfolio_id})"
            
        except Exception as e:
            return False, f"Error syncing to Supabase: {str(e)}"
    
    def load_portfolio(self, portfolio_name: str = "default"):
        """
        Load portfolio from Supabase
        
        Args:
            portfolio_name: Name of the portfolio to load
            
        Returns:
            dict: Portfolio data or None if not found
        """
        try:
            # Get portfolio
            portfolio_result = self.client.table('portfolios').select('*').eq('name', portfolio_name).execute()
            
            if not portfolio_result.data:
                return None
            
            portfolio_data = portfolio_result.data[0]
            portfolio_id = portfolio_data['id']
            
            # Get positions
            positions_result = self.client.table('positions').select('*').eq('portfolio_id', portfolio_id).execute()
            
            # Get trades
            trades_result = self.client.table('trades').select('*').eq('portfolio_id', portfolio_id).execute()
            
            return {
                'portfolio': portfolio_data,
                'positions': positions_result.data,
                'trades': trades_result.data
            }
            
        except Exception as e:
            print(f"Error loading from Supabase: {str(e)}")
            return None
    
    def get_portfolio_stats(self, portfolio_name: str = "default"):
        """Get portfolio statistics from Supabase"""
        try:
            # Get portfolio
            portfolio_result = self.client.table('portfolios').select('*').eq('name', portfolio_name).execute()
            
            if not portfolio_result.data:
                return None
            
            portfolio_data = portfolio_result.data[0]
            portfolio_id = portfolio_data['id']
            
            # Get positions count
            positions_result = self.client.table('positions').select('id', count='exact').eq('portfolio_id', portfolio_id).eq('status', 'open').execute()
            
            # Get trades count
            trades_result = self.client.table('trades').select('id', count='exact').eq('portfolio_id', portfolio_id).execute()
            
            return {
                'starting_cash': portfolio_data['starting_cash'],
                'current_cash': portfolio_data['current_cash'],
                'open_positions': positions_result.count,
                'total_trades': trades_result.count,
                'last_updated': portfolio_data.get('updated_at')
            }
            
        except Exception as e:
            print(f"Error getting stats: {str(e)}")
            return None


def setup_supabase_sync(url: str = None, key: str = None) -> Optional[SupabasePortfolioSync]:
    """
    Setup Supabase sync with automatic environment variable detection
    
    Args:
        url: Optional Supabase URL
        key: Optional Supabase key
        
    Returns:
        SupabasePortfolioSync instance or None if setup fails
    """
    try:
        # Try to load from .env file
        from dotenv import load_dotenv
        load_dotenv()
        
        sync = SupabasePortfolioSync(url, key)
        return sync
    except Exception as e:
        print(f"Warning: Could not setup Supabase sync: {str(e)}")
        return None
