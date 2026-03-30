"""
Test script to save and load a portfolio from Supabase with a specific name
"""
from core.paper_trader import PaperTradingPortfolio
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

print("=" * 60)
print("Testing Supabase Save/Load with portfolio name 'num_1'")
print("=" * 60)

# Verify credentials are loaded
print(f"\n✓ SUPABASE_URL: {os.getenv('SUPABASE_URL')[:50]}...")
print(f"✓ SUPABASE_KEY: {os.getenv('SUPABASE_KEY')[:50]}...")

# Create a test portfolio
print("\n[1] Creating test portfolio...")
portfolio = PaperTradingPortfolio(
    starting_cash=10000,
    max_position_size=1000,
    max_positions=5
)
print(f"✓ Created portfolio with ${portfolio.cash:,.2f}")

# Save to Supabase with name 'num_1'
print("\n[2] Saving to Supabase with name 'num_1'...")
agent_config = {
    'tickers': ['AAPL', 'MSFT', 'GOOGL'],
    'check_interval': 300,
    'position_size': 1
}
success, message = portfolio.save_to_supabase(portfolio_name='num_1', agent_config=agent_config)

if success:
    print(f"✓ {message}")
else:
    print(f"✗ {message}")
    exit(1)

# Load from Supabase with name 'num_1'
print("\n[3] Loading from Supabase with name 'num_1'...")
loaded = PaperTradingPortfolio.load_from_supabase(portfolio_name='num_1')

if loaded:
    print(f"✓ Portfolio loaded successfully!")
    print(f"  - Cash: ${loaded.cash:,.2f}")
    print(f"  - Starting Cash: ${loaded.starting_cash:,.2f}")
    print(f"  - Max Position Size: ${loaded.max_position_size:,.2f}")
    print(f"  - Max Positions: {loaded.max_positions}")
    print(f"  - Open Positions: {len(loaded.get_open_positions())}")
    print(f"  - Total Trades: {len(loaded.trade_history)}")
    
    # Check if agent config was saved
    from core.supabase_sync import setup_supabase_sync
    sync = setup_supabase_sync()
    if sync:
        data = sync.load_portfolio('num_1')
        if data and data['portfolio'].get('agent_config'):
            import json
            config = json.loads(data['portfolio']['agent_config'])
            print(f"  - Agent Config: {config}")
        else:
            print("  ⚠ No agent config found")
else:
    print("✗ Failed to load portfolio")
    exit(1)

print("\n" + "=" * 60)
print("✅ All tests passed!")
print("=" * 60)
