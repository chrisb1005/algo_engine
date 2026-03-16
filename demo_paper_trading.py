"""
Demo: Paper Trading Agent - Quick Start Example
Run this to see the agent in action (1 cycle only for demo)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.paper_trader import PaperTradingPortfolio
from core.auto_agent import AutoTradingAgent

print("=" * 80)
print("PAPER TRADING AGENT - QUICK DEMO")
print("=" * 80)

# Step 1: Create portfolio with $10,000 virtual cash
print("\n📊 Creating portfolio with $10,000...")
portfolio = PaperTradingPortfolio(
    starting_cash=10000,
    max_position_size=0.10,  # Max 10% per position
    max_positions=5           # Max 5 positions
)
print(f"✅ Portfolio created - Starting balance: ${portfolio.cash:,.2f}")

# Step 2: Create agent to monitor stocks
tickers = ["AAPL", "MSFT", "TSLA"]
print(f"\n🤖 Creating agent to monitor: {', '.join(tickers)}")

agent = AutoTradingAgent(
    portfolio=portfolio,
    tickers=tickers,
    check_interval=300,  # 5 minutes (not used in this demo)
    position_size=1      # Buy 1 contract per signal
)
print(f"✅ Agent created")

# Step 3: Run one trading cycle (checks all tickers once)
print(f"\n🔍 Running one trading cycle...")
print(f"Agent will check each ticker for signals and execute if found\n")

try:
    trades = agent.run_cycle()
    
    # Step 4: Show results
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    
    print(f"\n💼 Portfolio Status:")
    print(f"  Cash: ${portfolio.cash:,.2f}")
    print(f"  Open Positions: {len(portfolio.get_open_positions())}")
    print(f"  Trades Executed This Cycle: {trades}")
    
    # Show open positions
    open_positions = portfolio.get_open_positions()
    if open_positions:
        print(f"\n📈 Open Positions:")
        for pos in open_positions:
            cost = pos.entry_price * pos.quantity * 100
            print(f"  - {pos.ticker} {pos.option_type.upper()} ${pos.strike:.2f}")
            print(f"    Entry: ${pos.entry_price:.2f} x {pos.quantity} = ${cost:.2f}")
            print(f"    Expires: {pos.expiration.strftime('%Y-%m-%d')}")
    else:
        print(f"\n📈 No positions opened (no buy signals found)")
    
    # Show statistics
    stats = portfolio.get_statistics()
    print(f"\n📊 Statistics:")
    print(f"  Total Trades: {stats['total_trades']}")
    print(f"  Win Rate: {stats['win_rate']:.1f}%")
    print(f"  Total P&L: ${stats['total_pnl']:.2f}")
    
    # Show recent log messages
    if agent.log:
        print(f"\n📜 Activity Log (last 10 messages):")
        for msg in agent.log[-10:]:
            print(f"  {msg}")

except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("DEMO COMPLETE")
print("=" * 80)
print("\n💡 To run the full agent with monitoring:")
print("   1. Launch Streamlit: streamlit run app.py")
print("   2. Navigate to '🤖 Paper Trading Agent'")
print("   3. Configure and start the agent")
print("\n⚠️  This was just 1 cycle. The real agent runs continuously!")
