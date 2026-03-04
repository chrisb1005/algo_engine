import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import numpy as np
from core.backtester import backtest
from core.indicators import compute_indicators
from core.signals import generate_signal
from core.strategies import decide_action


def create_mock_data(n_periods=100, trend="bullish", volatility="low"):
    """
    Create mock stock price data for testing
    
    Args:
        n_periods: Number of data points
        trend: "bullish", "bearish", or "sideways"
        volatility: "low", "medium", or "high"
    """
    np.random.seed(42)
    
    dates = pd.date_range(start='2025-01-01', periods=n_periods, freq='D')
    
    # Base price movement
    if trend == "bullish":
        base_prices = np.linspace(100, 150, n_periods)
    elif trend == "bearish":
        base_prices = np.linspace(150, 100, n_periods)
    else:  # sideways
        base_prices = np.ones(n_periods) * 125
    
    # Add volatility
    vol_factor = {"low": 0.5, "medium": 1.5, "high": 3.0}[volatility]
    noise = np.random.randn(n_periods) * vol_factor
    
    close_prices = base_prices + noise
    
    # Generate OHLV data
    df = pd.DataFrame({
        'Date': dates,
        'Open': close_prices * (1 + np.random.randn(n_periods) * 0.005),
        'High': close_prices * (1 + np.abs(np.random.randn(n_periods)) * 0.01),
        'Low': close_prices * (1 - np.abs(np.random.randn(n_periods)) * 0.01),
        'Close': close_prices,
        'Volume': np.random.randint(1000000, 10000000, n_periods)
    })
    
    df.set_index('Date', inplace=True)
    return df


def test_backtest_basic():
    """Test basic backtester functionality"""
    print("Test 1: Basic backtest functionality")
    
    df = create_mock_data(100, trend="bullish", volatility="low")
    trades = backtest(df)
    
    print(f"  ✓ Generated {len(trades)} trades")
    print(f"  ✓ Trades type: {type(trades)}")
    assert isinstance(trades, list), "Trades should be a list"
    print("  PASSED\n")


def test_backtest_bullish_market():
    """Test backtester in bullish market"""
    print("Test 2: Bullish market backtest")
    
    df = create_mock_data(150, trend="bullish", volatility="low")
    trades = backtest(df)
    
    print(f"  ✓ Number of trades: {len(trades)}")
    if trades:
        avg_pnl = sum(trades) / len(trades)
        total_pnl = sum(trades)
        winning_trades = len([t for t in trades if t > 0])
        print(f"  ✓ Total P&L: ${total_pnl:.2f}")
        print(f"  ✓ Average P&L: ${avg_pnl:.2f}")
        print(f"  ✓ Winning trades: {winning_trades}/{len(trades)}")
    else:
        print("  ✓ No trades executed")
    
    print("  PASSED\n")


def test_backtest_bearish_market():
    """Test backtester in bearish market"""
    print("Test 3: Bearish market backtest")
    
    df = create_mock_data(150, trend="bearish", volatility="low")
    trades = backtest(df)
    
    print(f"  ✓ Number of trades: {len(trades)}")
    if trades:
        avg_pnl = sum(trades) / len(trades)
        total_pnl = sum(trades)
        winning_trades = len([t for t in trades if t > 0])
        print(f"  ✓ Total P&L: ${total_pnl:.2f}")
        print(f"  ✓ Average P&L: ${avg_pnl:.2f}")
        print(f"  ✓ Winning trades: {winning_trades}/{len(trades)}")
    else:
        print("  ✓ No trades executed")
    
    print("  PASSED\n")


def test_backtest_sideways_market():
    """Test backtester in sideways market"""
    print("Test 4: Sideways market backtest")
    
    df = create_mock_data(150, trend="sideways", volatility="medium")
    trades = backtest(df)
    
    print(f"  ✓ Number of trades: {len(trades)}")
    if trades:
        avg_pnl = sum(trades) / len(trades)
        total_pnl = sum(trades)
        print(f"  ✓ Total P&L: ${total_pnl:.2f}")
        print(f"  ✓ Average P&L: ${avg_pnl:.2f}")
    else:
        print("  ✓ No trades executed")
    
    print("  PASSED\n")


def test_indicators():
    """Test indicator computation"""
    print("Test 5: Indicator computation")
    
    df = create_mock_data(100, trend="bullish", volatility="low")
    df_with_indicators = compute_indicators(df)
    
    # Check if indicators were added
    assert "MA20" in df_with_indicators.columns, "MA20 should be computed"
    assert "MA50" in df_with_indicators.columns, "MA50 should be computed"
    assert "RSI" in df_with_indicators.columns, "RSI should be computed"
    assert "Momentum" in df_with_indicators.columns, "Momentum should be computed"
    assert "Volatility" in df_with_indicators.columns, "Volatility should be computed"
    
    print("  ✓ MA20 computed")
    print("  ✓ MA50 computed")
    print("  ✓ RSI computed")
    print("  ✓ Momentum computed")
    print("  ✓ Volatility computed")
    
    # Check RSI bounds
    rsi_values = df_with_indicators["RSI"].dropna()
    assert all(rsi_values >= 0) and all(rsi_values <= 100), "RSI should be between 0 and 100"
    print(f"  ✓ RSI range: {rsi_values.min():.2f} - {rsi_values.max():.2f}")
    
    print("  PASSED\n")


