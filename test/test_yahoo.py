import requests

# Test Yahoo Finance API
ticker = "AAPL"
days = 60

print(f"Testing Yahoo Finance for {ticker}...")

try:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range={days}d&interval=1d"
    print(f"URL: {url}")
    
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    
    r = requests.get(url, headers=headers, timeout=10)
    print(f"Status code: {r.status_code}")
    
    data = r.json()
    print(f"Response keys: {list(data.keys())}")
    
    if "chart" in data:
        print(f"Chart keys: {list(data['chart'].keys())}")
        if "result" in data["chart"] and data["chart"]["result"]:
            result = data["chart"]["result"][0]
            print(f"Result keys: {list(result.keys())}")
            if "timestamp" in result:
                print(f"Number of timestamps: {len(result['timestamp'])}")
            print("✓ Yahoo Finance API is working!")
            
            print("\n" + "="*60)
            print("FULL CHART DATA:")
            print("="*60)
            import json
            print(json.dumps(data, indent=2))
        else:
            print(f"Error in response: {data['chart'].get('error')}")
            print(f"Full chart response: {data['chart']}")
    
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
