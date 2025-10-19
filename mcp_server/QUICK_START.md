# Quick Setup Guide for Claude Desktop

## Step 1: Install Dependencies

Open PowerShell and run:
```powershell
cd d:\Projects\Experiments\Colombo-Stock-Exchange-CSE-API-Documentation\mcp_server
pip install -r requirements.txt
```

## Step 2: Configure Claude Desktop

1. **Locate your Claude Desktop config file:**
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - To open quickly, press `Win+R` and paste: `%APPDATA%\Claude`

2. **Edit the config file** (create it if it doesn't exist):

```json
{
  "mcpServers": {
    "cse-api": {
      "command": "python",
      "args": [
        "d:\\Projects\\Experiments\\Colombo-Stock-Exchange-CSE-API-Documentation\\mcp_server\\main.py"
      ]
    }
  }
}
```

> ⚠️ **Important:** Use your actual absolute path and double backslashes (`\\`) in the path!

3. **Restart Claude Desktop** completely (quit and reopen)

## Step 3: Verify It Works

In Claude Desktop, try asking:
- "What tools do you have available?" (You should see 22 CSE tools)
- "Get information about LOLC stock"
- "What are today's top gainers on CSE?"
- "Show me the current ASPI index"

## Available Tools (22 total)

### Market Data
- `cse_get_company_info` - Company details by symbol
- `cse_get_today_share_price` - Current prices
- `cse_get_trade_summary` - Trade summary
- `cse_get_chart_data` - Historical price data
- `cse_get_detailed_trades` - Detailed trades

### Market Movers
- `cse_get_top_gainers` - Top gaining stocks
- `cse_get_top_losers` - Top losing stocks  
- `cse_get_most_active_trades` - Most active by volume

### Indices & Summary
- `cse_get_aspi_data` - ASPI index
- `cse_get_snp_data` - S&P SL20 index
- `cse_get_market_status` - Open/closed status
- `cse_get_market_summary` - Market statistics
- `cse_get_daily_market_summary` - Daily comprehensive data
- `cse_get_all_sectors` - Sector data

### Announcements (8 types)
- Financial, Approved, New Listings, Buy-in Board, Circular, Directive, Non-compliance, COVID

## Troubleshooting

**Tools not showing up?**
1. Check the config file path is correct
2. Verify double backslashes in the path
3. Restart Claude Desktop completely
4. Check logs in Claude Desktop (View → Developer → Toggle Developer Tools)

**Python not found?**
- Use full path to python.exe:
  ```json
  "command": "C:\\Users\\YourName\\AppData\\Local\\Programs\\Python\\Python313\\python.exe"
  ```

**Import errors?**
- Make sure you ran `pip install -r requirements.txt`
- Try: `pip list | findstr mcp` to verify mcp is installed

## Example Queries

Once configured, you can ask Claude:

**Stock Analysis:**
- "Analyze LOLC stock - get company info, recent trades, and chart data"
- "Compare top gainers and losers today"
- "Show me all available CSE market data"

**Market Overview:**
- "Give me a complete market summary including ASPI, market status, and trading volumes"
- "What's happening in different sectors today?"

**Research:**
- "Get all recent financial announcements and summarize them"
- "Are there any compliance issues with CSE companies?"
- "Show me the daily market summary with P/E ratios and market cap"

---

## Need Help?

See the main [README.md](README.md) for full documentation.
