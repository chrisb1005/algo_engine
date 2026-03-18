import requests
import datetime as dt
import pandas as pd
import re
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


# Global session with cookies and crumb
_session = None
_crumb = None


# ---------------------------------------------------
# Initialize Yahoo session with crumb token
# ---------------------------------------------------
def init_yahoo_session():
    """
    Initialize a session with Yahoo Finance and get crumb token
    """
    global _session, _crumb
    
    if _session is not None and _crumb is not None:
        return True
    
    try:
        _session = requests.Session()
        _session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/json",
            "Accept-Language": "en-US,en;q=0.9",
        })
        
        # Get cookies by visiting Yahoo Finance homepage
        response = _session.get("https://finance.yahoo.com/quote/AAPL/options", timeout=10)
        
        if response.status_code != 200:
            print(f"Failed to initialize Yahoo session: {response.status_code}")
            return False
        
        # Try to extract crumb from page
        crumb_match = re.search(r'"crumb":"([^"]+)"', response.text)
        if crumb_match:
            _crumb = crumb_match.group(1)
            print(f"✓ Yahoo session initialized with crumb")
            return True
        else:
            print("Warning: Could not find crumb token, will try without it")
            _crumb = ""
            return True
            
    except Exception as e:
        print(f"Failed to initialize Yahoo session: {e}")
        return False


# ---------------------------------------------------
# Base Yahoo API request wrapper (reliable)
# ---------------------------------------------------
def yahoo_get(url):
    global _session, _crumb
    
    # Initialize session if needed
    if _session is None:
        if not init_yahoo_session():
            return None
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://finance.yahoo.com/"
    }
    
    try:
        # Add crumb to URL if we have one
        if _crumb and "?" in url:
            url = f"{url}&crumb={_crumb}"
        elif _crumb:
            url = f"{url}?crumb={_crumb}"
        
        r = _session.get(url, headers=headers, timeout=10)
        
        if r.status_code != 200:
            print(f"Yahoo API error: HTTP {r.status_code}")
            if r.status_code == 401:
                print("  Hint: Yahoo Finance may be blocking automated requests")
                print("  Consider using yfinance library: pip install yfinance")
            return None
            
        data = r.json()
        return data
        
    except requests.exceptions.Timeout:
        print(f"Yahoo API timeout")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Yahoo API request error: {e}")
        return None
    except ValueError as e:
        print(f"Yahoo API JSON parse error: {e}")
        return None


# ---------------------------------------------------
# Load option chain metadata (expirations only)
# ---------------------------------------------------
def load_options_chain_metadata(ticker):
    """
    Returns:
    {
        "expirations": [timestamp...]
    }
    """
    url = f"https://query2.finance.yahoo.com/v7/finance/options/{ticker}"
    data = yahoo_get(url)

    if not data or "optionChain" not in data:
        return None

    try:
        result = data["optionChain"]["result"][0]
        return {
            "expirations": result["expirationDates"]
        }
    except:
        return None


# ---------------------------------------------------
# Load calls/puts for a specific expiration
# ---------------------------------------------------
def load_options_chain(ticker, expiration_ts=None):
    """
    Returns calls + puts DataFrames for a specific expiration
    """

    # If no expiration provided → get first valid one
    meta = load_options_chain_metadata(ticker)
    if meta is None:
        return None

    expirations = meta["expirations"]

    if expiration_ts is None:
        expiration_ts = expirations[0]  # nearest weekly

    url = f"https://query2.finance.yahoo.com/v7/finance/options/{ticker}?date={expiration_ts}"
    data = yahoo_get(url)

    if not data or "optionChain" not in data:
        return None

    try:
        chain = data["optionChain"]["result"][0]["options"][0]

        df_calls = pd.DataFrame(chain.get("calls", []))
        df_puts  = pd.DataFrame(chain.get("puts", []))

        return {
            "expiration": expiration_ts,
            "calls": df_calls,
            "puts": df_puts,
            "expirations": expirations
        }

    except Exception as e:
        print("ERROR parsing options:", e)
        return None


# ---------------------------------------------------
# Pick the next weekly expiration (Friday)
# ---------------------------------------------------
def get_next_week_expiration(ticker):
    meta = load_options_chain_metadata(ticker)
    if meta is None:
        return None

    expirations = meta["expirations"]

    today = dt.datetime.now().timestamp()
    min_days_out = 3  # Minimum days in the future
    min_timestamp = today + (min_days_out * 24 * 60 * 60)

    # Filter for future expirations at least min_days_out away
    future_expirations = [exp for exp in expirations if exp >= min_timestamp]
    
    if not future_expirations:
        # Fallback to any future expiration if none meet min_days_out
        future_expirations = [exp for exp in expirations if exp > today]
    
    if not future_expirations:
        return None
    
    # Get the nearest future expiration
    nearest = min(future_expirations)

    return nearest


