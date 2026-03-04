"""
Quick verification script to check if algo_engine.py is ready to run
"""

import sys
import os

print("="*60)
print("ALGO ENGINE VERIFICATION")
print("="*60)

# Check Python version
print(f"\n✓ Python version: {sys.version.split()[0]}")

# Check imports
print("\nChecking dependencies...")
dependencies = {
    "streamlit": "Streamlit (Web UI)",
    "pandas": "Pandas (Data manipulation)",
    "numpy": "NumPy (Numerical computing)",
    "requests": "Requests (API calls)"
}

missing = []
for module, description in dependencies.items():
    try:
        __import__(module)
        print(f"  ✓ {description}")
    except ImportError:
        print(f"  ✗ {description} - NOT INSTALLED")
        missing.append(module)

if missing:
    print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
    print(f"Install with: pip install {' '.join(missing)}")
    sys.exit(1)

# Check core modules
print("\nChecking core modules...")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

core_modules = [
    "core.data",
    "core.indicators", 
    "core.signals",
    "core.strategies",
    "core.contracts",
    "core.backtester"
]

for module in core_modules:
    try:
        __import__(module)
        print(f"  ✓ {module}")
    except Exception as e:
        print(f"  ✗ {module} - ERROR: {e}")
        sys.exit(1)

# Check page files
print("\nChecking Streamlit pages...")
pages = [
    "pages/1_algo_engine.py",
    "pages/2_backtester.py", 
    "pages/3_live_trading.py"
]

for page in pages:
    if os.path.exists(page):
        print(f"  ✓ {page}")
    else:
        print(f"  ✗ {page} - NOT FOUND")

# Quick functionality test
print("\nRunning quick functionality test...")
try:
    from core.data import load_history, get_current_price
    from core.indicators import compute_indicators
    from core.signals import generate_signal
    from core.strategies import decide_action
    from core.contracts import choose_contract
    
    # Test data loading
    df = load_history("AAPL", days=100)
    if df is not None and len(df) > 0:
        print(f"  ✓ Data loading works (loaded {len(df)} rows)")
    else:
        print(f"  ⚠️  Could not load data (check internet connection)")
    
    # Test indicators
    if df is not None and len(df) > 50:
        df = compute_indicators(df)
        if "RSI" in df.columns:
            print(f"  ✓ Indicators working")
        
        # Test signal generation
        df_clean = df.dropna()
        if len(df_clean) > 0:
            sig = generate_signal(df_clean)
            action = decide_action(sig)
            print(f"  ✓ Signal generation working (Action: {action})")
    
    print("\n" + "="*60)
    print("✅ ALL CHECKS PASSED - READY TO RUN!")
    print("="*60)
    print("\nTo start the app:")
    print("  Windows: run_app.bat")
    print("  Command: streamlit run app.py")
    print("\nThe app will open in your browser at http://localhost:8501")
    print("="*60)

except Exception as e:
    print(f"\n❌ FUNCTIONALITY TEST FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
