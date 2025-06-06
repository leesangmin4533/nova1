import requests
import time
from typing import List, Dict


def get_upbit_candles(symbol: str = "KRW-BTC", count: int = 20) -> List[float]:
    """Fetch minute candles from Upbit and return a list of closing prices."""
    url = "https://api.upbit.com/v1/candles/minutes/1"
    params = {"market": symbol, "count": count}
    while True:
        try:
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 429:
                time.sleep(1)
                continue
            response.raise_for_status()
            data = response.json()
            closes = [candle["trade_price"] for candle in reversed(data)]
            return closes
        except requests.RequestException as exc:
            raise RuntimeError(f"Failed to fetch candles: {exc}") from exc


def get_upbit_orderbook(symbol: str = "KRW-BTC") -> Dict[str, float]:
    """Fetch orderbook snapshot from Upbit."""
    url = "https://api.upbit.com/v1/orderbook"
    params = {"markets": symbol}
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()[0]
        bid_volume = sum(item["bid_size"] for item in data.get("orderbook_units", []))
        ask_volume = sum(item["ask_size"] for item in data.get("orderbook_units", []))
        return {"bid_volume": bid_volume, "ask_volume": ask_volume}
    except requests.RequestException as exc:
        raise RuntimeError(f"Failed to fetch orderbook: {exc}") from exc