# ---------------------------------------------------
# Find near-the-money (ATM) options
# ---------------------------------------------------
def find_atm_options(chain, strike_range=5):
    """
    Find near-the-money call and put options
    
    Args:
        chain: Options chain dict with 'calls' and 'puts' DataFrames
        strike_range: Number of strikes above/below ATM to return
    
    Returns:
        dict with 'atm_strike', 'calls', 'puts'
    """
    if not chain or "calls" not in chain:
        return None
    
    calls = chain["calls"]
    
    # Find ATM strike (where inTheMoney changes)
    itm_calls = calls[calls["inTheMoney"] == True]
    otm_calls = calls[calls["inTheMoney"] == False]
    
    if len(otm_calls) == 0:
        return None
    
    atm_strike = otm_calls.iloc[0]["strike"]
    
    # Get options within strike_range of ATM
    atm_calls = calls[
        (calls["strike"] >= atm_strike - strike_range * 2.5) &
        (calls["strike"] <= atm_strike + strike_range * 2.5)
    ]
    
    puts = chain["puts"]
    atm_puts = puts[
        (puts["strike"] >= atm_strike - strike_range * 2.5) &
        (puts["strike"] <= atm_strike + strike_range * 2.5)
    ]
    
    return {
        "atm_strike": atm_strike,
        "calls": atm_calls,
        "puts": atm_puts
    }


# ---------------------------------------------------
# Find best option to trade based on criteria
# ---------------------------------------------------
def find_best_option(chain, option_type="call", criteria="volume"):
    """
    Find the best option to trade based on criteria
    
    Args:
        chain: Options chain dict
        option_type: "call" or "put"
        criteria: "volume" (most active), "iv" (highest IV), or "otm" (slightly out of money)
    
    Returns:
        Single row DataFrame with the best option
    """
    if not chain:
        return None
    
    df = chain["calls"] if option_type.lower() == "call" else chain["puts"]
    
    if len(df) == 0:
        return None
    
    if criteria == "volume":
        # Return highest volume option
        if "volume" in df.columns:
            return df.nlargest(1, "volume")
    
    elif criteria == "iv":
        # Return highest implied volatility
        if "impliedVolatility" in df.columns:
            return df.nlargest(1, "impliedVolatility")
    
    elif criteria == "otm":
        # Return first out-of-the-money option with good volume
        otm = df[df["inTheMoney"] == False]
        if len(otm) > 0 and "volume" in otm.columns:
            # Get OTM options with volume > 100
            liquid_otm = otm[otm["volume"] > 100]
            if len(liquid_otm) > 0:
                return liquid_otm.iloc[[0]]  # First OTM with volume
            return otm.iloc[[0]]  # Just return first OTM
    
    return None


# ---------------------------------------------------
# Get option contract symbol for trading
# ---------------------------------------------------
def get_contract_symbol(option_row):
    """
    Extract the contract symbol from an option row
    
    Args:
        option_row: Single row from calls/puts DataFrame
    
    Returns:
        Contract symbol string (e.g., "AAPL260209C00280000")
    """
    if option_row is None or len(option_row) == 0:
        return None
    
    if isinstance(option_row, pd.DataFrame):
        option_row = option_row.iloc[0]
    
    return option_row.get("contractSymbol", None)


# ---------------------------------------------------
# Choose a contract based on strategy action
# ---------------------------------------------------
def choose_contract(ticker, action):
    """
    Select the best option contract based on strategy action
    
    Args:
        ticker: Stock symbol
        action: Strategy action (BUY_CALL, BUY_PUT, SELL_CALL, SELL_PUT, NO_TRADE)
    
    Returns:
        Dict with contract details, or None if no suitable contract found
    """
    if action == "NO_TRADE":
        return None
    
    try:
        # Get next week's expiration
        exp = get_next_week_expiration(ticker)
        if exp is None:
            print(f"Could not find expiration for {ticker}")
            return None
        
        # Load options chain
        chain = load_options_chain(ticker, exp)
        if chain is None:
            print(f"Could not load options chain for {ticker}")
            return None
        
        # Determine option type and criteria
        if "CALL" in action:
            option_type = "call"
        elif "PUT" in action:
            option_type = "put"
        else:
            return None
        
        # For BUY actions, we want OTM options with volume
        # For SELL actions, we might want higher premium (closer to ATM)
        if "BUY" in action:
            criteria = "otm"
        else:
            criteria = "volume"
        
        # Find the best option
        best_option = find_best_option(chain, option_type=option_type, criteria=criteria)
        
        if best_option is None or len(best_option) == 0:
            print(f"Could not find suitable {option_type} for {action}")
            return None
        
        # Extract details
        row = best_option.iloc[0]
        
        exp_date = dt.datetime.fromtimestamp(exp)
        days_to_exp = (exp_date - dt.datetime.now()).days
        
        return {
            "symbol": row.get("contractSymbol", "N/A"),
            "strike": row.get("strike", 0),
            "last_price": row.get("lastPrice", 0),
            "bid": row.get("bid", 0),
            "ask": row.get("ask", 0),
            "volume": row.get("volume", 0),
            "open_interest": row.get("openInterest", 0),
            "implied_volatility": row.get("impliedVolatility", 0),
            "in_the_money": row.get("inTheMoney", False),
            "expiration": exp_date.strftime("%Y-%m-%d"),
            "days_to_expiration": days_to_exp,
            "option_type": option_type.upper(),
            "action": action
        }
        
    except Exception as e:
        print(f"Error choosing contract for {ticker}: {e}")
        return None

