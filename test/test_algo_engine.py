"""
Test script to verify algo_engine.py functionality
This simulates what the Streamlit app will do
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data import load_history, get_current_price
from core.indicators import compute_indicators
from core.signals import generate_signal
from core.strategies import decide_action
from core.contracts import choose_contract

def test_algo_engine(ticker="AAPL", days=60):
    """Test the complete algo engine workflow"""
    print("="*60)
    print(f"ALGO ENGINE TEST - {ticker}")
    print("="*60)
    
    # Step 1: Load data (request more to account for weekends/holidays)
    print(f"\n1. Loading {days} days of data for {ticker}...")
    # Request extra days to ensure we have enough after computing indicators
    df = load_history(ticker, days=days+40)
    
    if df is None or len(df) == 0:
        print(f"  ✗ FAILED: No data for {ticker}")
        return False
    
    print(f"  ✓ Loaded {len(df)} rows")
    print(f"  ✓ Date range: {df.index[0].date()} to {df.index[-1].date()}")
    
    # Step 2: Get current price
    print(f"\n2. Getting current price...")
    current_price = get_current_price(ticker)
    
    if current_price:
        print(f"  ✓ Current price: ${current_price:.2f}")
    else:
        print(f"  ⚠ Could not get current price")
    
    # Step 3: Compute indicators
    print(f"\n3. Computing technical indicators...")
    df = compute_indicators(df)
    df_clean = df.dropna()
    
    if len(df_clean) == 0:
        print(f"  ✗ FAILED: Not enough data after computing indicators")
        return False
    
    print(f"  ✓ Indicators computed successfully")
    print(f"  ✓ Clean data rows: {len(df_clean)}")
    
    # Check indicators exist
    indicators = ["MA20", "MA50", "RSI", "Momentum", "Volatility"]
    for ind in indicators:
        if ind in df_clean.columns:
            print(f"  ✓ {ind}: {df_clean[ind].iloc[-1]:.2f}")
        else:
            print(f"  ✗ Missing indicator: {ind}")
    
    # Step 4: Generate signal
    print(f"\n4. Generating trading signal...")
    sig = generate_signal(df_clean)
    
    if sig:
        print(f"  ✓ Signal generated:")
        print(f"    Trend: {sig.get('trend', 'N/A')}")
        print(f"    RSI: {sig.get('rsi', 0):.2f}")
        print(f"    Volatility: {sig.get('vol', 0):.2f}%")
        print(f"    Momentum: {sig.get('momentum', 0):.4f}")
    else:
        print(f"  ✗ FAILED: Could not generate signal")
        return False
    
    # Step 5: Get strategy recommendation
    print(f"\n5. Getting strategy recommendation...")
    action = decide_action(sig)
    
    if action:
        print(f"  ✓ Recommended action: {action}")
        
        action_descriptions = {
            "BUY_CALL": "Bullish momentum - Consider buying call options",
            "BUY_PUT": "Bearish momentum - Consider buying put options",
            "SELL_CALL": "Overbought - Consider selling covered calls",
            "SELL_PUT": "Oversold - Consider selling cash-secured puts",
            "NO_TRADE": "No clear signal - Stay on sidelines"
        }
        
        print(f"  ℹ {action_descriptions.get(action, '')}")
    else:
        print(f"  ✗ FAILED: Could not determine action")
        return False
    
    # Step 6: Get contract recommendation (if not NO_TRADE)
    if action != "NO_TRADE":
        print(f"\n6. Finding optimal contract...")
        contract = choose_contract(ticker, action)
        
        if contract:
            print(f"  ✓ Contract found:")
            print(f"    Symbol: {contract['symbol']}")
            print(f"    Strike: ${contract['strike']:.2f}")
            print(f"    Last Price: ${contract['last_price']:.2f}")
            print(f"    Bid/Ask: ${contract['bid']:.2f} / ${contract['ask']:.2f}")
            print(f"    Volume: {int(contract['volume']):,}")
            print(f"    Open Interest: {int(contract['open_interest']):,}")
            print(f"    IV: {contract['implied_volatility']*100:.1f}%")
            print(f"    Expiration: {contract['expiration']} ({contract['days_to_expiration']} days)")
            print(f"    In The Money: {contract['in_the_money']}")
        else:
            print(f"  ⚠ Could not find suitable contract (may need to retry)")
    else:
        print(f"\n6. No contract recommendation (NO_TRADE signal)")
    
    print("\n" + "="*60)
    print("✓ ALGO ENGINE TEST COMPLETE")
    print("="*60)
    return True


def test_multiple_tickers():
    """Test algo engine with multiple tickers"""
    print("\n" + "="*60)
    print("TESTING MULTIPLE TICKERS")
    print("="*60)
    
    tickers = ["AAPL", "MSFT", "TSLA"]
    results = []
    
    for ticker in tickers:
        print(f"\n{'='*60}")
        print(f"Testing {ticker}...")
        print(f"{'='*60}")
        
        try:
            result = test_algo_engine(ticker, days=60)
            results.append((ticker, result))
        except Exception as e:
            print(f"\n✗ ERROR testing {ticker}: {e}")
            results.append((ticker, False))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for ticker, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"  {ticker}: {status}")
    
    success_rate = sum(1 for _, s in results if s) / len(results) * 100
    print(f"\nSuccess Rate: {success_rate:.0f}%")
    print("="*60)


if __name__ == "__main__":
    # Test single ticker
    success = test_algo_engine("AAPL", days=60)
    
    # Test multiple tickers
    if success:
        print("\n\n")
        test_multiple_tickers()
