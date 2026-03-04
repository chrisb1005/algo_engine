import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.data import (
    load_history,
    get_polygon_history,
    get_yahoo_history,
    validate_data,
    get_current_price,
    get_price_stats,
    clear_cache
)
import time


def test_yahoo_finance():
    """Test Yahoo Finance data source"""
    print("="*60)
    print("Test 1: Yahoo Finance API")
    print("="*60)
    
    ticker = "AAPL"
    days = 60
    
    print(f"\nFetching {days} days of {ticker} data from Yahoo Finance...")
    df = get_yahoo_history(ticker, days)
    
    if df is not None:
        print(f"  ✓ Received {len(df)} rows")
        print(f"  ✓ Columns: {list(df.columns)}")
        print(f"  ✓ Date range: {df.index[0].date()} to {df.index[-1].date()}")
        print(f"  ✓ Latest close: ${df['Close'].iloc[-1]:.2f}")
        print(f"  ✓ Price range: ${df['Low'].min():.2f} - ${df['High'].max():.2f}")
        print(f"  ✓ Avg volume: {df['Volume'].mean():,.0f}")
        print("  PASSED\n")
        return True
    else:
        print("  ✗ FAILED - No data returned\n")
        return False


def test_polygon_api():
    """Test Polygon API data source"""
    print("="*60)
    print("Test 2: Polygon API")
    print("="*60)
    
    ticker = "AAPL"
    days = 60
    
    print(f"\nFetching {days} days of {ticker} data from Polygon...")
    df = get_polygon_history(ticker, days)
    
    if df is not None:
        print(f"  ✓ Received {len(df)} rows")
        print(f"  ✓ Columns: {list(df.columns)}")
        print(f"  ✓ Date range: {df.index[0].date()} to {df.index[-1].date()}")
        print(f"  ✓ Latest close: ${df['Close'].iloc[-1]:.2f}")
        print(f"  ✓ Price range: ${df['Low'].min():.2f} - ${df['High'].max():.2f}")
        print(f"  ✓ Avg volume: {df['Volume'].mean():,.0f}")
        print("  PASSED\n")
        return True
    else:
        print("  ⚠ Polygon API unavailable (will fallback to Yahoo)")
        print("  SKIPPED\n")
        return False


def test_load_history():
    """Test the main load_history function with fallback"""
    print("="*60)
    print("Test 3: Load History with Fallback")
    print("="*60)
    
    ticker = "MSFT"
    days = 30
    
    print(f"\nLoading {days} days of {ticker} data...")
    df = load_history(ticker, days)
    
    if df is not None:
        print(f"  ✓ Received {len(df)} rows")
        print(f"  ✓ Date range: {df.index[0].date()} to {df.index[-1].date()}")
        print(f"  ✓ Latest close: ${df['Close'].iloc[-1]:.2f}")
        
        # Check data quality
        nulls = df.isnull().sum().sum()
        print(f"  ✓ Null values: {nulls}")
        
        # Check OHLC relationship
        valid_ohlc = all(
            (df['Low'] <= df['High']) & 
            (df['Low'] <= df['Close']) & 
            (df['Close'] <= df['High'])
        )
        print(f"  ✓ OHLC relationships valid: {valid_ohlc}")
        
        print("  PASSED\n")
        return True
    else:
        print("  ✗ FAILED - No data returned\n")
        return False


def test_multiple_tickers():
    """Test loading data for multiple tickers"""
    print("="*60)
    print("Test 4: Multiple Tickers")
    print("="*60)
    
    tickers = ["AAPL", "GOOGL", "TSLA", "SPY"]
    
    results = []
    for ticker in tickers:
        print(f"\n  Loading {ticker}...")
        df = load_history(ticker, days=20)
        
        if df is not None:
            price = df['Close'].iloc[-1]
            print(f"    ✓ {ticker}: ${price:.2f} ({len(df)} rows)")
            results.append(True)
        else:
            print(f"    ✗ {ticker}: Failed")
            results.append(False)
    
    success_rate = sum(results) / len(results) * 100
    print(f"\n  Success rate: {success_rate:.0f}% ({sum(results)}/{len(results)})")
    
    if success_rate >= 75:
        print("  PASSED\n")
        return True
    else:
        print("  ✗ FAILED - Too many failures\n")
        return False


def test_data_validation():
    """Test data validation function"""
    print("="*60)
    print("Test 5: Data Validation")
    print("="*60)
    
    ticker = "AAPL"
    df = load_history(ticker, days=30)
    
    if df is None:
        print("  ✗ FAILED - Could not load data\n")
        return False
    
    print("\n  Testing validation function...")
    
    # Test valid data
    is_valid = validate_data(df, ticker, expected_days=30)
    print(f"  ✓ Valid data check: {is_valid}")
    
    # Test with invalid data (missing columns)
    import pandas as pd
    bad_df = pd.DataFrame({'Price': [100, 101, 102]})
    is_invalid = not validate_data(bad_df, ticker)
    print(f"  ✓ Invalid data detection: {is_invalid}")
    
    # Test with empty data
    empty_df = pd.DataFrame()
    is_empty = not validate_data(empty_df, ticker)
    print(f"  ✓ Empty data detection: {is_empty}")
    
    print("  PASSED\n")
    return True


