"""
CSE API MCP Server
Exposes Colombo Stock Exchange API endpoints as MCP tools for LLM integration
"""

import asyncio
import logging
from typing import Any, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cse-mcp-server")

# CSE API Base URL
CSE_BASE_URL = "https://www.cse.lk/api/"

# Initialize MCP server
app = Server("cse-api-server")


async def make_cse_request(endpoint: str, data: Optional[dict] = None) -> dict:
    """
    Make a POST request to CSE API endpoint
    
    Args:
        endpoint: API endpoint name
        data: Optional form data to send with request
        
    Returns:
        JSON response from API
    """
    url = f"{CSE_BASE_URL}{endpoint}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                url,
                data=data or {},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling {endpoint}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error calling {endpoint}: {e}")
            raise


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available CSE API tools"""
    return [
        Tool(
            name="cse_get_company_info",
            description="Get detailed information for a specific company/stock by symbol. Returns company name, last traded price, change, change percentage, market cap, beta value, and logo path.",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., 'LOLC.N0000', 'ABAN.N0000')"
                    }
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="cse_get_trade_summary",
            description="Get summary of trades for all securities. Returns array of all traded securities with their symbols, prices, volumes, and changes.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="cse_get_today_share_price",
            description="Get today's share price data for all securities. Returns current prices, changes, and trading information.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="cse_get_top_gainers",
            description="Get list of top gaining stocks for the day. Returns stocks with highest positive percentage changes.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="cse_get_top_losers",
            description="Get list of top losing stocks for the day. Returns stocks with highest negative percentage changes.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="cse_get_most_active_trades",
            description="Get most active trades by volume. Returns stocks with highest trading volumes.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="cse_get_new_listings_announcements",
            description="Get new listings and related notices/announcements from CSE.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="cse_get_buy_in_board_announcements",
            description="Get buy-in board announcements from CSE trading and market surveillance.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="cse_get_approved_announcements",
            description="Get approved company announcements and disclosures.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="cse_get_covid_announcements",
            description="Get COVID-related announcements from listed companies.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="cse_get_financial_announcements",
            description="Get financial announcements including annual reports, quarterly results, and financial statements.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="cse_get_circular_announcements",
            description="Get circular announcements from CSE including regulatory circulars and notices.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="cse_get_directive_announcements",
            description="Get directive announcements issued by CSE regulatory authorities.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="cse_get_non_compliance_announcements",
            description="Get non-compliance announcements for companies not meeting CSE requirements.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="cse_get_market_status",
            description="Get current market status (Market Open/Closed).",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="cse_get_market_summary",
            description="Get comprehensive market summary including trade volume, share volume, turnover, and market statistics.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="cse_get_aspi_data",
            description="Get All Share Price Index (ASPI) data including current value, change, and percentage change.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="cse_get_snp_data",
            description="Get S&P Sri Lanka 20 Index data including current value, change, and percentage change.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="cse_get_chart_data",
            description="Get historical chart/price data for a specific stock symbol. May return time series data for technical analysis.",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., 'LOLC.N0000')"
                    }
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="cse_get_all_sectors",
            description="Get data for all market sectors/industry groups with their indices and performance.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="cse_get_detailed_trades",
            description="Get detailed trade information for securities. Can filter by symbol or get all detailed trades.",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Optional stock symbol to filter trades (e.g., 'ABAN.N0000')"
                    }
                }
            }
        ),
        Tool(
            name="cse_get_daily_market_summary",
            description="Get daily market summary with comprehensive statistics including turnover, trades, market cap, indices (ASI, S&P), P/E ratio, P/BV, dividend yield, CDS holdings, and more. Historical daily data.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls and route to appropriate CSE API endpoint"""
    
    try:
        # Map tool names to API endpoints
        endpoint_map = {
            "cse_get_company_info": ("companyInfoSummery", {"symbol": arguments.get("symbol")}),
            "cse_get_trade_summary": ("tradeSummary", {}),
            "cse_get_today_share_price": ("todaySharePrice", {}),
            "cse_get_top_gainers": ("topGainers", {}),
            "cse_get_top_losers": ("topLooses", {}),
            "cse_get_most_active_trades": ("mostActiveTrades", {}),
            "cse_get_new_listings_announcements": ("getNewListingsRelatedNoticesAnnouncements", {}),
            "cse_get_buy_in_board_announcements": ("getBuyInBoardAnnouncements", {}),
            "cse_get_approved_announcements": ("approvedAnnouncement", {}),
            "cse_get_covid_announcements": ("getCOVIDAnnouncements", {}),
            "cse_get_financial_announcements": ("getFinancialAnnouncement", {}),
            "cse_get_circular_announcements": ("circularAnnouncement", {}),
            "cse_get_directive_announcements": ("directiveAnnouncement", {}),
            "cse_get_non_compliance_announcements": ("getNonComplianceAnnouncements", {}),
            "cse_get_market_status": ("marketStatus", {}),
            "cse_get_market_summary": ("marketSummery", {}),
            "cse_get_aspi_data": ("aspiData", {}),
            "cse_get_snp_data": ("snpData", {}),
            "cse_get_chart_data": ("chartData", {"symbol": arguments.get("symbol")}),
            "cse_get_all_sectors": ("allSectors", {}),
            "cse_get_detailed_trades": ("detailedTrades", {"symbol": arguments.get("symbol")} if arguments.get("symbol") else {}),
            "cse_get_daily_market_summary": ("dailyMarketSummery", {}),
        }
        
        if name not in endpoint_map:
            return [TextContent(
                type="text",
                text=f"Error: Unknown tool '{name}'"
            )]
        
        endpoint, data = endpoint_map[name]
        
        # Make API request
        result = await make_cse_request(endpoint, data)
        
        # Return formatted response
        import json
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, ensure_ascii=False)
        )]
        
    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP {e.response.status_code} error: {e.response.text}"
        logger.error(error_msg)
        return [TextContent(
            type="text",
            text=f"Error calling CSE API: {error_msg}"
        )]
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return [TextContent(
            type="text",
            text=f"Error: {error_msg}"
        )]


async def main():
    """Run the MCP server"""
    logger.info("Starting CSE API MCP Server...")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
