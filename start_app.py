"""
Quick app launcher with status checks
"""

import sys
import os

# Fix Windows console encoding
if sys.platform == "win32":
    try:
        import io
        if sys.stdout.encoding != 'utf-8':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

print("="*60)
print("Starting Options Algo Trading Terminal")
print("="*60)

# Quick check
print("\nRunning pre-flight checks...")

try:
    import streamlit
    print("  [OK] Streamlit installed")
except ImportError:
    print("  [ERROR] Streamlit not installed")
    print("  Run: pip install streamlit")
    sys.exit(1)

try:
    import pandas
    print("  [OK] Pandas installed")
except ImportError:
    print("  [ERROR] Pandas not installed")
    print("  Run: pip install pandas")
    sys.exit(1)

try:
    import requests
    print("  [OK] Requests installed") 
except ImportError:
    print("  [ERROR] Requests not installed")
    print("  Run: pip install requests")
    sys.exit(1)

print("\n" + "="*60)
print("All checks passed! Launching app...")
print("="*60)
print("\nThe app will open in your browser at:")
print("  http://localhost:8501")
print("\nPress Ctrl+C to stop the server")
print("="*60 + "\n")

# Launch streamlit
os.system("streamlit run app.py")
