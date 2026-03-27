"""
Demo script for Supabase integration
Tests saving portfolio to Supabase cloud database
"""

import sys
import os
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.paper_trader import PaperTradingPortfolio
from core.supabase_sync import setup_supabase_sync

def demo_supabase_sync():
    """Demo Supabase portfolio sync"""
    print("=" * 60)
    print("Supabase Portfolio Sync Demo")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Check for credentials
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("\n❌ ERROR: Supabase credentials not found!")
        print("\nTo use Supabase sync, you need to:")
        print("1. Create a free account at https://supabase.com")
        print("2. Create a new project (takes ~2 minutes)")
        print("3. Get your Project URL and API key from Project Settings > API")
        print("4. Either:")
        print("   - Create a .env file with SUPABASE_URL and SUPABASE_KEY")
        print("   - Or set these as environment variables")
        print("\nSee SUPABASE_SETUP.md for detailed instructions.")
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
        expiration=1743033600,  # March 25, 2026
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
        expiration=1743033600,
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
    
    # Sync to Supabase
    print("\n4. Syncing to Supabase...")
    
    try:
        success, result = portfolio.save_to_supabase("demo_portfolio")
        
        if success:
            print(f"   ✅ Successfully synced to Supabase!")
            print(f"   💾 {result}")
            print(f"\n   View your data at: {supabase_url}")
        else:
            print(f"   ❌ Sync failed: {result}")
        
        # Test loading
        print("\n5. Testing load from Supabase...")
        loaded_portfolio = PaperTradingPortfolio.load_from_supabase("demo_portfolio")
        
        if loaded_portfolio:
            print(f"   ✅ Successfully loaded portfolio!")
            print(f"   Cash: ${loaded_portfolio.cash:,.2f}")
            print(f"   Open Positions: {len(loaded_portfolio.get_open_positions())}")
        else:
            print(f"   ❌ Could not load portfolio")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)

if __name__ == "__main__":
    demo_supabase_sync()
