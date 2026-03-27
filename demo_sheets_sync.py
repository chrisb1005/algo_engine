"""
Demo script for Google Sheets integration
Tests saving portfolio to Google Sheets
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.paper_trader import PaperTradingPortfolio
from core.sheets_sync import setup_google_sheets_sync

def demo_sheets_sync():
    """Demo Google Sheets portfolio sync"""
    print("=" * 60)
    print("Google Sheets Portfolio Sync Demo")
    print("=" * 60)
    
    # Check for credentials
    creds_path = "google_credentials.json"
    if not os.path.exists(creds_path):
        print("\n❌ ERROR: google_credentials.json not found!")
        print("\nTo use Google Sheets sync, you need to:")
        print("1. Create a Google Cloud project")
        print("2. Enable Google Sheets API and Google Drive API")
        print("3. Create a service account and download credentials")
        print("4. Save the credentials as 'google_credentials.json' in this folder")
        print("\nSee GOOGLE_SHEETS_SETUP.md for detailed instructions.")
        return
    
    # Create a demo portfolio
    print("\n1. Creating demo portfolio...")
    portfolio = PaperTradingPortfolio(starting_cash=10000)
    
    # Make some demo trades
    print("2. Adding demo trades...")
    
    # Open a position
    success, result = portfolio.open_position(
        ticker="AAPL",
        option_type="call",
        strike=180.0,
        expiration=1711324800,  # March 25, 2026
        quantity=1,
        price=2.50
    )
    
    if success:
        print(f"   ✓ Opened AAPL call position")
    
    # Open another position
    success, result = portfolio.open_position(
        ticker="MSFT",
        option_type="put",
        strike=420.0,
        expiration=1711324800,
        quantity=2,
        price=3.75
    )
    
    if success:
        print(f"   ✓ Opened MSFT put position")
    
    # Show portfolio stats
    print("\n3. Portfolio Summary:")
    stats = portfolio.get_statistics()
    print(f"   Cash: ${portfolio.cash:,.2f}")
    print(f"   Open Positions: {len(portfolio.get_open_positions())}")
    print(f"   Total Trades: {stats['total_trades']}")
    
    # Sync to Google Sheets
    print("\n4. Syncing to Google Sheets...")
    
    try:
        sync = setup_google_sheets_sync(creds_path)
        if sync is None:
            print("   ❌ Could not setup Google Sheets sync")
            return
        
        success, result = sync.save_portfolio(portfolio)
        
        if success:
            print(f"   ✅ Successfully synced to Google Sheets!")
            print(f"   🔗 Spreadsheet URL: {result}")
            print("\n   Open the link above to view your portfolio in Google Sheets!")
        else:
            print(f"   ❌ Sync failed: {result}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)

if __name__ == "__main__":
    demo_sheets_sync()
