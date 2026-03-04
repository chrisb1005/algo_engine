import requests

# Test different Yahoo Finance endpoints and headers
ticker = "AAPL"

print("Testing Yahoo Finance Options API...")
print("="*60)

# Test 1: Basic options endpoint
print("\nTest 1: Basic options endpoint")
url1 = f"https://query2.finance.yahoo.com/v7/finance/options/{ticker}"
headers1 = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
r1 = requests.get(url1, headers=headers1, timeout=10)
print(f"Status: {r1.status_code}")
if r1.status_code == 200:
    print("✓ Works!")
else:
    print(f"✗ Failed: {r1.text[:200]}")

# Test 2: Enhanced headers
print("\nTest 2: Enhanced headers")
headers2 = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://finance.yahoo.com/",
    "Origin": "https://finance.yahoo.com"
}
r2 = requests.get(url1, headers=headers2, timeout=10)
print(f"Status: {r2.status_code}")
if r2.status_code == 200:
    print("✓ Works!")
    data = r2.json()
    if "optionChain" in data:
        result = data["optionChain"]["result"]
        if result and len(result) > 0:
            exps = result[0].get("expirationDates", [])
            print(f"Found {len(exps)} expirations")
else:
    print(f"✗ Failed")

# Test 3: Query1 endpoint (sometimes works better)
print("\nTest 3: Query1 endpoint")
url3 = f"https://query1.finance.yahoo.com/v7/finance/options/{ticker}"
r3 = requests.get(url3, headers=headers2, timeout=10)
print(f"Status: {r3.status_code}")
if r3.status_code == 200:
    print("✓ Works!")
else:
    print(f"✗ Failed")

print("\n" + "="*60)
