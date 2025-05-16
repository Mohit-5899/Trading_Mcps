# binance_mcp.py

from typing import Any, List, Optional
import json
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("binance-trade")

# Base URL for Binance REST API
BASE_URL = "https://api.binance.com/api/v3/"

def serialize_params(params: dict[str, Any]) -> dict[str, Any]:
    """
    Convert list-valued params to JSON strings and filter out None values.
    """
    out: dict[str, Any] = {}
    for k, v in params.items():
        if v is None:
            continue
        out[k] = json.dumps(v) if isinstance(v, list) else v
    return out

@mcp.tool()
async def ExchangeInfoOfASymbol(symbol: str) -> str:
    """Get exchange info for a single symbol."""  
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}exchangeInfo", params={"symbol": symbol})
        resp.raise_for_status()
        return resp.text

@mcp.tool()
async def ExchangeInfoOfAllSymbols() -> str:
    """Get exchange info for all symbols."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}exchangeInfo")
        resp.raise_for_status()
        return resp.text

@mcp.tool()
async def getTradeData(
    symbol: str,
    interval: str,
    startTime: Optional[int] = None,
    endTime: Optional[int] = None,
    limit:    Optional[int] = None,
) -> str:
    """Get kline/candlestick data for a symbol."""
    params = serialize_params({
        "symbol":    symbol,
        "interval":  interval,
        "startTime": startTime,
        "endTime":   endTime,
        "limit":     limit,
    })
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}klines", params=params)
        resp.raise_for_status()
        return resp.text

@mcp.tool()
async def AggTrades(symbol: str, limit: int = 20) -> str:
    """Get recent aggregated trades (default limit=20)."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}aggTrades", params={"symbol": symbol, "limit": limit})
        resp.raise_for_status()
        return resp.text

@mcp.tool()
async def TradeHistory(symbol: str, limit: int = 20) -> str:
    """Get recent trade history (default limit=20)."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}historicalTrades", params={"symbol": symbol, "limit": limit})
        resp.raise_for_status()
        return resp.text

@mcp.tool()
async def Depth(symbol: str) -> str:
    """Get current order book depth."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}depth", params={"symbol": symbol})
        resp.raise_for_status()
        return resp.text

@mcp.tool()
async def CurrentAvgPrice(symbol: str) -> str:
    """Get current average price."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}avgPrice", params={"symbol": symbol})
        resp.raise_for_status()
        return resp.text

@mcp.tool()
async def PriceTickerIn24Hr(symbol: str) -> str:
    """Get 24hr price ticker statistics."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}ticker/24hr", params={"symbol": symbol})
        resp.raise_for_status()
        return resp.text

@mcp.tool()
async def TradingDayTicker(symbols: List[str]) -> str:
    """Get trading day ticker for multiple symbols."""
    params = serialize_params({"symbols": symbols})
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}ticker/tradingDay", params=params)
        resp.raise_for_status()
        return resp.text

@mcp.tool()
async def SymbolPriceTicker(
    symbol:  Optional[str]       = None,
    symbols: Optional[List[str]] = None,
) -> str:
    """Get price ticker for one or more symbols."""
    params = serialize_params({"symbol": symbol, "symbols": symbols})
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}ticker/price", params=params)
        resp.raise_for_status()
        return resp.text

@mcp.tool()
async def SymbolOrderBookTicker(
    symbol:  Optional[str]       = None,
    symbols: Optional[List[str]] = None,
) -> str:
    """Get order book ticker for one or more symbols."""
    params = serialize_params({"symbol": symbol, "symbols": symbols})
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}ticker/bookTicker", params=params)
        resp.raise_for_status()
        return resp.text

@mcp.tool()
async def RollingWindowTicker(
    symbol:     Optional[str]       = None,
    symbols:    Optional[List[str]] = None,
    windowSize: Optional[str]       = None,
    type:       Optional[str]       = None,  # "FULL" or "MINI"
) -> str:
    """Get rolling window ticker data."""
    params = serialize_params({
        "symbol":     symbol,
        "symbols":    symbols,
        "windowSize": windowSize,
        "type":       type,
    })
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}ticker", params=params)
        resp.raise_for_status()
        return resp.text

if __name__ == "__main__":
    # Starts listening on stdio by default
    mcp.run()
