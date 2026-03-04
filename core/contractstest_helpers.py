from contracts import (
    load_options_chain, 
    get_next_week_expiration,
    find_atm_options,
    find_best_option,
    get_contract_symbol
)

ticker = "AAPL"

print("="*60)
print(f"HELPER FUNCTIONS TEST - {ticker}")
print("="*60)

# Load chain
exp = get_next_week_expiration(ticker)
chain = load_options_chain(ticker, exp)

if not chain:
    print("✗ Failed to load options chain")
    exit(1)

# Test 1: Find ATM options
print("\n1. Finding ATM options...")
atm = find_atm_options(chain, strike_range=3)

if atm:
    print(f"   ✓ ATM Strike: ${atm['atm_strike']:.2f}")
    print(f"   ✓ Found {len(atm['calls'])} calls near ATM")
    print(f"   ✓ Found {len(atm['puts'])} puts near ATM")
    
    print("\n   ATM Calls:")
    for _, row in atm['calls'].head(3).iterrows():
        symbol = row['contractSymbol']
        strike = row['strike']
        last = row.get('lastPrice', 0)
        volume = row.get('volume', 0)
        print(f"     {symbol}: ${strike} @ ${last:.2f} (Vol: {volume})")
else:
    print("   ✗ Failed to find ATM options")

# Test 2: Find best call by volume
print("\n2. Finding most active call option...")
best_call = find_best_option(chain, option_type="call", criteria="volume")

if best_call is not None and len(best_call) > 0:
    symbol = get_contract_symbol(best_call)
    strike = best_call.iloc[0]['strike']
    volume = best_call.iloc[0].get('volume', 0)
    last = best_call.iloc[0].get('lastPrice', 0)
    iv = best_call.iloc[0].get('impliedVolatility', 0)
    
    print(f"   ✓ Contract: {symbol}")
    print(f"   ✓ Strike: ${strike:.2f}")
    print(f"   ✓ Last Price: ${last:.2f}")
    print(f"   ✓ Volume: {volume}")
    print(f"   ✓ IV: {iv:.2%}")
else:
    print("   ✗ Failed to find best call")

# Test 3: Find best put by volume
print("\n3. Finding most active put option...")
best_put = find_best_option(chain, option_type="put", criteria="volume")

if best_put is not None and len(best_put) > 0:
    symbol = get_contract_symbol(best_put)
    strike = best_put.iloc[0]['strike']
    volume = best_put.iloc[0].get('volume', 0)
    last = best_put.iloc[0].get('lastPrice', 0)
    iv = best_put.iloc[0].get('impliedVolatility', 0)
    
    print(f"   ✓ Contract: {symbol}")
    print(f"   ✓ Strike: ${strike:.2f}")
    print(f"   ✓ Last Price: ${last:.2f}")
    print(f"   ✓ Volume: {volume}")
    print(f"   ✓ IV: {iv:.2%}")
else:
    print("   ✗ Failed to find best put")

# Test 4: Find OTM call with volume
print("\n4. Finding OTM call with volume...")
otm_call = find_best_option(chain, option_type="call", criteria="otm")

if otm_call is not None and len(otm_call) > 0:
    symbol = get_contract_symbol(otm_call)
    strike = otm_call.iloc[0]['strike']
    volume = otm_call.iloc[0].get('volume', 0)
    last = otm_call.iloc[0].get('lastPrice', 0)
    itm = otm_call.iloc[0].get('inTheMoney', False)
    
    print(f"   ✓ Contract: {symbol}")
    print(f"   ✓ Strike: ${strike:.2f}")
    print(f"   ✓ Last Price: ${last:.2f}")
    print(f"   ✓ Volume: {volume}")
    print(f"   ✓ In The Money: {itm}")
else:
    print("   ✗ Failed to find OTM call")

# Test 5: Find OTM put with volume
print("\n5. Finding OTM put with volume...")
otm_put = find_best_option(chain, option_type="put", criteria="otm")

if otm_put is not None and len(otm_put) > 0:
    symbol = get_contract_symbol(otm_put)
    strike = otm_put.iloc[0]['strike']
    volume = otm_put.iloc[0].get('volume', 0)
    last = otm_put.iloc[0].get('lastPrice', 0)
    itm = otm_put.iloc[0].get('inTheMoney', False)
    
    print(f"   ✓ Contract: {symbol}")
    print(f"   ✓ Strike: ${strike:.2f}")
    print(f"   ✓ Last Price: ${last:.2f}")
    print(f"   ✓ Volume: {volume}")
    print(f"   ✓ In The Money: {itm}")
else:
    print("   ✗ Failed to find OTM put")

# Test 6: Find highest IV options
print("\n6. Finding highest IV options...")
high_iv_call = find_best_option(chain, option_type="call", criteria="iv")
high_iv_put = find_best_option(chain, option_type="put", criteria="iv")

if high_iv_call is not None and len(high_iv_call) > 0:
    iv = high_iv_call.iloc[0].get('impliedVolatility', 0)
    strike = high_iv_call.iloc[0]['strike']
    print(f"   ✓ Highest IV Call: ${strike:.2f} strike with IV={iv:.2%}")
    
if high_iv_put is not None and len(high_iv_put) > 0:
    iv = high_iv_put.iloc[0].get('impliedVolatility', 0)
    strike = high_iv_put.iloc[0]['strike']
    print(f"   ✓ Highest IV Put: ${strike:.2f} strike with IV={iv:.2%}")

print("\n" + "="*60)
print("✓ HELPER FUNCTIONS TEST COMPLETE")
print("="*60)
