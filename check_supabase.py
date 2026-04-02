"""
Test script to check what's actually stored in Supabase
"""
from dotenv import load_dotenv
from core.supabase_sync import setup_supabase_sync
import json

# Load .env
load_dotenv()

# Connect to Supabase
sync = setup_supabase_sync()

if not sync:
    print("❌ Failed to connect to Supabase")
    print("Check your .env file has SUPABASE_URL and SUPABASE_KEY")
    exit(1)

print("✅ Connected to Supabase")
print("\n" + "="*60)

# List all portfolios
portfolios = sync.list_portfolio_names()
print(f"\n📋 Found {len(portfolios)} portfolio(s):\n")

for portfolio_name in portfolios:
    print(f"\n{'='*60}")
    print(f"Portfolio: {portfolio_name}")
    print("="*60)
    
    # Load portfolio data
    data = sync.load_portfolio(portfolio_name)
    
    if data:
        portfolio_info = data['portfolio']
        
        print(f"\n💰 Cash: ${portfolio_info['current_cash']:,.2f}")
        print(f"📊 Positions: {len(data['positions'])}")
        print(f"📜 Trades: {len(data['trades'])}")
        
        # Check agent_config
        agent_config_raw = portfolio_info.get('agent_config')
        print(f"\n🤖 Agent Config (raw): {agent_config_raw}")
        
        if agent_config_raw:
            try:
                agent_config = json.loads(agent_config_raw)
                print(f"\n✅ Agent Config (parsed):")
                print(f"   Tickers: {agent_config.get('tickers', 'NOT SET')}")
                print(f"   Check Interval: {agent_config.get('check_interval', 'NOT SET')}s")
                print(f"   Position Size: {agent_config.get('position_size', 'NOT SET')}")
            except json.JSONDecodeError as e:
                print(f"\n❌ Failed to parse agent_config: {e}")
        else:
            print(f"\n⚠️  Agent Config is NULL - needs to be synced!")
            print(f"   Solution: Load this portfolio in Streamlit and click 'Sync to Cloud'")

print("\n" + "="*60)
print("\n✅ Check complete!")