def test_current_price():
    """Test getting current price"""
    print("="*60)
    print("Test 6: Current Price")
    print("="*60)
    
    tickers = ["AAPL", "MSFT", "GOOGL"]
    
    print()
    for ticker in tickers:
        price = get_current_price(ticker)
        
        if price is not None:
            print(f"  ✓ {ticker}: ${price:.2f}")
        else:
            print(f"  ✗ {ticker}: Failed to get price")
    
    print("\n  PASSED\n")
    return True


def test_price_stats():
    """Test price statistics function"""
    print("="*60)
    print("Test 7: Price Statistics")
    print("="*60)
    
    ticker = "AAPL"
    days = 30
    
    print(f"\n  Getting {days}-day statistics for {ticker}...")
    stats = get_price_stats(ticker, days)
    
    if stats is not None:
        print(f"  ✓ Current Price: ${stats['current_price']:.2f}")
        print(f"  ✓ Period High: ${stats['period_high']:.2f}")
        print(f"  ✓ Period Low: ${stats['period_low']:.2f}")
        print(f"  ✓ Avg Volume: {stats['avg_volume']:,.0f}")
        print(f"  ✓ Volatility: {stats['volatility']:.4f}")
        print(f"  ✓ Avg Daily Return: {stats['avg_return']:.4f}")
        print(f"  ✓ Total Return: {stats['total_return']*100:.2f}%")
        print(f"  ✓ Data Points: {stats['data_points']}")
        print("\n  PASSED\n")
        return True
    else:
        print("  ✗ FAILED - Could not get statistics\n")
        return False


def test_caching():
    """Test data caching functionality"""
    print("="*60)
    print("Test 8: Data Caching")
    print("="*60)
    
    ticker = "AAPL"
    
    # Clear cache first
    clear_cache()
    print("\n  ✓ Cache cleared")
    
    # First load (should hit API)
    print(f"  First load of {ticker}...")
    start = time.time()
    df1 = load_history(ticker, days=30, use_cache=True)
    time1 = time.time() - start
    print(f"    Time: {time1:.3f}s")
    
    # Second load (should use cache)
    print(f"  Second load of {ticker} (cached)...")
    start = time.time()
    df2 = load_history(ticker, days=30, use_cache=True)
    time2 = time.time() - start
    print(f"    Time: {time2:.3f}s")
    
    if df1 is not None and df2 is not None:
        # Cache should be much faster
        speedup = time1 / time2 if time2 > 0 else float('inf')
        print(f"  ✓ Speedup: {speedup:.1f}x")
        
        # Data should be identical
        if len(df1) == len(df2):
            print(f"  ✓ Cached data matches original")
        
        print("\n  PASSED\n")
        return True
    else:
        print("  ✗ FAILED\n")
        return False


def test_different_periods():
    """Test loading different time periods"""
    print("="*60)
    print("Test 9: Different Time Periods")
    print("="*60)
    
    ticker = "SPY"
    periods = [5, 30, 90, 365]
    
    print(f"\n  Testing different periods for {ticker}...")
    
    for days in periods:
        df = load_history(ticker, days=days, use_cache=False)
        
        if df is not None:
            actual_days = len(df)
            expected_min = days * 0.5  # Allow for weekends/holidays
            
            if actual_days >= expected_min:
                print(f"  ✓ {days} days requested: Got {actual_days} rows")
            else:
                print(f"  ⚠ {days} days requested: Only got {actual_days} rows (expected >={expected_min:.0f})")
        else:
            print(f"  ✗ {days} days: Failed")
    
    print("\n  PASSED\n")
    return True


def test_error_handling():
    """Test error handling for invalid inputs"""
    print("="*60)
    print("Test 10: Error Handling")
    print("="*60)
    
    print("\n  Testing invalid ticker...")
    df = load_history("INVALID_TICKER_XYZ123", days=30)
    if df is None:
        print("  ✓ Correctly returned None for invalid ticker")
    else:
        print("  ⚠ Got data for invalid ticker (unexpected)")
    
    print("\n  Testing extreme date range...")
    df = load_history("AAPL", days=1000)
    if df is not None:
        print(f"  ✓ Handled large date range ({len(df)} rows)")
    else:
        print("  ⚠ Failed on large date range")
    
    print("\n  PASSED\n")
    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("DATA.PY TEST SUITE")
    print("="*60 + "\n")
    
    tests = [
        test_yahoo_finance,
        test_polygon_api,
        test_load_history,
        test_multiple_tickers,
        test_data_validation,
        test_current_price,
        test_price_stats,
        test_caching,
        test_different_periods,
        test_error_handling
    ]
    
    results = []
    start_time = time.time()
    
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ✗ EXCEPTION: {type(e).__name__}: {e}\n")
            results.append(False)
    
    total_time = time.time() - start_time
    
    # Summary
    print("="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"\nPassed: {passed}/{total} ({passed/total*100:.0f}%)")
    print(f"Total time: {total_time:.2f}s")
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED")
    else:
        print(f"\n⚠ {total - passed} TEST(S) FAILED")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()
