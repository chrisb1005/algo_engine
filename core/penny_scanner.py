"""
Penny Stock Scanner - Find high-volume penny stock movers
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

from core.data import load_history, get_current_price, get_price_stats
from core.indicators import compute_indicators
import pandas as pd
import time


# Popular penny stocks and small caps (under $10)
PENNY_STOCK_TICKERS = [
    # Sub $5
    "SNDL", "PLUG", "NIO", "SOFI", "WISH", "TLRY", "ACB", "CGC",
    "CLOV", "BB", "NOK", "PLTR", "SNAP", "RIVN", "LCID", "AMC",
    "HOOD", "SPCE", "COIN", "RBLX", "DKNG", "FUBO", "OPEN",
    
    # Small caps with movement
    "RIOT", "MARA", "CLNE", "WKHS", "RIDE", "GOEV", "FSR",
    "HYLN", "QS", "CHPT", "BLNK", "SKLZ", "BARK", "BODY",
    
    # Volatile microcaps
    "GNUS", "EXPR", "KOSS", "BBBY", "SIRI", "F", "INTC",
    "AAL", "CCL", "NCLH", "UAL", "DAL", "LUV", "JBLU"
]


def scan_penny_stock(ticker, min_price=0.50, max_price=10.0, min_volume=1_000_000, verbose=False):
    """
    Scan a single penny stock for movement and opportunity
    
    Args:
        ticker: Stock symbol
        min_price: Minimum stock price to consider
        max_price: Maximum price for penny stock (default $10)
        min_volume: Minimum daily volume required
        verbose: Print progress
        
    Returns:
        Dictionary with stock data and scores, or None if doesn't qualify
    """
    if verbose:
        print(f"  Scanning {ticker}...")
    
    try:
        # Load recent data (30 days)
        df = load_history(ticker, days=30)
        if df is None or len(df) < 5:
            if verbose:
                print(f"    ✗ Not enough data")
            return None
        
        # Get current price and stats
        current_price = df['Close'].iloc[-1]
        
        # Check price range
        if current_price < min_price or current_price > max_price:
            if verbose:
                print(f"    ✗ Price ${current_price:.2f} outside range ${min_price}-${max_price}")
            return None
        
        # Calculate stats directly from DataFrame
        avg_volume = df['Volume'].mean()
        returns = df['Close'].pct_change().dropna()
        volatility = returns.std()
        high_52w = df['High'].max()
        low_52w = df['Low'].min()
        
        # Check volume
        if avg_volume < min_volume:
            if verbose:
                print(f"    ✗ Volume {avg_volume:,.0f} below minimum {min_volume:,}")
            return None
        
        # Calculate movement metrics
        price_1d_ago = df['Close'].iloc[-2] if len(df) >= 2 else current_price
        price_5d_ago = df['Close'].iloc[-6] if len(df) >= 6 else current_price
        price_20d_ago = df['Close'].iloc[-21] if len(df) >= 21 else current_price
        
        change_1d = ((current_price - price_1d_ago) / price_1d_ago * 100) if price_1d_ago > 0 else 0
        change_5d = ((current_price - price_5d_ago) / price_5d_ago * 100) if price_5d_ago > 0 else 0
        change_20d = ((current_price - price_20d_ago) / price_20d_ago * 100) if price_20d_ago > 0 else 0
        
        # Calculate volatility (for scoring)
        # volatility already calculated above
        
        # Volume surge detection
        recent_volume = df['Volume'].iloc[-1]
        volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1.0
        
        # Momentum score (0-5)
        momentum_score = 0
        if abs(change_1d) > 10:
            momentum_score += 2
        elif abs(change_1d) > 5:
            momentum_score += 1
            
        if abs(change_5d) > 20:
            momentum_score += 2
        elif abs(change_5d) > 10:
            momentum_score += 1
            
        if abs(change_20d) > 50:
            momentum_score += 1
        
        # Volume score (0-5)
        volume_score = 0
        if volume_ratio > 3.0:
            volume_score = 5
        elif volume_ratio > 2.0:
            volume_score = 4
        elif volume_ratio > 1.5:
            volume_score = 3
        elif volume_ratio > 1.2:
            volume_score = 2
        elif volume_ratio > 1.0:
            volume_score = 1
        
        # Volatility score (0-5) - higher is more interesting for penny stocks
        vol_score = 0
        if volatility > 0.05:  # >5% daily volatility
            vol_score = 5
        elif volatility > 0.04:
            vol_score = 4
        elif volatility > 0.03:
            vol_score = 3
        elif volatility > 0.02:
            vol_score = 2
        elif volatility > 0.01:
            vol_score = 1
        
        # Total score
        total_score = momentum_score + volume_score + vol_score
        
        # Determine trend
        if change_5d > 5:
            trend = "STRONG_UP"
        elif change_5d > 2:
            trend = "UP"
        elif change_5d < -5:
            trend = "STRONG_DOWN"
        elif change_5d < -2:
            trend = "DOWN"
        else:
            trend = "SIDEWAYS"
        
        result = {
            'ticker': ticker,
            'score': total_score,
            'current_price': current_price,
            'change_1d': change_1d,
            'change_5d': change_5d,
            'change_20d': change_20d,
            'volume': recent_volume,
            'avg_volume': avg_volume,
            'volume_ratio': volume_ratio,
            'volatility': volatility,
            'trend': trend,
            'high_52w': high_52w,
            'low_52w': low_52w
        }
        
        if verbose:
            print(f"    ✓ Score: {total_score}/15, Price: ${current_price:.2f}, 5d: {change_5d:+.1f}%")
        
        return result
        
    except Exception as e:
        if verbose:
            print(f"    ✗ Error: {str(e)}")
        return None


def scan_penny_movers(tickers=None, min_price=0.50, max_price=10.0, min_volume=1_000_000, 
                      top_n=10, sort_by="score", progress_callback=None):
    """
    Scan multiple penny stocks and find the top movers
    
    Args:
        tickers: List of tickers to scan (uses PENNY_STOCK_TICKERS if None)
        min_price: Minimum stock price
        max_price: Maximum stock price
        min_volume: Minimum daily volume
        top_n: Number of top results to return
        sort_by: How to sort results ("score", "change_1d", "change_5d", "volume_ratio")
        progress_callback: Optional function(current, total) for progress updates
        
    Returns:
        List of stock dictionaries sorted by criteria
    """
    if tickers is None:
        tickers = PENNY_STOCK_TICKERS
    
    results = []
    total = len(tickers)
    
    for i, ticker in enumerate(tickers):
        if progress_callback:
            progress_callback(i + 1, total)
        
        result = scan_penny_stock(ticker, min_price, max_price, min_volume)
        if result:
            results.append(result)
        
        # Rate limiting
        time.sleep(0.1)
    
    # Sort results
    if sort_by == "score":
        results.sort(key=lambda x: x['score'], reverse=True)
    elif sort_by == "change_1d":
        results.sort(key=lambda x: abs(x['change_1d']), reverse=True)
    elif sort_by == "change_5d":
        results.sort(key=lambda x: abs(x['change_5d']), reverse=True)
    elif sort_by == "change_20d":
        results.sort(key=lambda x: abs(x['change_20d']), reverse=True)
    elif sort_by == "volume_ratio":
        results.sort(key=lambda x: x['volume_ratio'], reverse=True)
    
    return results[:top_n]


def get_stock_due_diligence(ticker):
    """
    Perform due diligence analysis on a stock
    
    Returns comprehensive data for DD analysis
    """
    try:
        # Load 3 months of data for better analysis
        df = load_history(ticker, days=90)
        if df is None or len(df) < 20:
            return {"error": "Insufficient data for analysis"}
        
        # Basic price info
        current_price = df['Close'].iloc[-1]
        
        # Calculate stats directly from DataFrame
        avg_volume = df['Volume'].mean()
        returns = df['Close'].pct_change().dropna()
        volatility = returns.std()
        high_52w = df['High'].max()
        low_52w = df['Low'].min()
        
        # Calculate price changes over different periods
        price_changes = {}
        periods = {
            '1d': -2,
            '5d': -6,
            '10d': -11,
            '20d': -21,
            '30d': -31,
            '60d': -61
        }
        
        for period_name, days_ago in periods.items():
            if len(df) >= abs(days_ago):
                old_price = df['Close'].iloc[days_ago]
                change_pct = ((current_price - old_price) / old_price * 100) if old_price > 0 else 0
                price_changes[period_name] = {
                    'change_pct': change_pct,
                    'old_price': old_price
                }
        
        # Technical indicators
        df_with_indicators = compute_indicators(df)
        
        # Extract indicator values (use last valid value)
        rsi = df_with_indicators['RSI'].iloc[-1] if not pd.isna(df_with_indicators['RSI'].iloc[-1]) else 50
        ma20 = df_with_indicators['MA20'].iloc[-1] if not pd.isna(df_with_indicators['MA20'].iloc[-1]) else current_price
        ma50 = df_with_indicators['MA50'].iloc[-1] if not pd.isna(df_with_indicators['MA50'].iloc[-1]) else current_price
        momentum = df_with_indicators['Momentum'].iloc[-1] if not pd.isna(df_with_indicators['Momentum'].iloc[-1]) else 0
        
        # Volume analysis
        recent_volume = df['Volume'].iloc[-1]
        avg_volume_5d = df['Volume'].iloc[-5:].mean()
        avg_volume_20d = df['Volume'].iloc[-20:].mean()
        volume_trend = "INCREASING" if avg_volume_5d > avg_volume_20d * 1.2 else \
                      "DECREASING" if avg_volume_5d < avg_volume_20d * 0.8 else "STABLE"
        
        # Price levels
        resistance_levels = []
        support_levels = []
        
        # Simple support/resistance using recent highs/lows
        recent_high = df['High'].iloc[-20:].max()
        recent_low = df['Low'].iloc[-20:].min()
        
        if recent_high > current_price * 1.05:
            resistance_levels.append(recent_high)
        if recent_low < current_price * 0.95:
            support_levels.append(recent_low)
        
        # Risk assessment
        risk_factors = []
        
        if current_price < 1.0:
            risk_factors.append("⚠️ Ultra-low price (<$1) - extreme volatility risk")
        elif current_price < 5.0:
            risk_factors.append("⚠️ Penny stock - higher risk of delisting/manipulation")
        
        if volatility > 0.05:
            risk_factors.append("⚠️ Very high volatility (>5%/day) - significant price swings")
        
        if avg_volume < 500_000:
            risk_factors.append("⚠️ Low liquidity - may be hard to enter/exit positions")
        
        # Price relative to 52-week range
        price_position = ((current_price - low_52w) / 
                         (high_52w - low_52w) * 100) if high_52w > low_52w else 50
        
        if price_position < 20:
            risk_factors.append("📊 Trading near 52-week lows")
        elif price_position > 80:
            risk_factors.append("📊 Trading near 52-week highs")
        
        # Opportunity signals
        opportunities = []
        
        if rsi < 30:
            opportunities.append("🟢 Oversold (RSI < 30) - potential bounce candidate")
        elif rsi > 70:
            opportunities.append("🔴 Overbought (RSI > 70) - potential pullback risk")
        
        if price_changes.get('5d', {}).get('change_pct', 0) > 20:
            opportunities.append("🚀 Strong upward momentum (+20% in 5 days)")
        elif price_changes.get('5d', {}).get('change_pct', 0) < -20:
            opportunities.append("📉 Sharp decline (-20% in 5 days) - reversal watch")
        
        if recent_volume > avg_volume * 2:
            opportunities.append("📊 Volume surge (2x+ average) - increased interest")
        
        return {
            'ticker': ticker,
            'current_price': current_price,
            'price_changes': price_changes,
            'volume': {
                'current': recent_volume,
                'avg_5d': avg_volume_5d,
                'avg_20d': avg_volume_20d,
                'avg_overall': avg_volume,
                'trend': volume_trend
            },
            'technicals': {
                'rsi': rsi,
                'ma20': ma20,
                'ma50': ma50,
                'momentum': momentum,
                'volatility': volatility
            },
            'price_levels': {
                'high_52w': high_52w,
                'low_52w': low_52w,
                'position_in_range': price_position,
                'resistance': resistance_levels,
                'support': support_levels
            },
            'risk_factors': risk_factors,
            'opportunities': opportunities,
            'data': df  # Full dataframe for charting
        }
        
    except Exception as e:
        return {"error": f"DD analysis failed: {str(e)}"}


def get_quick_penny_movers(count=10):
    """Quick scan of most popular penny stocks"""
    quick_list = [
        "SNDL", "PLUG", "NIO", "SOFI", "PLTR", "AMC", "BB", "NOK",
        "RIOT", "MARA", "LCID", "RIVN", "F", "AAL", "CCL"
    ]
    return scan_penny_movers(tickers=quick_list, top_n=count, sort_by="score")
