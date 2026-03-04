from contracts import load_options_chain, get_next_week_expiration, load_options_chain_metadata
import datetime as dt

# Test ticker
ticker = "AAPL"

print("="*60)
print(f"OPTIONS CHAIN TEST - {ticker}")
print("="*60)

# Get metadata
print("\n1. Loading options metadata...")
meta = load_options_chain_metadata(ticker)
if meta:
    expirations = meta["expirations"]
    print(f"   ✓ Found {len(expirations)} expiration dates")
    
    # Show first 5 expirations with dates
    print("\n   Available expirations:")
    for i, exp_ts in enumerate(expirations[:5]):
        exp_date = dt.datetime.fromtimestamp(exp_ts)
        days_away = (exp_date - dt.datetime.now()).days
        print(f"     {i+1}. {exp_date.strftime('%Y-%m-%d (%A)')} - {days_away} days away")
    if len(expirations) > 5:
        print(f"     ... and {len(expirations) - 5} more")
else:
    print("   ✗ Failed to load metadata")

# Get next week expiration
print("\n2. Getting next week expiration...")
exp = get_next_week_expiration(ticker)
if exp:
    exp_date = dt.datetime.fromtimestamp(exp)
    print(f"   ✓ Next expiration: {exp_date.strftime('%Y-%m-%d (%A)')}")
    print(f"   ✓ Timestamp: {exp}")
else:
    print("   ✗ Failed to get next expiration")

# Load options chain
print("\n3. Loading options chain...")
chain = load_options_chain(ticker, exp)

if chain and chain.get("calls") is not None and chain.get("puts") is not None:
    calls = chain["calls"]
    puts = chain["puts"]
    
    print(f"   ✓ Loaded {len(calls)} call contracts")
    print(f"   ✓ Loaded {len(puts)} put contracts")
    
    # Show ATM options
    print("\n4. Near-the-money options:")
    
    # Get current price from calls (last is current spot price implied by options)
    if len(calls) > 0 and "lastPrice" in calls.columns:
        # Find ATM strike (where inTheMoney changes)
        itm_calls = calls[calls["inTheMoney"] == True]
        otm_calls = calls[calls["inTheMoney"] == False]
        
        if len(itm_calls) > 0 and len(otm_calls) > 0:
            atm_strike = otm_calls.iloc[0]["strike"]
            print(f"\n   Approximate current price: ~${atm_strike:.2f}")
        
        # Show 5 calls around ATM
        print("\n   CALLS (near ATM):")
        print("   Strike   Last    Bid     Ask     Volume  IV      ITM")
        print("   " + "-"*56)
        
        mid_idx = len(calls) // 2
        for i in range(max(0, mid_idx - 2), min(len(calls), mid_idx + 3)):
            row = calls.iloc[i]
            strike = row.get("strike", 0)
            last = row.get("lastPrice", 0)
            bid = row.get("bid", 0)
            ask = row.get("ask", 0)
            volume = row.get("volume", 0)
            iv = row.get("impliedVolatility", 0)
            itm = "✓" if row.get("inTheMoney", False) else ""
            
            print(f"   ${strike:<6.1f}  ${last:<6.2f} ${bid:<6.2f} ${ask:<6.2f} {volume:>6}  {iv:>5.2f}  {itm}")
        
        # Show 5 puts around ATM
        print("\n   PUTS (near ATM):")
        print("   Strike   Last    Bid     Ask     Volume  IV      ITM")
        print("   " + "-"*56)
        
        mid_idx = len(puts) // 2
        for i in range(max(0, mid_idx - 2), min(len(puts), mid_idx + 3)):
            row = puts.iloc[i]
            strike = row.get("strike", 0)
            last = row.get("lastPrice", 0)
            bid = row.get("bid", 0)
            ask = row.get("ask", 0)
            volume = row.get("volume", 0)
            iv = row.get("impliedVolatility", 0)
            itm = "✓" if row.get("inTheMoney", False) else ""
            
            print(f"   ${strike:<6.1f}  ${last:<6.2f} ${bid:<6.2f} ${ask:<6.2f} {volume:>6}  {iv:>5.2f}  {itm}")
    
    # Most active options
    print("\n5. Most active call options:")
    if "volume" in calls.columns:
        top_calls = calls.nlargest(3, "volume")
        print("   Strike   Volume   Last    IV")
        print("   " + "-"*40)
        for _, row in top_calls.iterrows():
            strike = row["strike"]
            volume = row.get("volume", 0)
            last = row.get("lastPrice", 0)
            iv = row.get("impliedVolatility", 0)
            print(f"   ${strike:<6.1f}  {volume:>6}   ${last:<6.2f} {iv:>5.2f}")
    
    print("\n6. Most active put options:")
    if "volume" in puts.columns:
        top_puts = puts.nlargest(3, "volume")
        print("   Strike   Volume   Last    IV")
        print("   " + "-"*40)
        for _, row in top_puts.iterrows():
            strike = row["strike"]
            volume = row.get("volume", 0)
            last = row.get("lastPrice", 0)
            iv = row.get("impliedVolatility", 0)
            print(f"   ${strike:<6.1f}  {volume:>6}   ${last:<6.2f} {iv:>5.2f}")
    
    print("\n" + "="*60)
    print("✓ OPTIONS CHAIN TEST COMPLETE")
    print("="*60)
    
else:
    print("   ✗ Failed to load options chain")
    print("\n" + "="*60)
    print("✗ TEST FAILED")
    print("="*60)
