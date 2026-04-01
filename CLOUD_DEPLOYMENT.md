# Cloud Agent Deployment Guide

## Overview
Your trading agent can now run independently in the cloud, executing trades 24/7 without needing your browser open. The Streamlit UI becomes a monitoring dashboard that shows live trades from the cloud.

## Architecture
- **Agent Service** (`agent_service.py`): Standalone Python script that runs continuously
- **Supabase**: Cloud database storing portfolio, trades, and agent configuration
- **Streamlit UI**: Monitoring dashboard to view trades and portfolio state

---

## Option 1: Run Locally (Background Process)

### Windows
```powershell
# Start the agent in background
python agent_service.py your_portfolio_name

# Or run with nohup-equivalent (keep running after closing terminal)
Start-Process python -ArgumentList "agent_service.py", "your_portfolio_name" -WindowStyle Hidden
```

### Mac/Linux
```bash
# Start the agent in background
nohup python agent_service.py your_portfolio_name > agent.log 2>&1 &

# Check if it's running
ps aux | grep agent_service

# Stop the agent
pkill -f agent_service.py
```

**Note**: Your computer must stay on and connected to internet. For true 24/7 operation, use a cloud deployment.

---

## Option 2: Deploy to Cloud (Recommended)

### Deploy to Railway (Free Tier)

1. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your GitHub account
   - Select your algo_trader repository

3. **Configure Environment Variables**
   - Go to your project settings
   - Add these variables:
     ```
     SUPABASE_URL=your_supabase_url
     SUPABASE_KEY=your_supabase_key
     PORTFOLIO_NAME=your_portfolio_name
     ```

4. **Create Procfile**
   - Add a file named `Procfile` in your project root:
     ```
     worker: python agent_service.py
     ```

5. **Deploy**
   - Railway will automatically deploy
   - Your agent will start running 24/7
   - Check logs in Railway dashboard

**Cost**: Free tier includes $5/month credit (enough for this agent)

---

### Deploy to Render (Free Tier)

1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

2. **Create Background Worker**
   - Click "New +"
   - Select "Background Worker"
   - Connect your repository

3. **Configure**
   - **Name**: algo-trading-agent
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python agent_service.py`
   - **Environment Variables**:
     ```
     SUPABASE_URL=your_supabase_url
     SUPABASE_KEY=your_supabase_key
     PORTFOLIO_NAME=your_portfolio_name
     ```

4. **Deploy**
   - Click "Create Background Worker"
   - Render will deploy and start your agent
   - View logs in Render dashboard

**Cost**: Free tier available (with some limitations)

---

### Deploy to Heroku

1. **Install Heroku CLI**
   ```bash
   # Windows (with chocolatey)
   choco install heroku-cli
   
   # Mac
   brew install heroku/brew/heroku
   ```

2. **Login and Create App**
   ```bash
   heroku login
   heroku create your-algo-trader
   ```

3. **Set Environment Variables**
   ```bash
   heroku config:set SUPABASE_URL=your_supabase_url
   heroku config:set SUPABASE_KEY=your_supabase_key
   heroku config:set PORTFOLIO_NAME=your_portfolio_name
   ```

4. **Create Procfile**
   ```
   worker: python agent_service.py
   ```

5. **Deploy**
   ```bash
   git add .
   git commit -m "Deploy cloud agent"
   git push heroku main
   
   # Scale up the worker
   heroku ps:scale worker=1
   ```

6. **View Logs**
   ```bash
   heroku logs --tail
   ```

**Cost**: Free tier available (550-1000 dyno hours/month)

---

## Option 3: AWS/Google Cloud

### AWS Lambda (Serverless)
- Best for: Running on schedule (every 5-15 minutes)
- **Pros**: Only pay when running, very cheap
- **Cons**: More complex setup, 15-minute max execution time

### Google Cloud Run
- Best for: Continuous running with auto-scaling
- **Pros**: Auto-scales, generous free tier
- **Cons**: Requires Docker knowledge

### EC2/Compute Engine
- Best for: Full control, 24/7 operation
- **Pros**: Full control, can run anything
- **Cons**: More expensive, requires server management

---

## Monitoring Your Agent

### View Logs

**Local**:
```bash
# View log file
tail -f agent_service.log

# Windows PowerShell
Get-Content agent_service.log -Wait
```

**Railway**: View in dashboard under "Deployments" → "Logs"

**Render**: View in dashboard under "Logs" tab

**Heroku**:
```bash
heroku logs --tail
```

### Streamlit Dashboard
- Open your Streamlit app
- Navigate to "Live Trading" page
- Portfolio and trades automatically sync from Supabase
- See real-time updates as agent executes trades

---

## Configuration

### Change Tickers/Settings
1. Update in Streamlit UI:
   - Modify tickers, check interval, position size
   - Click "Sync to Cloud"

2. Agent picks up changes:
   - Agent reloads config from Supabase on each cycle
   - No need to restart

### Stop the Agent

**Local**:
```bash
# Send Ctrl+C to the process
# Or kill by process ID
pkill -f agent_service.py  # Mac/Linux
Stop-Process -Name python   # Windows (be careful, stops all Python)
```

**Cloud**: Scale down to 0 workers in platform dashboard

---

## Troubleshooting

### Agent Not Starting
- Check logs for error messages
- Verify SUPABASE_URL and SUPABASE_KEY are set correctly
- Ensure portfolio exists in Supabase with agent_config

### No Trades Executing
- Check if tickers are configured in agent_config
- Verify check_interval is reasonable (300-900 seconds recommended)
- Check logs for "No data for {ticker}" messages
- Ensure market is open (agent runs 24/7 but only trades during market hours)

### Out of Memory
- Cloud free tiers have memory limits (512MB typically)
- Reduce number of tickers being monitored
- Increase check_interval to reduce memory usage

### Connection Errors
- Verify Supabase credentials
- Check if Supabase project is active (free tier pauses after 7 days inactivity)
- Verify internet connection (for local deployment)

---

## Best Practices

1. **Start Small**: Test with 1-2 tickers first
2. **Monitor Logs**: Check logs daily for first week
3. **Set Alerts**: Use platform monitoring (Railway, Render) to get alerts on crashes
4. **Backup**: Supabase auto-backs up, but export portfolio data weekly
5. **Paper Trading**: Run in paper trading mode for at least 1 month before live

---

## Cost Comparison

| Platform | Free Tier | Best For |
|----------|-----------|----------|
| Local | $0 (electricity only) | Testing, development |
| Railway | $5/month credit | Simple, beginner-friendly |
| Render | 750 hours/month free | Good free option |
| Heroku | 550-1000 hours/month | Established platform |
| AWS Lambda | 1M requests/month | Scheduled (not continuous) |
| Google Cloud Run | 2M requests/month | Auto-scaling needs |

**Recommendation**: Start with Railway or Render free tier for 24/7 cloud operation.

---

## Next Steps

1. Test locally first: `python agent_service.py your_portfolio_name`
2. Monitor logs for errors
3. Once stable, deploy to Railway or Render
4. Use Streamlit as monitoring dashboard
5. Enjoy autonomous trading! 🚀
