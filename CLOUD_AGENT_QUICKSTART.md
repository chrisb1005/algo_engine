# Cloud Agent Quick Start

## What Changed?

Your trading agent can now run **autonomously in the cloud** 24/7, executing trades even when your browser is closed!

### Files Added
- **`agent_service.py`**: Standalone agent that runs independently
- **`Procfile`**: Configuration for cloud deployment (Railway, Heroku)
- **`CLOUD_DEPLOYMENT.md`**: Full deployment guide with multiple options

### UI Updates
- **Setup Tab**: New "Cloud Agent" section with deployment instructions
- **Trade Log Tab**: Auto-refresh option to monitor live trades from cloud
- **Monitoring Mode**: Streamlit now displays real-time trades from Supabase

---

## Quick Start (Test Locally)

1. **Create/Configure Your Portfolio**:
   - Open Streamlit app: `streamlit run app.py`
   - Go to "Live Trading" page → Setup tab
   - Create portfolio with your desired settings
   - Click "Sync to Cloud" to save to Supabase

2. **Run Cloud Agent Locally**:
   ```bash
   python agent_service.py your_portfolio_name
   ```
   - Replace `your_portfolio_name` with your actual portfolio name
   - Agent will load config from Supabase and start running
   - Logs appear in terminal and `agent_service.log` file

3. **Monitor in Streamlit**:
   - Keep Streamlit app open (or reopen anytime)
   - Go to "Trade Log" tab
   - Enable "Auto-refresh" checkbox
   - Watch trades appear in real-time as agent executes them

4. **Stop Agent**:
   - Press `Ctrl+C` in the terminal running the agent
   - Agent will save final state to Supabase before stopping

---

## Deploy to Cloud (24/7 Operation)

### Option 1: Railway (Easiest, Free Tier)

1. Push code to GitHub (if not already):
   ```bash
   git add .
   git commit -m "Add cloud agent"
   git push origin main
   ```

2. Go to [railway.app](https://railway.app) and sign up

3. Create new project → "Deploy from GitHub repo"

4. Add environment variables:
   - `SUPABASE_URL`: (your Supabase URL)
   - `SUPABASE_KEY`: (your Supabase key)
   - `PORTFOLIO_NAME`: (your portfolio name)

5. Railway auto-detects `Procfile` and deploys as worker

6. Check logs in Railway dashboard to verify it's running

**Cost**: Free tier includes $5/month credit

### Option 2: Run Locally 24/7

**Windows**:
```powershell
Start-Process python -ArgumentList "agent_service.py", "your_portfolio_name" -WindowStyle Hidden
```

**Mac/Linux**:
```bash
nohup python agent_service.py your_portfolio_name > agent.log 2>&1 &
```

**Note**: Your computer must stay on and connected to internet

---

## How It Works

```
┌─────────────────────────────────────────┐
│  Cloud Agent (agent_service.py)         │
│  - Runs continuously                    │
│  - Loads config from Supabase           │
│  - Monitors tickers                     │
│  - Executes trades                      │
│  - Saves to Supabase                    │
└──────────┬──────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  Supabase (Cloud Database)              │
│  - Stores portfolio state               │
│  - Stores positions & trades            │
│  - Stores agent configuration           │
└──────────┬──────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  Streamlit UI (Monitoring Dashboard)    │
│  - View portfolio in real-time          │
│  - See live trades                      │
│  - Update configuration                 │
│  - Auto-refresh for live updates        │
└─────────────────────────────────────────┘
```

---

## Agent Configuration

All configuration stored in Supabase `agent_config`:

```json
{
  "tickers": ["NVDA", "AAPL", "TSLA"],
  "check_interval": 300,
  "position_size": 1
}
```

To update configuration:
1. Open Streamlit UI
2. Modify tickers, check interval, or position size
3. Click "Sync to Cloud"
4. Agent picks up changes on next cycle (no restart needed)

---

## Monitoring

### View Logs

**Local**:
- Terminal output
- `agent_service.log` file

**Railway**:
- Dashboard → Deployments → Logs

### Streamlit Dashboard

- Portfolio value updates in real-time
- Positions tab shows all open/closed positions
- Trade Log tab shows:
  - Individual trades (buy/sell)
  - Entry/exit prices
  - P&L calculations
- Enable auto-refresh for live monitoring

---

## Trading Logic

The agent follows these rules:

1. **Every Check Interval**:
   - Load portfolio from Supabase
   - For each ticker:
     - Get stock data (3 months)
     - Generate signal using BullCallSpreadStrategy
     - If BUY/STRONG_BUY signal → look for bull call spread opportunity
   - Check existing positions for exit conditions

2. **Entry Conditions**:
   - BUY or STRONG_BUY signal
   - No existing position in ticker
   - Haven't reached max_positions limit
   - Sufficient cash for spread cost
   - Valid options chain available

3. **Exit Conditions**:
   - 50% profit target reached
   - 30% stop loss hit
   - Expiration within 1 day
   - Based on current option prices

4. **After Trades**:
   - Save portfolio state to Supabase
   - Logs trade details
   - Updates cash balance

---

## Troubleshooting

### Agent not starting
- Check `SUPABASE_URL` and `SUPABASE_KEY` are set in .env
- Verify portfolio exists in Supabase
- Check portfolio has `agent_config` data
- Look for errors in logs

### No trades executing
- Verify market is open (agent runs 24/7 but needs market data)
- Check tickers are configured correctly
- Ensure check_interval is reasonable (300-900 seconds)
- Review logs for "No data for {ticker}" messages

### Connection errors
- Verify Supabase credentials
- Check Supabase project is active (free tier pauses after 7 days inactivity)
- Verify internet connection

---

## Next Steps

1. ✅ Test locally first with `python agent_service.py your_portfolio_name`
2. ✅ Monitor for a few hours to verify it's working
3. ✅ Deploy to Railway for 24/7 cloud operation
4. ✅ Use Streamlit as monitoring dashboard
5. ✅ Start with paper trading (no real money)
6. ✅ Run for at least 1 month before considering live trading

---

## Benefits

- 🚀 **Autonomous**: Trades 24/7 without browser open
- ☁️ **Cloud-based**: Deploy to Railway, Render, or any cloud platform
- 📊 **Real-time Monitoring**: Streamlit shows live trades from database
- 🔄 **Auto-sync**: All state saved to Supabase automatically
- 📝 **Full Logging**: Detailed logs of all decisions and trades
- 🔧 **Easy Configuration**: Update settings via Streamlit UI
- 💰 **Cost-effective**: Free tier options available

Enjoy autonomous trading! 🎉
