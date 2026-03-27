"""
Google Sheets integration for paper trading portfolio
Syncs portfolio data to/from Google Sheets for cloud persistence
"""

import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import datetime as dt
import json
import os
from typing import Optional, Dict, List


class SheetsPortfolioSync:
    """Sync paper trading portfolio with Google Sheets"""
    
    def __init__(self, credentials_path: str, spreadsheet_name: str = "Paper Trading Portfolio"):
        """
        Initialize Google Sheets sync
        
        Args:
            credentials_path: Path to Google service account JSON credentials
            spreadsheet_name: Name of the Google Sheet (will be created if doesn't exist)
        """
        self.credentials_path = credentials_path
        self.spreadsheet_name = spreadsheet_name
        self.client = None
        self.spreadsheet = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Sheets API"""
        try:
            # Define the scope
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Authenticate using service account
            creds = Credentials.from_service_account_file(
                self.credentials_path,
                scopes=scope
            )
            
            self.client = gspread.authorize(creds)
            print("✓ Google Sheets authentication successful")
            
        except FileNotFoundError:
            raise Exception(f"Credentials file not found: {self.credentials_path}")
        except Exception as e:
            raise Exception(f"Authentication failed: {str(e)}")
    
    def _get_or_create_spreadsheet(self):
        """Get existing spreadsheet or create new one"""
        try:
            # Try to open existing spreadsheet
            self.spreadsheet = self.client.open(self.spreadsheet_name)
            print(f"✓ Opened existing spreadsheet: {self.spreadsheet_name}")
        except gspread.exceptions.SpreadsheetNotFound:
            # Create new spreadsheet
            self.spreadsheet = self.client.create(self.spreadsheet_name)
            print(f"✓ Created new spreadsheet: {self.spreadsheet_name}")
            
            # Initialize worksheets
            self._initialize_worksheets()
    
    def _initialize_worksheets(self):
        """Initialize worksheet structure for new spreadsheet"""
        # Create worksheets for different data types
        worksheet_configs = [
            ("Portfolio", ["Key", "Value"]),
            ("Positions", ["Ticker", "Type", "Strike", "Expiration", "Quantity", 
                          "Entry Price", "Entry Date", "Exit Price", "Exit Date", "Status"]),
            ("Trade History", ["Date", "Ticker", "Action", "Type", "Strike", 
                              "Quantity", "Price", "Cost", "P&L"]),
            ("Config", ["Key", "Value"])
        ]
        
        # Remove default sheet if it exists
        try:
            default_sheet = self.spreadsheet.sheet1
            if default_sheet.title == "Sheet1":
                self.spreadsheet.del_worksheet(default_sheet)
        except:
            pass
        
        # Create worksheets
        for title, headers in worksheet_configs:
            try:
                ws = self.spreadsheet.add_worksheet(title=title, rows=1000, cols=20)
                ws.append_row(headers)
                ws.format('1', {'textFormat': {'bold': True}})
                print(f"  Created worksheet: {title}")
            except Exception as e:
                print(f"  Warning: Could not create {title}: {str(e)}")
    
    def save_portfolio(self, portfolio):
        """
        Save portfolio to Google Sheets
        
        Args:
            portfolio: PaperTradingPortfolio instance
        """
        self._get_or_create_spreadsheet()
        
        try:
            # Save portfolio summary
            self._save_portfolio_summary(portfolio)
            
            # Save positions
            self._save_positions(portfolio)
            
            # Save trade history
            self._save_trade_history(portfolio)
            
            print(f"✓ Portfolio saved to Google Sheets: {self.spreadsheet.url}")
            return True, self.spreadsheet.url
            
        except Exception as e:
            print(f"✗ Error saving to Google Sheets: {str(e)}")
            return False, str(e)
    
    def _save_portfolio_summary(self, portfolio):
        """Save portfolio summary data"""
        ws = self.spreadsheet.worksheet("Portfolio")
        
        stats = portfolio.get_statistics()
        portfolio_value = portfolio.get_portfolio_value()
        
        data = [
            ["Key", "Value"],
            ["Last Updated", dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ["Starting Cash", portfolio.starting_cash],
            ["Current Cash", portfolio.cash],
            ["Portfolio Value", portfolio_value],
            ["Total P&L", portfolio_value - portfolio.starting_cash],
            ["Total P&L %", ((portfolio_value - portfolio.starting_cash) / portfolio.starting_cash * 100)],
            ["Open Positions", len(portfolio.get_open_positions())],
            ["Max Positions", portfolio.max_positions],
            ["Max Position Size", portfolio.max_position_size],
            ["Total Trades", stats['total_trades']],
            ["Winning Trades", stats['winning_trades']],
            ["Losing Trades", stats['losing_trades']],
            ["Win Rate %", stats['win_rate']],
            ["Avg P&L", stats['avg_pnl']],
            ["Best Trade", stats['best_trade']],
            ["Worst Trade", stats['worst_trade']]
        ]
        
        ws.clear()
        ws.update('A1', data)
        ws.format('A1:B1', {'textFormat': {'bold': True}})
    
    def _save_positions(self, portfolio):
        """Save all positions (open and closed)"""
        ws = self.spreadsheet.worksheet("Positions")
        
        headers = ["Ticker", "Type", "Strike", "Expiration", "Quantity", 
                   "Entry Price", "Entry Date", "Exit Price", "Exit Date", "Status", "P&L"]
        
        rows = [headers]
        
        # Add all positions (open and closed)
        all_positions = portfolio.positions
        
        for pos in all_positions:
            # Convert timestamps to readable dates
            if isinstance(pos.expiration, (int, float)):
                exp_date = dt.datetime.fromtimestamp(pos.expiration).strftime('%Y-%m-%d')
            else:
                exp_date = pos.expiration.strftime('%Y-%m-%d')
            
            if isinstance(pos.entry_date, (int, float)):
                entry_date = dt.datetime.fromtimestamp(pos.entry_date).strftime('%Y-%m-%d')
            else:
                entry_date = pos.entry_date.strftime('%Y-%m-%d')
            
            exit_date = ""
            if pos.exit_date:
                if isinstance(pos.exit_date, (int, float)):
                    exit_date = dt.datetime.fromtimestamp(pos.exit_date).strftime('%Y-%m-%d')
                else:
                    exit_date = pos.exit_date.strftime('%Y-%m-%d')
            
            pnl = pos.get_pnl() if pos.status == 'closed' else 0
            
            rows.append([
                pos.ticker,
                pos.option_type,
                pos.strike,
                exp_date,
                pos.quantity,
                pos.entry_price,
                entry_date,
                pos.exit_price if pos.exit_price else "",
                exit_date,
                pos.status,
                pnl
            ])
        
        ws.clear()
        ws.update('A1', rows)
        ws.format('A1:K1', {'textFormat': {'bold': True}})
    
    def _save_trade_history(self, portfolio):
        """Save trade history"""
        ws = self.spreadsheet.worksheet("Trade History")
        
        headers = ["Date", "Ticker", "Action", "Type", "Strike", 
                   "Quantity", "Price", "Cost", "P&L"]
        
        rows = [headers]
        
        for trade in portfolio.trade_history:
            date_str = trade['date'].strftime('%Y-%m-%d %H:%M:%S') if isinstance(trade['date'], dt.datetime) else trade['date']
            
            rows.append([
                date_str,
                trade.get('ticker', ''),
                trade.get('action', ''),
                trade.get('option_type', ''),
                trade.get('strike', ''),
                trade.get('quantity', ''),
                trade.get('price', ''),
                trade.get('cost', ''),
                trade.get('pnl', '')
            ])
        
        ws.clear()
        ws.update('A1', rows)
        ws.format('A1:I1', {'textFormat': {'bold': True}})
    
    def load_portfolio(self):
        """
        Load portfolio data from Google Sheets
        
        Returns:
            dict: Portfolio data that can be used to reconstruct PaperTradingPortfolio
        """
        try:
            self._get_or_create_spreadsheet()
            
            # Load portfolio summary
            portfolio_data = self._load_portfolio_summary()
            
            # Load positions
            positions_data = self._load_positions()
            
            # Load trade history
            trade_history = self._load_trade_history()
            
            return {
                'portfolio': portfolio_data,
                'positions': positions_data,
                'trade_history': trade_history
            }
            
        except Exception as e:
            print(f"✗ Error loading from Google Sheets: {str(e)}")
            return None
    
    def _load_portfolio_summary(self):
        """Load portfolio summary data"""
        ws = self.spreadsheet.worksheet("Portfolio")
        data = ws.get_all_records()
        
        portfolio_dict = {}
        for row in data:
            portfolio_dict[row['Key']] = row['Value']
        
        return portfolio_dict
    
    def _load_positions(self):
        """Load positions data"""
        ws = self.spreadsheet.worksheet("Positions")
        return ws.get_all_records()
    
    def _load_trade_history(self):
        """Load trade history"""
        ws = self.spreadsheet.worksheet("Trade History")
        return ws.get_all_records()
    
    def get_spreadsheet_url(self):
        """Get the URL of the spreadsheet"""
        if self.spreadsheet:
            return self.spreadsheet.url
        return None


def setup_google_sheets_sync(credentials_path: Optional[str] = None) -> Optional[SheetsPortfolioSync]:
    """
    Setup Google Sheets sync with automatic credential detection
    
    Args:
        credentials_path: Optional path to credentials file
        
    Returns:
        SheetsPortfolioSync instance or None if setup fails
    """
    # Default credential locations
    default_paths = [
        os.path.join(os.path.dirname(__file__), '..', 'google_credentials.json'),
        os.path.join(os.path.expanduser('~'), '.algo_trader', 'google_credentials.json'),
        credentials_path
    ]
    
    for path in default_paths:
        if path and os.path.exists(path):
            try:
                sync = SheetsPortfolioSync(path)
                return sync
            except Exception as e:
                print(f"Warning: Could not setup Google Sheets sync: {str(e)}")
                continue
    
    return None
