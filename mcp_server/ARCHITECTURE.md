# CSE API MCP Server - Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         LLM Client                              │
│              (Claude Desktop, GPT, etc.)                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ MCP Protocol (stdio)
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                   MCP Server (main.py)                          │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              22 MCP Tool Endpoints                       │  │
│  │                                                          │  │
│  │  • cse_get_company_info                                 │  │
│  │  • cse_get_trade_summary                                │  │
│  │  • cse_get_today_share_price                            │  │
│  │  • cse_get_top_gainers / losers / active                │  │
│  │  • cse_get_market_status / summary / daily_summary      │  │
│  │  • cse_get_aspi_data / snp_data                         │  │
│  │  • cse_get_chart_data                                   │  │
│  │  • cse_get_detailed_trades                              │  │
│  │  • cse_get_all_sectors                                  │  │
│  │  • cse_get_*_announcements (8 types)                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                         │                                       │
│                         │ HTTP POST                             │
│                         │ application/x-www-form-urlencoded     │
│                         │                                       │
└─────────────────────────┼───────────────────────────────────────┘
                          │
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│              CSE Public API (www.cse.lk/api/)                   │
│                                                                 │
│  Endpoints:                                                     │
│  • companyInfoSummery      • topGainers                         │
│  • tradeSummary            • topLooses                          │
│  • todaySharePrice         • mostActiveTrades                   │
│  • marketStatus            • chartData                          │
│  • marketSummery           • allSectors                         │
│  • aspiData                • detailedTrades                     │
│  • snpData                 • dailyMarketSummery                 │
│  • getFinancialAnnouncement                                     │
│  • approvedAnnouncement                                         │
│  • + 8 more announcement endpoints                              │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

1. **LLM sends tool call** → MCP Server via stdio protocol
2. **MCP Server validates** → Input schema, required parameters
3. **Server makes HTTP POST** → CSE API endpoint with form data
4. **CSE API returns JSON** → Stock data, market info, announcements
5. **Server formats response** → Pretty-printed JSON text
6. **LLM receives data** → Can analyze, summarize, or answer user

## Component Details

### MCP Server (`main.py`)
- **Protocol:** Model Context Protocol 1.0+
- **Transport:** stdio (standard input/output)
- **HTTP Client:** httpx (async)
- **Error Handling:** HTTP exceptions, JSON parsing, timeouts

### Tool Schema
```python
{
  "name": "cse_get_company_info",
  "description": "Get detailed company info...",
  "inputSchema": {
    "type": "object",
    "properties": {
      "symbol": {"type": "string", "description": "..."}
    },
    "required": ["symbol"]
  }
}
```

### API Request
```python
POST https://www.cse.lk/api/companyInfoSummery
Content-Type: application/x-www-form-urlencoded

symbol=LOLC.N0000
```

### Response Format
```json
{
  "reqSymbolInfo": {
    "symbol": "LOLC.N0000",
    "name": "L O L C HOLDINGS PLC",
    "lastTradedPrice": 546.5,
    "marketCap": 259696800000
  }
}
```

## Security & Best Practices

✅ **Input Validation:** JSON schema validation on all tool inputs  
✅ **Error Handling:** Graceful degradation on API failures  
✅ **Timeouts:** 30-second timeout on HTTP requests  
✅ **Async I/O:** Non-blocking HTTP calls  
✅ **Logging:** Structured logging for debugging  
✅ **Type Safety:** Full type hints with Pydantic models  

## Performance Characteristics

- **Latency:** ~500ms - 2s per API call (network dependent)
- **Concurrency:** Async support for parallel tool calls
- **Rate Limiting:** None implemented (use CSE API responsibly)
- **Caching:** None implemented (always fresh data)

## Deployment Options

### 1. Local (Claude Desktop)
```json
{
  "mcpServers": {
    "cse-api": {
      "command": "python",
      "args": ["path/to/main.py"]
    }
  }
}
```

### 2. Remote (SSE Transport)
Future enhancement: Deploy as HTTP service with SSE transport

### 3. Container (Docker)
Future enhancement: Dockerize for cloud deployment

## Extension Points

Want to extend the server? Easy modification points:

1. **Add new endpoints** → Update `list_tools()` and `endpoint_map`
2. **Add caching** → Wrap `make_cse_request()` with cache decorator
3. **Add rate limiting** → Use `asyncio.Semaphore` in request handler
4. **Add authentication** → Add API key to request headers
5. **Add data validation** → Create Pydantic models for responses
6. **Add persistence** → Store historical data in SQLite/PostgreSQL

## Error Handling Strategy

```
User Query
    │
    ├─► Input Validation ─► Schema Error ──► Return error message
    │
    ├─► HTTP Request ──► Network Error ──► Log & return error
    │
    ├─► API Response ──► HTTP 4xx/5xx ──► Log & return error
    │
    ├─► JSON Parsing ──► Parse Error ──► Log & return error
    │
    └─► Success ──────────────────────────► Return formatted data
```

## Monitoring & Debugging

- **Logs:** Check console output for INFO/ERROR messages
- **MCP Inspector:** Use `npx @modelcontextprotocol/inspector`
- **Test Scripts:** Run `test_server.py` or `test_api.py`
- **Claude Desktop Dev Tools:** View → Developer → Toggle Developer Tools

---

**Ready to use!** The architecture is simple, extensible, and production-ready.
