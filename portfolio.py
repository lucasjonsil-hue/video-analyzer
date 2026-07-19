"""Portfolio tracker v1 (spec: ROADMAP.md, Investment module step 2).

Holdings live in local portfolio.json (gitignored — personal financial data),
quotes come from Yahoo Finance via yfinance (free, no API key). Endpoints are
sync `def` so FastAPI runs the blocking yfinance calls in its threadpool.

- GET /api/portfolio: holdings enriched with live price/value/gain/allocation
- POST /api/portfolio/holdings: upsert {ticker, shares, avg_cost}
- DELETE /api/portfolio/holdings/{ticker}
- Quotes are cached for 2 minutes per ticker to keep page reloads fast.
"""

import json
import os
import time
from datetime import datetime, timezone

import yfinance as yf
from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import JSONResponse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PORTFOLIO_PATH = os.path.join(BASE_DIR, "portfolio.json")

QUOTE_CACHE_SECONDS = 120
_quote_cache: dict[str, tuple[float, float]] = {}  # ticker -> (fetched_at, price)


def _load() -> dict:
    if os.path.exists(PORTFOLIO_PATH):
        with open(PORTFOLIO_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"holdings": []}


def _save(data: dict) -> None:
    with open(PORTFOLIO_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _get_price(ticker: str) -> float | None:
    cached = _quote_cache.get(ticker)
    if cached and time.time() - cached[0] < QUOTE_CACHE_SECONDS:
        return cached[1]
    try:
        price = yf.Ticker(ticker).fast_info.last_price
        if price is None:
            return None
        price = float(price)
    except Exception:
        return None
    _quote_cache[ticker] = (time.time(), price)
    return price


def _enriched() -> dict:
    data = _load()
    holdings = []
    total_value = 0.0
    total_cost = 0.0
    for h in data["holdings"]:
        price = _get_price(h["ticker"])
        cost = h["shares"] * h["avg_cost"]
        value = h["shares"] * price if price is not None else None
        holdings.append({
            **h,
            "price": price,
            "cost": cost,
            "value": value,
            "gain": (value - cost) if value is not None else None,
        })
        total_cost += cost
        if value is not None:
            total_value += value
    for h in holdings:
        h["allocation"] = (h["value"] / total_value * 100) if h["value"] and total_value else None
    return {
        "holdings": holdings,
        "total_value": total_value,
        "total_cost": total_cost,
        "total_gain": total_value - total_cost if holdings else 0.0,
        "as_of": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


router = APIRouter()


@router.get("/api/portfolio")
def get_portfolio():
    return JSONResponse(content=_enriched())


@router.post("/api/portfolio/holdings")
def add_holding(payload: dict = Body(...)):
    ticker = (payload.get("ticker") or "").strip().upper()
    if not ticker:
        raise HTTPException(status_code=422, detail="ticker is required")
    try:
        shares = float(payload.get("shares"))
        avg_cost = float(payload.get("avg_cost"))
    except (TypeError, ValueError):
        raise HTTPException(status_code=422, detail="shares and avg cost must be numbers")
    if shares <= 0 or avg_cost < 0:
        raise HTTPException(status_code=422, detail="shares must be positive and avg cost non-negative")
    if _get_price(ticker) is None:
        raise HTTPException(status_code=422, detail=f"no Yahoo Finance quote found for '{ticker}' — check the symbol")

    data = _load()
    data["holdings"] = [h for h in data["holdings"] if h["ticker"] != ticker]
    data["holdings"].append({
        "ticker": ticker,
        "shares": shares,
        "avg_cost": avg_cost,
        "added": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    })
    data["holdings"].sort(key=lambda h: h["ticker"])
    _save(data)
    return JSONResponse(content=_enriched())


@router.delete("/api/portfolio/holdings/{ticker}")
def delete_holding(ticker: str):
    data = _load()
    remaining = [h for h in data["holdings"] if h["ticker"] != ticker.upper()]
    if len(remaining) == len(data["holdings"]):
        raise HTTPException(status_code=404, detail="holding not found")
    data["holdings"] = remaining
    _save(data)
    return JSONResponse(content=_enriched())
