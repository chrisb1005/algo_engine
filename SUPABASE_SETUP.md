# Supabase Setup Guide (2 Minutes)

## Why Supabase Instead of Google Sheets?

✅ **Faster** - Real PostgreSQL database vs spreadsheet  
✅ **Easier** - 2-minute setup vs 15 minutes  
✅ **No JSON files** - Just URL + API key  
✅ **More secure** - Database-level permissions  
✅ **Better for trading** - Proper data types, queries, indexes  
✅ **100% Free** - Up to 500MB database (plenty for trading data)

---

## Quick Setup (5 Steps)

### 1. Create Free Account
- Go to [supabase.com](https://supabase.com/)
- Click "Start your project"
- Sign in with GitHub (fastest) or email

### 2. Create Project
- Click "New Project"
- Name: `algo-trader` (or any name)
- Database Password: Create a strong password (save it!)
- Region: Choose closest to you
- Click "Create new project"
- ⏱️ Wait ~2 minutes for project to deploy

### 3. Get Credentials
- Once project is ready, click on Project Settings (gear icon)
- Go to **API** section
- Copy two things:
  1. **Project URL** - looks like `https://xxxxx.supabase.co`
  2. **anon public** key - under "Project API keys" (long string starting with "eyJ...")

### 4. Create Database Tables
- Go to **SQL Editor** (left sidebar)  
- Click "New Query"
- Paste this SQL and click "Run":

```sql
-- Portfolios table
CREATE TABLE IF NOT EXISTS portfolios (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    starting_cash NUMERIC NOT NULL,
    current_cash NUMERIC NOT NULL,
    max_position_size NUMERIC NOT NULL,
    max_positions INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Positions table
CREATE TABLE IF NOT EXISTS positions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    portfolio_id UUID REFERENCES portfolios(id) ON DELETE CASCADE,
    ticker TEXT NOT NULL,
    option_type TEXT NOT NULL,
    strike NUMERIC NOT NULL,
    expiration TIMESTAMP WITH TIME ZONE NOT NULL,
    quantity INTEGER NOT NULL,
    entry_price NUMERIC NOT NULL,
    entry_date TIMESTAMP WITH TIME ZONE NOT NULL,
    exit_price NUMERIC,
    exit_date TIMESTAMP WITH TIME ZONE,
    status TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Trades table
CREATE TABLE IF NOT EXISTS trades (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    portfolio_id UUID REFERENCES portfolios(id) ON DELETE CASCADE,
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    ticker TEXT,
    action TEXT,
    option_type TEXT,
    strike NUMERIC,
    quantity INTEGER,
    price NUMERIC,
    cost NUMERIC,
    pnl NUMERIC,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_positions_portfolio ON positions(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_trades_portfolio ON trades(portfolio_id);
```

You should see "Success. No rows returned" - that's good!

### 5. Add Credentials to Your Project

**Option A: Use .env file (recommended)**

Create a file named `.env` in your project root:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...your-key...
```

**Option B: Paste directly in Streamlit UI**

Just paste your URL and key in the "Supabase Cloud Sync" section.

---

## Testing

Run the demo script:

```bash
python demo_supabase_sync.py
```

You should see:
```
✅ Successfully synced to Supabase!
✅ Successfully loaded portfolio!
```

---

## Using in the App

### Save Portfolio to Cloud:
1. Go to "Live Trading" page
2. Scroll to "☁️ Supabase Cloud Sync"
3. Enter your credentials (if not in .env)
4. Enter a portfolio name (e.g., "my_portfolio")
5. Click "☁️ Sync to Cloud"

### Load Portfolio from Cloud:
1. Enter the same portfolio name
2. Click "📥 Load from Cloud"
3. Your portfolio will be restored!

---

## View Your Data

You can view your trading data in Supabase:

1. Go to your Supabase project
2. Click "Table Editor" (left sidebar)
3. View `portfolios`, `positions`, and `trades` tables
4. See all your portfolio data in real-time!

---

## Security Notes

🔒 **Your data is secure:**
- Supabase uses PostgreSQL with row-level security
- API keys can be rotated anytime
- Data is encrypted in transit and at rest
- Free tier includes 500MB (plenty for years of trades)

⚠️ **Keep your keys safe:**
- Don't commit `.env` file to Git (already in .gitignore)
- Don't share your API key publicly
- Can create multiple API keys for different purposes

---

## Troubleshooting

**Error: "No module named 'supabase'"**
```bash
pip install supabase python-dotenv
```

**Error: "SUPABASE_URL and KEY required"**
- Make sure `.env` file exists in project root
- Or paste credentials in the UI fields

**Error: "relation does not exist"**
- You forgot to run the SQL in Step 4
- Go to SQL Editor and run the CREATE TABLE queries

**Tables not showing in Table Editor:**
- Refresh the page
- Check SQL Editor for any errors

---

## Auto-Sync After Trades

The agent automatically syncs to Supabase after each trade if credentials are set!

---

## Free Tier Limits

Supabase free tier includes:
- ✅ 500MB database storage
- ✅ 2GB bandwidth per month
- ✅ 50,000 monthly active users
- ✅ Social OAuth providers
- ✅ Unlimited API requests

**Estimate:** You can store ~100,000 trades on the free tier!

---

## Questions?

- Supabase Docs: [supabase.com/docs](https://supabase.com/docs)
- Support: [supabase.com/support](https://supabase.com/support)

Happy trading! 🚀📊
