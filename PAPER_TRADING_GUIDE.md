# Paper Trading Agent 🤖

Automated trading agent that monitors stocks and executes options trades based on algo_engine signals using virtual money.

## Features

### 📊 Paper Trading Portfolio
- Start with virtual cash ($1K - $1M)
- Track positions and P&L in real-time
- No risk - all trades are simulated
- Position size limits and risk management
- Trade history and performance statistics

### 🤖 Automated Agent
- Monitors multiple tickers simultaneously
- Gets signals from algo_engine for each ticker
- Automatically finds and buys option contracts
- Configurable check intervals (1 min - 1 hour)
- Real-time activity logging

### 📈 Risk Management
- Maximum position size (% of portfolio)
- Maximum number of open positions
- Automatic position closing near expiration
- Cash management

## How to Use

### 1. Setup Portfolio

1. Navigate to **"🤖 Paper Trading Agent"** page in Streamlit
2. Go to **"⚙️ Setup"** tab
3. Configure:
   - **Starting Cash**: $1,000 - $1,000,000 (virtual money)
   - **Max Open Positions**: 1-20 (how many positions simultaneously)
   - **Max Position Size**: 1-20% (max % of portfolio per trade)
   - **Contracts Per Trade**: 1-10 (number of contracts to buy)
   - **Tickers to Monitor**: Enter one per line (e.g., AAPL, MSFT, TSLA)
   - **Check Interval**: How often to check for signals

4. Click **"🚀 Create Portfolio"**

### 2. Start the Agent

1. Once portfolio is created, click **"▶️ Start Agent"**
2. Agent will:
   - Check each ticker for signals every interval
   - When a BUY_CALL or BUY_PUT signal appears, find option contract
   - Automatically execute the trade if portfolio has enough cash
   - Log all activity in the Trade Log tab

### 3. Monitor Performance

**📊 Portfolio Tab:**
- View portfolio value and total return
- See cash balance and open positions
- Review performance statistics (win rate, avg P&L, etc.)
- Check portfolio allocation

**📈 Positions Tab:**
- View all open positions with details
- See closed positions history
- Track days held and days to expiry
- Monitor entry/exit prices and P&L

**📜 Trade Log Tab:**
- Real-time activity log
- See when signals are detected
- View trade executions
- Monitor agent status

### 4. Stop and Reset

- Click **"⏹️ Stop Agent"** to pause monitoring
- Click **"🗑️ Reset Portfolio"** to start fresh

## Trading Logic

### Signal Detection
The agent uses the same algo_engine logic as the main analysis tool:
1. Load 60 days of historical data
2. Compute technical indicators (MA20, MA50, RSI, Momentum, Volatility)
3. Generate trading signal from indicators
4. Decide action (BUY_CALL, BUY_PUT, SELL_CALL, SELL_PUT, NO_TRADE)

### Contract Selection
When a BUY signal is detected:
1. Get next week's expiration date
2. Load options chain for that expiration
3. Choose contract using `choose_contract()` helper:
   - For calls: Slightly OTM (strike > current price)
   - For puts: Slightly OTM (strike < current price)
   - Filters for liquidity (volume > 100)
   - Selects reasonable price range

### Position Management
- **Entry**: Execute when signal appears and portfolio has capacity
- **Exit**: Currently closes positions 1 day before expiration
- **Future enhancements**: Stop-loss, take-profit, signal-based exits

## Example Configuration

**Conservative Setup:**
- Starting Cash: $10,000
- Max Positions: 3
- Max Position Size: 5%
- Contracts Per Trade: 1
- Tickers: AAPL, MSFT, GOOGL
- Check Interval: 1 hour

**Aggressive Setup:**
- Starting Cash: $50,000
- Max Positions: 10
- Max Position Size: 10%
- Contracts Per Trade: 2
- Tickers: AAPL, MSFT, TSLA, AMD, NVDA, META, GOOGL, AMZN, SPY, QQQ
- Check Interval: 5 minutes

## Files

- **`core/paper_trader.py`**: Portfolio management, position tracking, P&L calculations
- **`core/auto_agent.py`**: Automated trading agent logic
- **`pages/3_live_trading.py`**: Streamlit UI for paper trading
- **`test/test_paper_trading.py`**: Test script for backend

## Testing

Run the test script to verify functionality:

```bash
python test/test_paper_trading.py
```

Tests:
- Portfolio creation
- Opening positions
- Closing positions
- P&L calculations
- Statistics
- Agent creation
- Save/load functionality

## Future Enhancements

- [ ] Stop-loss and take-profit orders
- [ ] Signal-based exits (sell when signal reverses)
- [ ] Portfolio rebalancing
- [ ] Multiple strategy support
- [ ] Real options pricing data for P&L
- [ ] Performance charts and analytics
- [ ] Email/SMS notifications for trades
- [ ] Save/load portfolio state
- [ ] Export trade history to CSV

## Risk Warning

⚠️ This is a paper trading tool for testing strategies with virtual money. Do NOT use this for real money trading without:
1. Thoroughly testing your strategy
2. Understanding the risks
3. Consulting with a financial advisor
4. Using proper risk management

Past performance does not guarantee future results. Options trading is risky and you can lose your entire investment.
