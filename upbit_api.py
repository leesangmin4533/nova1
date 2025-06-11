import requests
from typing import Dict, Any


def get_orderbook(market: str = "KRW-BTC", depth: int = 5) -> Dict[str, Any]:
    """Return simplified orderbook snapshot from Upbit."""
    url = "https://api.upbit.com/v1/orderbook"
    params = {"markets": market}
    response = requests.get(url, params=params, timeout=5)
    response.raise_for_status()
    data = response.json()[0]
    units = data.get("orderbook_units", [])[:depth]
    bids = [{"price": u["bid_price"], "volume": u["bid_size"]} for u in units]
    asks = [{"price": u["ask_price"], "volume": u["ask_size"]} for u in units]
    return {"bids": bids, "asks": asks, "bid_volume": data.get("total_bid_size"), "ask_volume": data.get("total_ask_size")}


def get_current_price(market: str = "KRW-BTC") -> Dict[str, Any]:
    """Return current trade price and change rate."""
    url = "https://api.upbit.com/v1/ticker"
    params = {"markets": market}
    response = requests.get(url, params=params, timeout=5)
    response.raise_for_status()
    data = response.json()[0]
    return {
        "trade_price": data.get("trade_price"),
        "signed_change_rate": data.get("signed_change_rate"),
    }
