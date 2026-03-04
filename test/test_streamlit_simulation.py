"""
Test script to simulate Streamlit app behavior with different tickers
This will help debug any issues
"""

import sys
import os

# Fix Windows console encoding issues
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_streamlit_flow(ticker, days=60):
    """Simulate the exact flow that Streamlit uses"""
    print(f"\n{'='*60}")
    print(f"Simulating Streamlit flow for: {ticker.upper()}")
    print(f"{'='*60}")
    
    # Sanitize input like Streamlit does
    ticker = ticker.upper().strip()
    
    # Validate ticker
    if not ticker.replace(".", "").replace("-", "").isalpha():
        print(f"  ⚠️  Invalid ticker format: {ticker}")
        return False
    
    try:
        # Import modules (like Streamlit does)
        from core.data import load_history, get_current_price
        from core.indicators import compute_indicators
        from core.signals import generate_signal
        from core.strategies import decide_action
        from core.contracts import choose_contract
        
        # Step 1: Load data
        print(f"\n1. Loading data...")
        data_days = days + 40
        df = load_history(ticker, days=data_days)
        
        if df is None or len(df) == 0:
            print(f"  ❌ No data found for {ticker}")
            return False
        
        print(f"  ✓ Loaded {len(df)} rows")
        
        # Step 2: Get current price
        print(f"\n2. Getting current price...")
        current_price = get_current_price(ticker)
        print(f"  ✓ Current price: ${current_price:.2f}" if current_price else "  ⚠️  No current price")
        
        # Step 3: Compute indicators
        print(f"\n3. Computing indicators...")
        df = compute_indicators(df)
        df_clean = df.dropna()
        
        if len(df_clean) == 0:
            print(f"  ❌ Not enough data after computing indicators")
            return False
        
        print(f"  ✓ {len(df_clean)} rows after cleaning")
        
        # Step 4: Generate signal
        print(f"\n4. Generating signal...")
        sig = generate_signal(df_clean)
        print(f"  ✓ Trend: {sig.get('trend')}, RSI: {sig.get('rsi', 0):.1f}")
        
        # Step 5: Get action
        print(f"\n5. Getting strategy action...")
        action = decide_action(sig)
        print(f"  ✓ Action: {action}")
        
        # Step 6: Get contract (if needed)
        if action != "NO_TRADE":
            print(f"\n6. Finding contract...")
            try:
                contract = choose_contract(ticker, action)
                
                if contract:
                    print(f"  ✓ Contract: {contract['symbol']}")
                    print(f"    Strike: ${contract['strike']:.2f}")
                    print(f"    Last: ${contract['last_price']:.2f}")
                else:
                    print(f"  ⚠️  No contract found (this can happen)")
            except Exception as contract_error:
                print(f"  ⚠️  Contract error: {str(contract_error)[:100]}")
                print(f"  ℹ️  Analysis is still valid")
        
        print(f"\n✅ {ticker} completed successfully")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Test various tickers including edge cases
    test_cases = [
        # Valid major stocks
        ("AAPL", "Apple - should work"),
        ("MSFT", "Microsoft - should work"),
        ("GOOGL", "Google - should work"),
        ("TSLA", "Tesla - should work"),
        ("spy", "SPY lowercase - should work"),
        ("  NVDA  ", "NVDA with spaces - should work"),
        
        # Edge cases
        ("BRK.B", "Berkshire with dot - should work"),
        
        # Invalid
        ("", "Empty string - should fail gracefully"),
        ("123", "Numbers - should fail validation"),
        ("INVALID123", "Mixed - should fail validation"),
    ]
    
    results = []
    
    for ticker, description in test_cases:
        print(f"\n\n{'#'*60}")
        print(f"Test Case: {description}")
        print(f"Input: '{ticker}'")
        print(f"{'#'*60}")
        
        success = test_streamlit_flow(ticker)
        results.append((ticker, description, success))
        
        import time
        time.sleep(0.5)  # Small delay to avoid rate limiting
    
    # Final summary
    print(f"\n\n{'='*60}")
    print("FINAL SUMMARY")
    print(f"{'='*60}")
    
    for ticker, description, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {description}")
    
    passed = sum(1 for _, _, s in results if s)
    print(f"\nPassed: {passed}/{len(results)}")
    print(f"{'='*60}")
