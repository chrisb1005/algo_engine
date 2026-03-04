"""
Stock Scanner - Find optimal stocks for weekly options trading
"""

import sys
if sys.platform == "win32":
    try:
        import io
        if sys.stdout.encoding != 'utf-8':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

from core.data import load_history, get_price_stats
from core.indicators import compute_indicators
from core.signals import generate_signal
from core.strategies import decide_action
from core.contracts import load_options_chain_metadata, load_options_chain, get_next_week_expiration
import time


# Popular stocks good for options trading
POPULAR_TICKERS = [
    # Tech Giants
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "AMD", "INTC",
    
    # Finance
    "JPM", "BAC", "WFC", "GS", "MS", "C",
    
    # Consumer
    "WMT", "HD", "DIS", "NKE", "SBUX", "MCD",
    
    # Healthcare
    "JNJ", "UNH", "PFE", "ABBV", "TMO",
    
    # Energy
    "XOM", "CVX", "COP", "SLB",
    
    # ETFs
    "SPY", "QQQ", "IWM", "DIA",
    
    # Communication
    "T", "VZ", "NFLX",
    
    # Others
    "BA", "CAT", "GE", "F", "GM", "AAL", "DAL"
]


def scan_stock_for_options(ticker, min_price=10, max_price=30, verbose=False):
    """
    Scan a single stock for weekly options trading opportunities
    
    Args:
        ticker: Stock symbol
        min_price: Minimum option price
        max_price: Maximum option price
        verbose: Print detailed info
    
    Returns:
        Dict with scoring info or None if not suitable
    """
    try:
        if verbose:
            print(f"  Scanning {ticker}...")
        
        # Get basic data
        df = load_history(ticker, days=60, use_cache=True)
        if df is None or len(df) < 30:
            return None
        
        # Get price stats
        stats = get_price_stats(ticker, days=30)
        if not stats:
            return None
        
        current_price = stats['current_price']
        volatility = stats['volatility']
        avg_volume = stats['avg_volume']
        
        # Check if stock is liquid enough (volume)
        if avg_volume < 1_000_000:  # Less than 1M volume/day
            return None
        
        # Get options data
        exp = get_next_week_expiration(ticker)
        if not exp:
            return None
        
        chain = load_options_chain(ticker, exp)
        if not chain or chain.get('calls') is None or len(chain['calls']) == 0:
            return None
        
        calls = chain['calls']
        puts = chain['puts']
        
        # Find options in price range
        affordable_calls = calls[
            (calls['lastPrice'] >= min_price) & 
            (calls['lastPrice'] <= max_price) &
            (calls['volume'] > 100)  # Good volume
        ]
        
        affordable_puts = puts[
            (puts['lastPrice'] >= min_price) & 
            (puts['lastPrice'] <= max_price) &
            (puts['volume'] > 100)
        ]
        
        if len(affordable_calls) == 0 and len(affordable_puts) == 0:
            return None
        
        # Calculate scores
        # Volatility score (sweet spot: 0.01-0.03 daily)
        if volatility < 0.005:
            vol_score = 1  # Too low
        elif volatility > 0.05:
            vol_score = 2  # Too high
        else:
            vol_score = 5  # Good range
        
        # Volume score
        if avg_volume > 10_000_000:
            volume_score = 5
        elif avg_volume > 5_000_000:
            volume_score = 4
        elif avg_volume > 2_000_000:
            volume_score = 3
        else:
            volume_score = 2
        
        # Options availability score
        options_score = min(5, len(affordable_calls) + len(affordable_puts))
        
        # Get technical signal
        df = compute_indicators(df)
        df_clean = df.dropna()
        
        if len(df_clean) > 0:
            sig = generate_signal(df_clean)
            action = decide_action(sig)
            has_signal = action != "NO_TRADE"
        else:
            action = "NO_TRADE"
            has_signal = False
        
        # Total score
        total_score = vol_score + volume_score + options_score
        if has_signal:
            total_score += 2  # Bonus for having a clear signal
        
        # Find best affordable option
        best_call = None
        if len(affordable_calls) > 0:
            best_call = affordable_calls.nlargest(1, 'volume').iloc[0]
        
        best_put = None
        if len(affordable_puts) > 0:
            best_put = affordable_puts.nlargest(1, 'volume').iloc[0]
        
        return {
            'ticker': ticker,
            'score': total_score,
            'current_price': current_price,
            'volatility': volatility,
            'avg_volume': avg_volume,
            'affordable_calls': len(affordable_calls),
            'affordable_puts': len(affordable_puts),
            'action': action,
            'has_signal': has_signal,
            'best_call': {
                'strike': best_call['strike'] if best_call is not None else None,
                'price': best_call['lastPrice'] if best_call is not None else None,
                'volume': best_call['volume'] if best_call is not None else None,
            } if best_call is not None else None,
            'best_put': {
                'strike': best_put['strike'] if best_put is not None else None,
                'price': best_put['lastPrice'] if best_put is not None else None,
                'volume': best_put['volume'] if best_put is not None else None,
            } if best_put is not None else None,
        }
        
    except Exception as e:
        if verbose:
            print(f"    Error scanning {ticker}: {e}")
        return None


def scan_market(tickers=None, min_price=10, max_price=30, top_n=10, progress_callback=None):
    """
    Scan multiple stocks for options trading opportunities
    
    Args:
        tickers: List of tickers to scan (default: POPULAR_TICKERS)
        min_price: Minimum option price
        max_price: Maximum option price
        top_n: Number of top results to return
        progress_callback: Function to call with progress updates (current, total)
    
    Returns:
        List of dicts with top stocks sorted by score
    """
    if tickers is None:
        tickers = POPULAR_TICKERS
    
    results = []
    total = len(tickers)
    
    for i, ticker in enumerate(tickers):
        if progress_callback:
            progress_callback(i + 1, total)
        
        result = scan_stock_for_options(ticker, min_price, max_price, verbose=False)
        
        if result:
            results.append(result)
        
        # Small delay to avoid rate limiting
        if i < total - 1:  # Don't delay after last ticker
            time.sleep(0.1)
    
    # Sort by score (descending)
    results.sort(key=lambda x: x['score'], reverse=True)
    
    return results[:top_n]


def get_quick_recommendations(count=5):
    """
    Quick scan of most popular tickers for fast results
    
    Args:
        count: Number of recommendations to return
    
    Returns:
        List of recommended tickers with info
    """
    # Scan top liquid stocks first
    quick_tickers = ["SPY", "QQQ", "AAPL", "MSFT", "TSLA", "AMD", "NVDA", "AMZN", "META", "GOOGL"]
    
    return scan_market(quick_tickers, min_price=10, max_price=30, top_n=count)
