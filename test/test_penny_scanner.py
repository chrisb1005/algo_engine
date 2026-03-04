"""
Test script for the penny stock scanner module
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.penny_scanner import scan_penny_stock, get_quick_penny_movers, get_stock_due_diligence

print("=" * 80)
print("PENNY STOCK SCANNER TEST")
print("=" * 80)

# Test 1: Scan a single penny stock
print("\n" + "=" * 80)
print("TEST 1: Scan single penny stock (NIO)")
print("=" * 80)

try:
    result = scan_penny_stock("NIO", min_price=0.50, max_price=10.0, verbose=True)
    
    if result:
        print(f"\n✅ SUCCESS - NIO scan completed")
        print(f"Score: {result['score']}/15")
        print(f"Current Price: ${result['current_price']:.2f}")
        print(f"1-Day Change: {result['change_1d']:+.2f}%")
        print(f"5-Day Change: {result['change_5d']:+.2f}%")
        print(f"20-Day Change: {result['change_20d']:+.2f}%")
        print(f"Volume: {result['volume']:,.0f}")
        print(f"Volume Ratio: {result['volume_ratio']:.2f}x")
        print(f"Volatility: {result['volatility']*100:.2f}%")
        print(f"Trend: {result['trend']}")
    else:
        print("❌ FAILED - NIO scan returned None (may not meet criteria)")
        
except Exception as e:
    print(f"❌ ERROR scanning NIO: {str(e)}")
    import traceback
    traceback.print_exc()

# Test 2: Quick movers scan
print("\n" + "=" * 80)
print("TEST 2: Get quick penny movers (top 3)")
print("=" * 80)

try:
    movers = get_quick_penny_movers(count=3)
    
    if movers:
        print(f"\n✅ SUCCESS - Found {len(movers)} movers")
        
        for i, mover in enumerate(movers):
            print(f"\n#{i+1} - {mover['ticker']} (Score: {mover['score']}/15)")
            print(f"  Price: ${mover['current_price']:.2f}")
            print(f"  1D: {mover['change_1d']:+.2f}%")
            print(f"  5D: {mover['change_5d']:+.2f}%")
            print(f"  Volume Ratio: {mover['volume_ratio']:.1f}x")
            print(f"  Trend: {mover['trend']}")
    else:
        print("⚠️ WARNING - No movers found")
        
except Exception as e:
    print(f"❌ ERROR getting movers: {str(e)}")
    import traceback
    traceback.print_exc()

# Test 3: Due diligence on a penny stock
print("\n" + "=" * 80)
print("TEST 3: Due diligence analysis (PLUG)")
print("=" * 80)

try:
    dd_data = get_stock_due_diligence("PLUG")
    
    if 'error' in dd_data:
        print(f"❌ FAILED - {dd_data['error']}")
    else:
        print(f"\n✅ SUCCESS - DD analysis completed")
        print(f"Ticker: {dd_data['ticker']}")
        print(f"Current Price: ${dd_data['current_price']:.2f}")
        print(f"\nPrice Changes:")
        for period, data in dd_data['price_changes'].items():
            print(f"  {period}: {data['change_pct']:+.2f}%")
        
        print(f"\nVolume:")
        print(f"  Current: {dd_data['volume']['current']:,.0f}")
        print(f"  Avg (20d): {dd_data['volume']['avg_20d']:,.0f}")
        print(f"  Trend: {dd_data['volume']['trend']}")
        
        print(f"\nTechnicals:")
        print(f"  RSI: {dd_data['technicals']['rsi']:.1f}")
        print(f"  Volatility: {dd_data['technicals']['volatility']*100:.2f}%")
        print(f"  Momentum: {dd_data['technicals']['momentum']*100:+.2f}%")
        
        print(f"\n52-Week Range:")
        print(f"  High: ${dd_data['price_levels']['high_52w']:.2f}")
        print(f"  Low: ${dd_data['price_levels']['low_52w']:.2f}")
        print(f"  Position: {dd_data['price_levels']['position_in_range']:.1f}%")
        
        if dd_data['risk_factors']:
            print(f"\nRisk Factors ({len(dd_data['risk_factors'])}):")
            for risk in dd_data['risk_factors'][:3]:
                print(f"  - {risk}")
        
        if dd_data['opportunities']:
            print(f"\nOpportunities ({len(dd_data['opportunities'])}):")
            for opp in dd_data['opportunities'][:3]:
                print(f"  - {opp}")
        
except Exception as e:
    print(f"❌ ERROR performing DD: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("TEST COMPLETED")
print("=" * 80)
