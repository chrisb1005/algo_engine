# Google Sheets Integration Setup Guide

This guide will help you set up Google Sheets integration for your paper trading portfolio, allowing you to save and sync your portfolio data to the cloud.

## Overview

The Google Sheets integration allows you to:
- ✅ Save your portfolio data to Google Sheets automatically
- ✅ View your portfolio in a nicely formatted spreadsheet
- ✅ Access your portfolio from anywhere with internet
- ✅ Share your portfolio with others (optional)
- ✅ Export data for analysis in Excel, etc.

## Setup Steps

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Click on the project dropdown (top left, next to "Google Cloud")
4. Click "NEW PROJECT"
5. Enter project name: `algo-trader` (or any name you like)
6. Click "CREATE"
7. Wait for the project to be created (a few seconds)
8. Select your new project from the dropdown

### Step 2: Enable Required APIs

#### Enable Google Sheets API:
1. In the left sidebar, go to "APIs & Services" > "Library"
2. In the search box, type "Google Sheets API"
3. Click on "Google Sheets API" in the results
4. Click "ENABLE"
5. Wait for it to enable (a few seconds)

#### Enable Google Drive API:
1. Click the back arrow or search again in the API Library
2. Search for "Google Drive API"
3. Click on "Google Drive API" in the results
4. Click "ENABLE"

### Step 3: Create a Service Account

1. In the left sidebar, go to "APIs & Services" > "Credentials"
2. Click the "+ CREATE CREDENTIALS" button at the top
3. Select "Service Account" from the dropdown
4. Fill in the service account details:
   - **Service account name**: `algo-trader-sheets` (or any name)
   - **Service account ID**: auto-generated (leave as is)
   - **Description**: "Service account for algo trader portfolio sync"
5. Click "CREATE AND CONTINUE"
6. In "Grant this service account access to project":
   - Select role: "Editor" (or "Basic" > "Editor")
7. Click "CONTINUE"
8. Skip "Grant users access to this service account" (click "DONE")

### Step 4: Create and Download Keys

1. You should now see your service account in the list
2. Click on the service account email (looks like `algo-trader-sheets@your-project.iam.gserviceaccount.com`)
3. Go to the "KEYS" tab at the top
4. Click "ADD KEY" > "Create new key"
5. Select "JSON" format
6. Click "CREATE"
7. The JSON key file will automatically download to your computer

### Step 5: Configure Your Project

1. **Rename the file**: Rename the downloaded JSON file to `google_credentials.json`

2. **Move to project folder**: Place the file in your algo_trader directory:
   ```
   c:\Users\Chris Breezy\Documents\projects\algo_trader\google_credentials.json
   ```

3. **Verify the file structure** - The JSON should look something like this:
   ```json
   {
     "type": "service_account",
     "project_id": "your-project-id",
     "private_key_id": "...",
     "private_key": "-----BEGIN PRIVATE KEY-----\n...",
     "client_email": "algo-trader-sheets@your-project.iam.gserviceaccount.com",
     ...
   }
   ```

### Step 6: Install Required Packages

Run this command in your terminal:

```powershell
pip install gspread google-auth oauth2client
```

Or install from requirements.txt:

```powershell
pip install -r requirements.txt
```

### Step 7: Test the Integration

Run the demo script to test if everything is working:

```powershell
python demo_sheets_sync.py
```

If successful, you should see:
- ✅ Successfully synced to Google Sheets!
- 🔗 A link to your spreadsheet

## Using Google Sheets Sync

### In the Streamlit App:

1. Go to the "Live Trading" page
2. Create or load a portfolio
3. Scroll down to the "☁️ Google Sheets Sync" section
4. Make sure the credentials path shows `google_credentials.json`
5. Click "☁️ Sync to Google Sheets"
6. You'll get a link to your spreadsheet if successful!

### Programmatically:

```python
from core.paper_trader import PaperTradingPortfolio

# Create or load portfolio
portfolio = PaperTradingPortfolio(starting_cash=10000)

# Sync to Google Sheets
success, result = portfolio.save_to_google_sheets('google_credentials.json')

if success:
    print(f"Spreadsheet URL: {result}")
else:
    print(f"Error: {result}")
```

## Spreadsheet Structure

The Google Sheet will have 4 tabs:

1. **Portfolio** - Summary metrics (cash, P&L, win rate, etc.)
2. **Positions** - All positions (open and closed)
3. **Trade History** - Detailed trade log
4. **Config** - Configuration settings (future use)

## Troubleshooting

### Error: "Credentials file not found"
- Make sure `google_credentials.json` is in the correct folder
- Check the file name is exactly `google_credentials.json` (case sensitive)

### Error: "Authentication failed"
- Verify the JSON file is valid (not corrupted)
- Make sure you enabled both Google Sheets API and Google Drive API
- Try downloading the credentials again

### Error: "Permission denied"
- Make sure the service account has "Editor" role
- Check that both APIs are enabled in your Google Cloud project

### Can't see the spreadsheet in Google Drive
- The spreadsheet is created under the service account, not your personal account
- The spreadsheet will be visible in the link provided after syncing
- To see it in your Drive, you can share it with yourself:
  1. Open the spreadsheet link
  2. Click "Share" (top right)
  3. Add your email address

## Security Notes

⚠️ **Important**: The `google_credentials.json` file contains sensitive credentials!

- **DO NOT** commit this file to Git
- **DO NOT** share this file publicly
- Add `google_credentials.json` to your `.gitignore` file
- Keep this file secure and private

## Additional Features

### Auto-Sync After Trades

The agent can automatically sync to Google Sheets after each trade:

```python
from core.auto_agent import AutoTradingAgent

# Create agent with auto-sync
def auto_sync():
    portfolio.save_to_google_sheets()

agent = AutoTradingAgent(
    portfolio=portfolio,
    tickers=['AAPL', 'MSFT'],
    save_callback=auto_sync  # Auto-sync after trades
)
```

### Sharing Your Portfolio

To share your portfolio spreadsheet with others:

1. Open the spreadsheet link
2. Click "Share" button (top right)
3. Add email addresses of people you want to share with
4. Set permissions (Viewer, Commenter, or Editor)
5. Click "Send"

## Questions?

If you run into issues:
1. Check the error message carefully
2. Verify all setup steps were completed
3. Make sure APIs are enabled
4. Try the demo script to isolate the issue

Happy trading! 🚀📊
