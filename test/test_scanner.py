"""
Test script for the stock scanner module
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.scanner import scan_stock_for_options, get_quick_recommendations

print("=" * 80)
print("STOCK SCANNER TEST")
print("=" * 80)

# Test 1: Scan a single stock
print("\n" + "=" * 80)
print("TEST 1: Scan single stock (AAPL)")
print("=" * 80)

try:
    result = scan_stock_for_options("AAPL", min_price=10, max_price=30, verbose=True)
    
    if result:
        print(f"\n✅ SUCCESS - AAPL scan completed")
        print(f"Score: {result['score']}/15")
        print(f"Current Price: ${result['current_price']:.2f}")
        print(f"Volatility: {result['volatility']*100:.2f}%")
        print(f"Avg Volume: {result['avg_volume']:,.0f}")
        print(f"Affordable Calls: {result['affordable_calls']}")
        print(f"Affordable Puts: {result['affordable_puts']}")
        print(f"Signal: {result['action']}")
        
        if result['best_call']:
            print(f"\nBest Call:")
            print(f"  Strike: ${result['best_call']['strike']:.2f}")
            print(f"  Price: ${result['best_call']['price']:.2f}")
            print(f"  Volume: {int(result['best_call']['volume']):,}")
        
        if result['best_put']:
            print(f"\nBest Put:")
            print(f"  Strike: ${result['best_put']['strike']:.2f}")
            print(f"  Price: ${result['best_put']['price']:.2f}")
            print(f"  Volume: {int(result['best_put']['volume']):,}")
    else:
        print("❌ FAILED - AAPL scan returned None")
        
except Exception as e:
    print(f"❌ ERROR scanning AAPL: {str(e)}")
    import traceback
    traceback.print_exc()

# Test 2: Quick recommendations
print("\n" + "=" * 80)
print("TEST 2: Get quick recommendations (top 3)")
print("=" * 80)

try:
    recommendations = get_quick_recommendations(count=3)
    
    if recommendations:
        print(f"\n✅ SUCCESS - Found {len(recommendations)} recommendations")
        
        for i, rec in enumerate(recommendations):
            print(f"\n#{i+1} - {rec['ticker']} (Score: {rec['score']}/15)")
            print(f"  Price: ${rec['current_price']:.2f}")
            print(f"  Volatility: {rec['volatility']*100:.2f}%")
            print(f"  Volume: {rec['avg_volume']:,.0f}")
            print(f"  Affordable Calls: {rec['affordable_calls']}")
            print(f"  Affordable Puts: {rec['affordable_puts']}")
            print(f"  Signal: {rec['action']}")
    else:
        print("⚠️ WARNING - No recommendations found")
        
except Exception as e:
    print(f"❌ ERROR getting recommendations: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("TEST COMPLETED")
print("=" * 80)
