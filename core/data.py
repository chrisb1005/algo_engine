import requests
import pandas as pd
import datetime as dt
from functools import lru_cache
import time
import sys

# Fix Windows console encoding for Unicode characters
if sys.platform == "win32":
    try:
        import io
        if sys.stdout.encoding != 'utf-8':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass  # Silently fail if we can't fix encoding

POLYGON_API_KEY = "IoZ5ptZq2FEmG3in0M8DOpSYEBBgsl2B"

# Cache for storing recent data requests (ticker -> (timestamp, dataframe))
_data_cache = {}

# ---------------------------------------------------
# Load stock history (Polygon → Yahoo fallback)
# ---------------------------------------------------
def load_history(ticker, days=60, use_cache=True):
    """
    Load historical stock data with automatic fallback
    
    Args:
        ticker: Stock symbol (e.g., 'AAPL')
        days: Number of days of history
        use_cache: Whether to use cached data (cache valid for 5 minutes)
    
    Returns:
        DataFrame with OHLCV data, or None if failed
    """
    # Check cache first
    if use_cache and ticker in _data_cache:
        cache_time, cached_df = _data_cache[ticker]
        # Cache valid for 5 minutes
        if time.time() - cache_time < 300:
            return cached_df.copy()
    
    # Try Polygon first
    df = get_polygon_history(ticker, days)
    if df is not None and validate_data(df, ticker, days):
        _data_cache[ticker] = (time.time(), df)
        return df

    # Fallback to Yahoo JSON API
    print(f"Falling back to Yahoo Finance for {ticker}...")
    df = get_yahoo_history(ticker, days)
    
    if df is not None and validate_data(df, ticker, days):
        _data_cache[ticker] = (time.time(), df)
        return df
    
    return None


# ---------------------------------------------------
# Polygon Aggregates (daily candles)
# ---------------------------------------------------
def get_polygon_history(ticker, days=60):
    try:
        end = dt.datetime.now()
        start = end - dt.timedelta(days=days)

        url = (
            f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/"
            f"{start.strftime('%Y-%m-%d')}/{end.strftime('%Y-%m-%d')}"
            f"?adjusted=true&sort=asc&apiKey={POLYGON_API_KEY}"
        )

        r = requests.get(url, timeout=10)
        data = r.json()

        if "results" not in data:
            if "error" in data:
                print(f"Polygon API error for {ticker}: {data['error']}")
            else:
                print(f"Polygon API: No results for {ticker} (status: {data.get('status')})")
            return None

        rows = data["results"]
        df = pd.DataFrame(rows)

        df["Date"] = pd.to_datetime(df["t"], unit="ms")
        df = df.rename(columns={"o": "Open", "h": "High", "l": "Low",
                                "c": "Close", "v": "Volume"})
        df = df[["Date", "Open", "High", "Low", "Close", "Volume"]]
        df.set_index("Date", inplace=True)

        return df

    except Exception as e:
        print(f"Polygon API exception for {ticker}: {type(e).__name__}: {e}")
        return None


# ---------------------------------------------------
# Yahoo Finance JSON history fallback
# ---------------------------------------------------
def get_yahoo_history(ticker, days=60):
    try:
        period = days
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range={period}d&interval=1d"
        
        # Add User-Agent header (Yahoo may block requests without it)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()
        
        # Check for errors in response
        if "chart" not in data:
            print(f"Yahoo Finance error: No 'chart' in response for {ticker}")
            return None
            
        if data["chart"].get("error"):
            print(f"Yahoo Finance error for {ticker}: {data['chart']['error']}")
            return None
            
        if not data["chart"]["result"]:
            print(f"Yahoo Finance error: Empty result for {ticker}")
            return None

        result = data["chart"]["result"][0]
        ts = result["timestamp"]
        indicators = result["indicators"]["quote"][0]

        df = pd.DataFrame(indicators)
        df["Date"] = pd.to_datetime(ts, unit="s")
        df.set_index("Date", inplace=True)

        df.rename(columns={
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume"
        }, inplace=True)

        return df

    except Exception as e:
        print(f"Yahoo Finance exception for {ticker}: {type(e).__name__}: {e}")
        return None


# ---------------------------------------------------
# Validate data quality
# ---------------------------------------------------
def validate_data(df, ticker, expected_days=None):
    """
    Validate that the data meets quality standards
    
    Args:
        df: DataFrame to validate
        ticker: Stock symbol for error messages
        expected_days: Expected number of days (optional)
    
    Returns:
        True if valid, False otherwise
    """
    if df is None or len(df) == 0:
        print(f"Validation failed for {ticker}: Empty DataFrame")
        return False
    
    required_columns = ["Open", "High", "Low", "Close", "Volume"]
    missing_cols = [col for col in required_columns if col not in df.columns]
    
    if missing_cols:
        print(f"Validation failed for {ticker}: Missing columns {missing_cols}")
        return False
    
    # Check for too many NaN values
    null_pct = (df[required_columns].isnull().sum() / len(df)).max()
    if null_pct > 0.5:
        print(f"Validation warning for {ticker}: {null_pct*100:.1f}% null values")
    
    # Check if we got enough data
    if expected_days and len(df) < expected_days * 0.5:
        print(f"Validation warning for {ticker}: Only got {len(df)} rows, expected ~{expected_days}")
    
    # Check for obviously bad prices (negative or zero)
    if (df["Close"] <= 0).any():
        print(f"Validation failed for {ticker}: Invalid prices detected")
        return False
    
    return True


# ---------------------------------------------------
# Get current/latest price
# ---------------------------------------------------
def get_current_price(ticker):
    """
    Get the most recent closing price for a ticker
    
    Args:
        ticker: Stock symbol
    
    Returns:
        Latest close price as float, or None if failed
    """
    df = load_history(ticker, days=5, use_cache=True)
    
    if df is not None and len(df) > 0:
        return float(df["Close"].iloc[-1])
    
    return None


# ---------------------------------------------------
# Get price change statistics
# ---------------------------------------------------
def get_price_stats(ticker, days=30):
    """
    Get price statistics for a ticker
    
    Args:
        ticker: Stock symbol
        days: Number of days to analyze
    
    Returns:
        Dict with statistics, or None if failed
    """
    df = load_history(ticker, days=days)
    
    if df is None or len(df) == 0:
        return None
    
    current = df["Close"].iloc[-1]
    high = df["High"].max()
    low = df["Low"].min()
    avg_volume = df["Volume"].mean()
    
    # Calculate returns
    returns = df["Close"].pct_change().dropna()
    
    return {
        "ticker": ticker,
        "current_price": current,
        "period_high": high,
        "period_low": low,
        "avg_volume": avg_volume,
        "volatility": returns.std(),
        "avg_return": returns.mean(),
        "total_return": (df["Close"].iloc[-1] / df["Close"].iloc[0] - 1),
        "data_points": len(df)
    }


# ---------------------------------------------------
# Clear data cache
# ---------------------------------------------------
def clear_cache():
    """Clear the data cache"""
    global _data_cache
    _data_cache = {}
    print("Data cache cleared")
