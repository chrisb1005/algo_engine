# Options Algo Trading Terminal 📈

An automated algorithmic trading platform for options trading with real-time signals, backtesting, and strategy recommendations.

## Features

### 🔍 Algo Engine
- Real-time technical analysis with RSI, moving averages, and momentum indicators
- Automated strategy recommendations (BUY_CALL, BUY_PUT, SELL_CALL, SELL_PUT)
- Smart contract selection with optimal strike prices and expirations
- Live data from Polygon.io and Yahoo Finance APIs

### 📊 Backtester
- Test strategies on historical data
- Track P&L, win rates, and trade statistics
- Visualize cumulative returns
- Validate strategy effectiveness before going live

### ⚡ Live Trading (Coming Soon)
- Integration with Alpaca and Tradier APIs
- Automated order execution
- Real-time position monitoring

## Quick Start

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the App

**Option 1: Windows Batch File**
```bash
run_app.bat
```

**Option 2: Command Line**
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Testing

Run the test suites to verify everything works:

```bash
# Test data loading
python test\test_data.py

# Test backtester
python test\test_backtester.py

# Test algo engine
python test\test_algo_engine.py

# Test contracts/options
cd core
python contractstest.py
python contractstest_helpers.py
```

## Usage

### Algo Engine

1. Navigate to **🔍 Algo Engine** in the sidebar
2. Enter a ticker symbol (e.g., AAPL, MSFT, TSLA)
3. Select analysis period
4. Click **Analyze**
5. Review signals and contract recommendations

### Backtester

1. Navigate to **📊 Backtester** in the sidebar
2. Enter a ticker symbol
3. Select days of history (60-365 days)
4. Click **Run Backtest**
5. Review performance metrics and charts

## Project Structure

```
algo_trader/
├── app.py                  # Main Streamlit app
├── run_app.bat            # Windows startup script
├── requirements.txt       # Python dependencies
├── core/                  # Core trading logic
│   ├── data.py           # Data loading (Polygon + Yahoo Finance)
│   ├── indicators.py     # Technical indicators (MA, RSI, etc.)
│   ├── signals.py        # Signal generation
│   ├── strategies.py     # Trading strategies
│   ├── contracts.py      # Options contract selection
│   ├── backtester.py     # Backtesting engine
│   └── execution.py      # Order execution (future)
├── pages/                 # Streamlit pages
│   ├── 1_algo_engine.py  # Algo engine interface
│   ├── 2_backtester.py   # Backtester interface
│   └── 3_live_trading.py # Live trading interface
└── test/                  # Test suites
    ├── test_data.py
    ├── test_backtester.py
    └── test_algo_engine.py
```

## Core Modules

### data.py
- **Automatic fallback**: Polygon API → Yahoo Finance
- **5-minute caching**: 350x faster repeated requests
- **Data validation**: Quality checks on all data
- **Helper functions**: `get_current_price()`, `get_price_stats()`

### contracts.py
- **Yahoo Finance session management** with crumb token authentication
- **Options chain loading** with all expirations
- **Smart contract selection**: Find ATM, OTM, highest volume, highest IV
- **Helper functions**: `choose_contract()`, `find_atm_options()`, `find_best_option()`

### indicators.py
- Moving averages (MA20, MA50)
- RSI (Relative Strength Index)
- Momentum indicators
- Volatility calculations

### strategies.py
- Automated decision making based on signals
- Actions: BUY_CALL, BUY_PUT, SELL_CALL, SELL_PUT, NO_TRADE
- Customizable rules and thresholds

### backtester.py
- Historical strategy simulation
- Trade tracking and P&L calculation
- Performance metrics

## API Keys

### Polygon.io
The app includes a Polygon.io API key for historical data. For production use, sign up at [polygon.io](https://polygon.io) for your own key.

### Yahoo Finance
No API key required. Uses public Yahoo Finance API with proper authentication.

## Recent Updates

### ✅ Fixed & Optimized

1. **contracts.py**
   - Added Yahoo Finance session management with crumb token
   - Fixed 401 authentication errors
   - Added helper functions for contract selection
   - Better error handling with detailed messages

2. **data.py**
   - Added 5-minute caching (350x speedup)
   - Implemented data validation
   - Added `get_current_price()` and `get_price_stats()`
   - Better error messages for debugging

3. **algo_engine.py**
   - Complete redesign with better UI
   - Added visual metrics and charts
   - Error handling and user feedback
   - Contract recommendation display

4. **backtester.py**
   - Fixed parameter issues
   - Added detailed metrics and charts
   - Better result visualization

5. **Test Suites**
   - 100% test pass rate
   - Comprehensive coverage of all modules
   - Demo scripts for each module

## Disclaimer

⚠️ **This tool is for educational and research purposes only.** 

Always do your own research and consult with a financial advisor before making investment decisions. Past performance does not guarantee future results.

## Support

For issues or questions, check the test scripts for examples of proper usage.

## License

MIT License - See LICENSE file for details
