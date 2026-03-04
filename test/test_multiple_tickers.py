"""
Test algo engine with different tickers to find the issue
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data import load_history, get_current_price
from core.indicators import compute_indicators
from core.signals import generate_signal
from core.strategies import decide_action
from core.contracts import choose_contract

def test_ticker(ticker):
    """Test a single ticker"""
    print(f"\n{'='*60}")
    print(f"Testing {ticker}")
    print(f"{'='*60}")
    
    try:
        # Load data
        print(f"1. Loading data...")
        df = load_history(ticker, days=100)
        
        if df is None or len(df) == 0:
            print(f"  ✗ No data available for {ticker}")
            return False
        
        print(f"  ✓ Loaded {len(df)} rows")
        
        # Compute indicators
        print(f"2. Computing indicators...")
        df = compute_indicators(df)
        df_clean = df.dropna()
        
        if len(df_clean) == 0:
            print(f"  ✗ Not enough data after computing indicators")
            return False
        
        print(f"  ✓ {len(df_clean)} rows after cleaning")
        
        # Generate signal
        print(f"3. Generating signal...")
        sig = generate_signal(df_clean)
        print(f"  ✓ Signal: {sig}")
        
        # Get action
        print(f"4. Getting action...")
        action = decide_action(sig)
        print(f"  ✓ Action: {action}")
        
        # Get contract (if not NO_TRADE)
        if action != "NO_TRADE":
            print(f"5. Finding contract...")
            contract = choose_contract(ticker, action)
            
            if contract:
                print(f"  ✓ Contract: {contract['symbol']}")
            else:
                print(f"  ⚠ No contract found (this can happen)")
        
        print(f"  ✓ {ticker} TEST PASSED")
        return True
        
    except Exception as e:
        print(f"  ✗ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Test multiple tickers
    tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "SPY", "NVDA", "AMZN"]
    
    results = []
    for ticker in tickers:
        success = test_ticker(ticker)
        results.append((ticker, success))
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    for ticker, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {ticker}: {status}")
    
    success_count = sum(1 for _, s in results if s)
    print(f"\nSuccess rate: {success_count}/{len(results)}")