def test_signal_generation():
    """Test signal generation"""
    print("Test 6: Signal generation")
    
    df = create_mock_data(100, trend="bullish", volatility="low")
    df = compute_indicators(df)
    df.dropna(inplace=True)
    
    signal = generate_signal(df)
    
    assert "trend" in signal, "Signal should have trend"
    assert "rsi" in signal, "Signal should have RSI"
    assert "vol" in signal, "Signal should have volatility"
    assert "momentum" in signal, "Signal should have momentum"
    
    print(f"  ✓ Trend: {signal['trend']}")
    print(f"  ✓ RSI: {signal['rsi']:.2f}")
    print(f"  ✓ Volatility: {signal['vol']:.4f}")
    print(f"  ✓ Momentum: {signal['momentum']:.4f}")
    
    print("  PASSED\n")


def test_strategy_decisions():
    """Test strategy decision making"""
    print("Test 7: Strategy decisions")
    
    # Test BUY_CALL scenario
    sig_buy_call = {"trend": "Bullish", "rsi": 50, "vol": 1.0, "momentum": 0.01}
    action = decide_action(sig_buy_call)
    print(f"  ✓ Bullish + RSI=50 → {action}")
    assert action == "BUY_CALL", "Should suggest BUY_CALL"
    
    # Test BUY_PUT scenario
    sig_buy_put = {"trend": "Bearish", "rsi": 50, "vol": 1.0, "momentum": -0.01}
    action = decide_action(sig_buy_put)
    print(f"  ✓ Bearish + RSI=50 → {action}")
    assert action == "BUY_PUT", "Should suggest BUY_PUT"
    
    # Test SELL_PUT scenario
    sig_sell_put = {"trend": "Bearish", "rsi": 25, "vol": 1.0, "momentum": -0.02}
    action = decide_action(sig_sell_put)
    print(f"  ✓ RSI=25 → {action}")
    assert action == "SELL_PUT", "Should suggest SELL_PUT"
    
    # Test SELL_CALL scenario
    sig_sell_call = {"trend": "Bullish", "rsi": 75, "vol": 1.0, "momentum": 0.02}
    action = decide_action(sig_sell_call)
    print(f"  ✓ RSI=75 → {action}")
    assert action == "SELL_CALL", "Should suggest SELL_CALL"
    
    # Test NO_TRADE scenario
    sig_no_trade = {"trend": "Bullish", "rsi": 80, "vol": 1.0, "momentum": 0.01}
    action = decide_action(sig_no_trade)
    print(f"  ✓ No clear signal → {action}")
    
    print("  PASSED\n")


def test_edge_cases():
    """Test edge cases"""
    print("Test 8: Edge cases")
    
    # Small dataset (should not crash)
    df_small = create_mock_data(60, trend="bullish", volatility="low")
    trades_small = backtest(df_small)
    print(f"  ✓ Small dataset (60 periods): {len(trades_small)} trades")
    
    # High volatility
    df_volatile = create_mock_data(150, trend="sideways", volatility="high")
    trades_volatile = backtest(df_volatile)
    print(f"  ✓ High volatility: {len(trades_volatile)} trades")
    
    print("  PASSED\n")


def test_performance_metrics():
    """Test and display performance metrics"""
    print("Test 9: Performance metrics")
    
    df = create_mock_data(200, trend="bullish", volatility="medium")
    trades = backtest(df)
    
    if trades:
        total_pnl = sum(trades)
        avg_pnl = total_pnl / len(trades)
        winning_trades = len([t for t in trades if t > 0])
        losing_trades = len([t for t in trades if t < 0])
        win_rate = (winning_trades / len(trades)) * 100 if trades else 0
        
        best_trade = max(trades)
        worst_trade = min(trades)
        
        print(f"  ✓ Total trades: {len(trades)}")
        print(f"  ✓ Winning trades: {winning_trades}")
        print(f"  ✓ Losing trades: {losing_trades}")
        print(f"  ✓ Win rate: {win_rate:.2f}%")
        print(f"  ✓ Total P&L: ${total_pnl:.2f}")
        print(f"  ✓ Average P&L: ${avg_pnl:.2f}")
        print(f"  ✓ Best trade: ${best_trade:.2f}")
        print(f"  ✓ Worst trade: ${worst_trade:.2f}")
    else:
        print("  ✓ No trades executed")
    
    print("  PASSED\n")


def run_all_tests():
    """Run all tests"""
    print("="*60)
    print("BACKTESTER TEST SUITE")
    print("="*60)
    print()
    
    try:
        test_backtest_basic()
        test_indicators()
        test_signal_generation()
        test_strategy_decisions()
        test_backtest_bullish_market()
        test_backtest_bearish_market()
        test_backtest_sideways_market()
        test_edge_cases()
        test_performance_metrics()
        
        print("="*60)
        print("ALL TESTS PASSED ✓")
        print("="*60)
        
    except Exception as e:
        print("\n" + "="*60)
        print(f"TEST FAILED ✗")
        print("="*60)
        print(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
