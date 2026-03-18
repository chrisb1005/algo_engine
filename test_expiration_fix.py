"""
Test script to verify expiration date selection fix
"""
import datetime as dt
from core.contracts import get_next_week_expiration, load_options_chain_metadata

def test_expiration_selection():
    """Test that we get future expirations, not near-term ones"""
    print("Testing expiration date selection...\n")
    
    tickers = ['AAPL', 'MSFT', 'TSLA']
    
    for ticker in tickers:
        print(f"\n{ticker}:")
        print("-" * 50)
        
        # Get metadata to see all available expirations
        meta = load_options_chain_metadata(ticker)
        if meta and 'expirations' in meta:
            print(f"Available expirations:")
            today = dt.datetime.now()
            for exp_timestamp in sorted(meta['expirations'])[:5]:  # Show first 5
                exp_date = dt.datetime.fromtimestamp(exp_timestamp)
                days_away = (exp_date - today).days
                print(f"  - {exp_date.strftime('%Y-%m-%d')} ({days_away} days away)")
        
        # Get the selected expiration
        selected = get_next_week_expiration(ticker)
        if selected:
            selected_date = dt.datetime.fromtimestamp(selected)
            days_away = (selected_date - today).days
            print(f"\n✓ SELECTED: {selected_date.strftime('%Y-%m-%d')} ({days_away} days away)")
            
            if days_away < 3:
                print(f"  ⚠️ WARNING: Selected expiration is less than 3 days away!")
            else:
                print(f"  ✓ Good! Expiration is {days_away} days away")
        else:
            print("  ✗ ERROR: No expiration found")

if __name__ == "__main__":
    test_expiration_selection()
