# dhanhq_mcp.py

import os
import time
import json
import httpx
from fastmcp import FastMCP, Context

BASE_URL = "https://api.dhan.co/v2"  # v2 base URL :contentReference[oaicite:4]{index=4}

# Load credentials
CLIENT_ID = os.getenv("DHAN_CLIENT_ID")
ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")
HEADERS = {
    "Content-Type": "application/json",
    "client-id": CLIENT_ID,
    "access-token": ACCESS_TOKEN,
}

mcp = FastMCP("DhanHQ-v2")

def serialize(params: dict) -> dict:
    """Filter out None and JSON-encode lists."""
    return {k: (json.dumps(v) if isinstance(v, list) else v)
            for k, v in params.items() if v is not None}

async def call_api(ctx: Context, method: str, path: str, params=None, json_body=None):
    url = f"{BASE_URL}{path}"
    async with httpx.AsyncClient() as client:
        resp = await client.request(method, url, headers=HEADERS,
                                    params=serialize(params or {}),
                                    json=json_body)
        resp.raise_for_status()
        return resp.json()

# I. Order Management

@mcp.tool()
async def place_order(symbol: str, qty: float, price: float, side: str, product_type: str,
                      order_type: str, **kwargs) -> dict:
    """
    Place a regular order (Intraday/Delivery/Margin/CO/BO).
    """
    body = {"symbol": symbol, "quantity": qty, "price": price,
            "side": side, "productType": product_type, "orderType": order_type}
    body.update(kwargs)
    return await call_api(mcp.ctx, "POST", "/orders", json_body=body)  # :contentReference[oaicite:5]{index=5}

@mcp.tool()
async def place_super_order(symbol: str, qty: float, entry_price: float,
                            targets: list, stop_loss: float) -> dict:
    """Place a Super Order (entry + multiple targets + SL)."""
    body = {"symbol": symbol, "quantity": qty,
            "entryPrice": entry_price, "targets": targets, "stopLoss": stop_loss}
    return await call_api(mcp.ctx, "POST", "/super-order", json_body=body)  # :contentReference[oaicite:6]{index=6}

@mcp.tool()
async def place_forever_order(symbol: str, quantity: float, price: float,
                              side: str, oco: bool = False) -> dict:
    """Place a Forever Order (single or OCO)."""
    body = {"symbol": symbol, "quantity": quantity,
            "price": price, "side": side, "oco": oco}
    return await call_api(mcp.ctx, "POST", "/forever-order", json_body=body)  # :contentReference[oaicite:7]{index=7}

@mcp.tool()
async def get_order_book() -> dict:
    """Fetch today's orders (pending, executed, cancelled)."""
    return await call_api(mcp.ctx, "GET", "/orders")  # :contentReference[oaicite:8]{index=8}

# II. Market Data

@mcp.tool()
async def get_market_quote(symbols: list[str]) -> dict:
    """Fetch LTP, OI quote, market depth for up to 1000 instruments."""
    return await call_api(mcp.ctx, "GET", "/market-quote", params={"symbols": symbols})  # :contentReference[oaicite:9]{index=9}

@mcp.tool()
async def get_option_chain(underlying: str) -> dict:
    """Fetch full option chain (OI, Greeks, volume, bid/ask, price)."""
    return await call_api(mcp.ctx, "GET", "/option-chain", params={"underlying": underlying})  # :contentReference[oaicite:10]{index=10}

@mcp.tool()
async def get_historical_intraday(instrument: str, from_ts: int, to_ts: int,
                                  timeframe: str = "1m") -> dict:
    """
    Intraday historical OHLC+Volume for last 5 days, timeframes 1/5/15/25/60m.
    """
    params = {"instrument": instrument, "from": from_ts, "to": to_ts, "timeframe": timeframe}
    return await call_api(mcp.ctx, "POST", "/charts/intraday", json_body=params)  # :contentReference[oaicite:11]{index=11}

@mcp.tool()
async def get_historical_daily(instrument: str, from_date: str, to_date: str) -> dict:
    """
    Historical daily OHLC+Volume for last 5 years.
    """
    params = {"instrument": instrument, "from": from_date, "to": to_date}
    return await call_api(mcp.ctx, "POST", "/charts/daily", json_body=params)  # :contentReference[oaicite:12]{index=12}

# III. Account Information

@mcp.tool()
async def get_fund_balance() -> dict:
    """Fetch account balance, margin utilization, and available funds."""
    return await call_api(mcp.ctx, "GET", "/user/funds")

@mcp.tool()
async def get_account_details() -> dict:
    """Fetch complete account information including KYC status."""
    return await call_api(mcp.ctx, "GET", "/user/profile")

# IV. Portfolio Management

@mcp.tool()
async def get_holdings() -> dict:
    """Fetch current holdings with current market value and P&L."""
    return await call_api(mcp.ctx, "GET", "/holdings")

@mcp.tool()
async def get_positions() -> dict:
    """Fetch current day's positions with P&L."""
    return await call_api(mcp.ctx, "GET", "/positions")

@mcp.tool()
async def get_portfolio_summary() -> dict:
    """Fetch summary of holdings and positions with overall P&L."""
    return await call_api(mcp.ctx, "GET", "/portfolio/summary")

# V. Margin Calculator

@mcp.tool()
async def calculate_margin(symbol: str, qty: float, price: float, 
                         order_type: str = "LIMIT", product_type: str = "INTRADAY") -> dict:
    """Calculate margin required for a potential trade."""
    body = {
        "symbol": symbol,
        "quantity": qty,
        "price": price,
        "orderType": order_type,
        "productType": product_type
    }
    return await call_api(mcp.ctx, "POST", "/margin/calculate", json_body=body)

@mcp.tool()
async def get_margin_benefits(symbols: list[str]) -> dict:
    """Get margin benefits for a list of symbols."""
    return await call_api(mcp.ctx, "GET", "/margin/benefits", params={"symbols": symbols})

# VI. After-Market Orders

@mcp.tool()
async def place_after_market_order(symbol: str, qty: float, price: float, 
                                side: str, product_type: str = "DELIVERY") -> dict:
    """
    Place an order to be executed in the after-market session.
    Only available for equity delivery orders.
    """
    body = {
        "symbol": symbol,
        "quantity": qty,
        "price": price,
        "side": side,
        "productType": product_type,
        "afterMarket": True
    }
    return await call_api(mcp.ctx, "POST", "/orders", json_body=body)

@mcp.tool()
async def get_after_market_eligibility(symbols: list[str]) -> dict:
    """Check if symbols are eligible for after-market orders."""
    return await call_api(mcp.ctx, "GET", "/market/after-hours-eligibility", 
                         params={"symbols": symbols})

if __name__ == "__main__":
    # For local testing
    mcp.run(host="127.0.0.1", port=8000)
