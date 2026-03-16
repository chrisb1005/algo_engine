"""
Test script for paper trading agent
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.paper_trader import PaperTradingPortfolio, Position
from core.auto_agent import AutoTradingAgent
import datetime as dt

print("=" * 80)
print("PAPER TRADING AGENT TEST")
print("=" * 80)

# Test 1: Create portfolio
print("\n" + "=" * 80)
print("TEST 1: Create Portfolio")
print("=" * 80)

portfolio = PaperTradingPortfolio(
    starting_cash=10000,
    max_position_size=0.05,
    max_positions=5
)

print(f"✅ Portfolio created")
print(f"Starting Cash: ${portfolio.starting_cash:,.2f}")
print(f"Current Cash: ${portfolio.cash:,.2f}")
print(f"Max Positions: {portfolio.max_positions}")
print(f"Max Position Size: {portfolio.max_position_size*100}%")

# Test 2: Open a position
print("\n" + "=" * 80)
print("TEST 2: Open Position")
print("=" * 80)

try:
    success, result = portfolio.open_position(
        ticker="AAPL",
        option_type="call",
        strike=150.0,
        expiration=dt.datetime.now() + dt.timedelta(days=7),
        quantity=1,
        price=5.00
    )
    
    if success:
        print(f"✅ Position opened successfully")
        print(f"Cash remaining: ${portfolio.cash:,.2f}")
        print(f"Open positions: {len(portfolio.get_open_positions())}")
        
        pos = portfolio.get_open_positions()[0]
        print(f"\nPosition details:")
        print(f"  Ticker: {pos.ticker}")
        print(f"  Type: {pos.option_type}")
        print(f"  Strike: ${pos.strike:.2f}")
        print(f"  Quantity: {pos.quantity}")
        print(f"  Entry Price: ${pos.entry_price:.2f}")
        print(f"  Cost: ${pos.entry_price * pos.quantity * 100:.2f}")
    else:
        print(f"❌ Failed to open position: {result}")

except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()

# Test 3: Close position
print("\n" + "=" * 80)
print("TEST 3: Close Position")
print("=" * 80)

try:
    open_positions = portfolio.get_open_positions()
    
    if open_positions:
        pos = open_positions[0]
        
        # Close at a profit
        exit_price = 6.50
        success, message = portfolio.close_position(pos, exit_price)
        
        if success:
            print(f"✅ Position closed")
            print(f"Exit Price: ${exit_price:.2f}")
            print(f"P&L: ${pos.get_pnl():.2f}")
            print(f"P&L %: {pos.get_pnl_percent():+.2f}%")
            print(f"Cash after close: ${portfolio.cash:,.2f}")
        else:
            print(f"❌ Failed to close: {message}")
    else:
        print("⚠️ No open positions to close")

except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()

# Test 4: Portfolio statistics
print("\n" + "=" * 80)
print("TEST 4: Portfolio Statistics")
print("=" * 80)

stats = portfolio.get_statistics()

print(f"Total Trades: {stats['total_trades']}")
print(f"Winning Trades: {stats['winning_trades']}")
print(f"Losing Trades: {stats['losing_trades']}")
print(f"Win Rate: {stats['win_rate']:.1f}%")
print(f"Total P&L: ${stats['total_pnl']:,.2f}")
print(f"Avg P&L: ${stats['avg_pnl']:,.2f}")
print(f"Best Trade: ${stats['best_trade']:,.2f}")
print(f"Worst Trade: ${stats['worst_trade']:,.2f}")

# Test 5: Create auto-trading agent
print("\n" + "=" * 80)
print("TEST 5: Create Auto-Trading Agent")
print("=" * 80)

try:
    # Create new portfolio for agent
    agent_portfolio = PaperTradingPortfolio(starting_cash=10000)
    
    # Create agent
    agent = AutoTradingAgent(
        portfolio=agent_portfolio,
        tickers=["AAPL"],
        check_interval=60,
        position_size=1
    )
    
    print(f"✅ Agent created")
    print(f"Monitoring: {', '.join(agent.tickers)}")
    print(f"Check interval: {agent.check_interval} seconds")
    print(f"Position size: {agent.position_size} contracts")
    
    # Test signal retrieval (don't actually trade)
    print(f"\n🔍 Testing signal retrieval for AAPL...")
    action, signal = agent.get_signal_for_ticker("AAPL")
    
    if action:
        print(f"✅ Signal retrieved: {action}")
        print(f"Signal details: {signal}")
    else:
        print(f"⚠️ Could not get signal: {signal}")

except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()

# Test 6: Save and load portfolio
print("\n" + "=" * 80)
print("TEST 6: Save/Load Portfolio")
print("=" * 80)

try:
    # Save
    filepath = "test_portfolio.json"
    portfolio.save_to_file(filepath)
    print(f"✅ Portfolio saved to {filepath}")
    
    # Load
    loaded_portfolio = PaperTradingPortfolio.load_from_file(filepath)
    
    if loaded_portfolio:
        print(f"✅ Portfolio loaded successfully")
        print(f"Starting Cash: ${loaded_portfolio.starting_cash:,.2f}")
        print(f"Current Cash: ${loaded_portfolio.cash:,.2f}")
        print(f"Total Positions: {len(loaded_portfolio.positions)}")
        print(f"Total Trades: {len(loaded_portfolio.trade_history)}")
        
        # Clean up test file
        os.remove(filepath)
        print(f"🗑️ Test file removed")
    else:
        print(f"❌ Failed to load portfolio")

except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("TEST COMPLETED")
print("=" * 80)
