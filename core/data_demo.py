import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data import (
    load_history, 
    get_current_price, 
    get_price_stats,
    clear_cache
)
import pandas as pd

print("="*60)
print("DATA.PY DEMO - Stock Data Loading")
print("="*60)

# Example 1: Load history with caching
print("\n1. Loading stock history (with automatic caching)...")
ticker = "AAPL"
df = load_history(ticker, days=30)

if df is not None:
    print(f"\n   {ticker} - Last 5 days:")
    print("   " + "-"*55)
    
    # Show last 5 days
    for date, row in df.tail(5).iterrows():
        print(f"   {date.date()}: Open=${row['Open']:.2f} Close=${row['Close']:.2f} Volume={row['Volume']:,.0f}")

# Example 2: Get current price (super fast)
print("\n2. Getting current prices (cached)...")
tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]

print("\n   Ticker  Price")
print("   " + "-"*20)
for ticker in tickers:
    price = get_current_price(ticker)
    if price:
        print(f"   {ticker:<6} ${price:>7.2f}")

# Example 3: Get detailed statistics
print("\n3. Getting price statistics...")
stats = get_price_stats("AAPL", days=30)

if stats:
    print(f"\n   {stats['ticker']} - 30 Day Statistics:")
    print("   " + "-"*55)
    print(f"   Current Price:    ${stats['current_price']:.2f}")
    print(f"   Period High:      ${stats['period_high']:.2f}")
    print(f"   Period Low:       ${stats['period_low']:.2f}")
    print(f"   Total Return:     {stats['total_return']*100:+.2f}%")
    print(f"   Volatility:       {stats['volatility']:.4f}")
    print(f"   Avg Daily Volume: {stats['avg_volume']:,.0f}")

# Example 4: Compare multiple stocks
print("\n4. Comparing stocks...")
compare_tickers = ["AAPL", "MSFT", "GOOGL"]

print("\n   Ticker  Price    30d Return  Volatility")
print("   " + "-"*50)

for ticker in compare_tickers:
    stats = get_price_stats(ticker, days=30)
    if stats:
        print(f"   {ticker:<6} ${stats['current_price']:>7.2f}  {stats['total_return']*100:>+6.2f}%    {stats['volatility']:>6.4f}")

# Example 5: Historical price chart (simple text version)
print("\n5. Simple price chart (last 10 days)...")
df = load_history("AAPL", days=10)

if df is not None:
    print(f"\n   {ticker} Price Trend:")
    closes = df['Close'].values
    min_price = closes.min()
    max_price = closes.max()
    
    for i, (date, row) in enumerate(df.iterrows()):
        price = row['Close']
        # Normalize to 0-50 scale for chart
        bar_len = int(((price - min_price) / (max_price - min_price)) * 40) + 1
        bar = "█" * bar_len
        print(f"   {date.date()} ${price:>6.2f} {bar}")

print("\n" + "="*60)
print("✓ Demo Complete!")
print("="*60)
print("\nKey Features:")
print("  • Automatic fallback from Polygon to Yahoo Finance")
print("  • 5-minute caching for faster repeated requests")
print("  • Data validation and quality checks")
print("  • Helper functions for common tasks")
print("  • Detailed error messages for debugging")
print("="*60 + "\n")
