# CSE API MCP Server 📈

Model Context Protocol (MCP) server that exposes Colombo Stock Exchange (CSE) API endpoints as tools for Large Language Models.

## What is MCP?

The Model Context Protocol (MCP) is an open protocol that enables AI assistants to securely access external data sources and tools. This server implements MCP to make CSE stock market data available to LLMs like Claude, GPT, and others.

## Features

- **22 CSE API endpoints** exposed as MCP tools
- Real-time stock market data access
- Company information, prices, and trading volumes
- Market indices (ASPI, S&P SL20)
- Announcements and regulatory filings
- Sector and daily market summaries
- Async HTTP requests with proper error handling

## Available Tools

### Stock & Company Data
- `cse_get_company_info` - Detailed company info by symbol (price, market cap, beta, logo)
- `cse_get_today_share_price` - Today's share prices for all securities
- `cse_get_trade_summary` - Summary of all trades
- `cse_get_chart_data` - Historical price/chart data for technical analysis

### Market Movers
- `cse_get_top_gainers` - Top gaining stocks
- `cse_get_top_losers` - Top losing stocks
- `cse_get_most_active_trades` - Most active by volume
- `cse_get_detailed_trades` - Detailed trade information

### Market Indices & Summary
- `cse_get_aspi_data` - All Share Price Index (ASPI)
- `cse_get_snp_data` - S&P Sri Lanka 20 Index
- `cse_get_market_status` - Market open/closed status
- `cse_get_market_summary` - Overall market statistics
- `cse_get_daily_market_summary` - Comprehensive daily data (turnover, market cap, P/E, P/BV, dividend yield)
- `cse_get_all_sectors` - All sector/industry group data

### Announcements & Regulatory
- `cse_get_financial_announcements` - Annual reports, quarterly results
- `cse_get_approved_announcements` - Company disclosures
- `cse_get_new_listings_announcements` - New listings and notices
- `cse_get_buy_in_board_announcements` - Buy-in board notices
- `cse_get_circular_announcements` - Regulatory circulars
- `cse_get_directive_announcements` - Regulatory directives
- `cse_get_non_compliance_announcements` - Non-compliance notices
- `cse_get_covid_announcements` - COVID-related announcements

## Installation

### Prerequisites
- Python 3.10 or higher
- pip

### Install Dependencies

```powershell
cd mcp_server
pip install -r requirements.txt
```

Or install individually:
```powershell
pip install mcp httpx pydantic
```

## Configuration

### For Claude Desktop (or other MCP clients)

Add to your MCP settings configuration file:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

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

> **Note:** Replace the path with your actual absolute path to `main.py`

### For Other MCP Clients

Configure your MCP client to run:
```powershell
python d:\Projects\Experiments\Colombo-Stock-Exchange-CSE-API-Documentation\mcp_server\main.py
```

## Usage Examples

Once configured, you can ask your LLM questions like:

- "Get information about LOLC stock"
- "What are today's top gainers on CSE?"
- "Show me the current ASPI index value"
- "Get the market summary for today"
- "What are the latest financial announcements?"
- "Show me detailed trades for ABAN.N0000"
- "Is the market open right now?"
- "Get all sector performance data"

The LLM will automatically call the appropriate CSE API tools and format the results.

## Testing the Server

Run the server manually to verify it works:

```powershell
cd mcp_server
python main.py
```

The server communicates via stdio (standard input/output), so it won't show a typical web interface. When properly configured in an MCP client, it will respond to tool calls.

To test with MCP Inspector (debugging tool):

```powershell
npx @modelcontextprotocol/inspector python main.py
```

## Development

### Project Structure
```
mcp_server/
├── __init__.py          # Package init
├── main.py              # MCP server implementation
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

### Adding New Tools

To add a new CSE endpoint:

1. Add tool definition in `list_tools()`
2. Add endpoint mapping in `call_tool()` endpoint_map
3. Update this README

## API Rate Limiting & Usage

⚠️ **Important Notes:**
- This uses the unofficial CSE public API (reverse-engineered)
- No official documentation or SLA exists
- Endpoints may change without notice
- Be respectful with request frequency to avoid IP blocking
- Validate critical data with official CSE sources

## Troubleshooting

### Server won't start
- Verify Python 3.10+ is installed: `python --version`
- Check dependencies are installed: `pip list | findstr mcp`
- Look for error messages in logs

### Tools not appearing in LLM
- Verify MCP config file path is correct
- Restart your MCP client (e.g., Claude Desktop)
- Check server is running without errors

### HTTP errors from CSE API
- Some endpoints may require specific parameters
- The CSE API may be temporarily unavailable
- Check your internet connection
- Some symbols may not be valid

## License

This MCP server is provided as-is for educational purposes. The underlying CSE API is owned by the Colombo Stock Exchange.

## Contributing

Contributions welcome! Please test thoroughly and follow the existing code style.

## Disclaimer

- This is an **unofficial** integration using reverse-engineered endpoints
- Use responsibly and verify data accuracy
- No warranties or guarantees provided
- For official CSE data, visit https://www.cse.lk

---

Built with ❤️ using the [Model Context Protocol](https://modelcontextprotocol.io)
