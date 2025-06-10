"""Utility functions for fetching market data."""

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover - fallback for minimal environments
    class _DummyRequests:
        class RequestException(Exception):
            pass

        @staticmethod
        def get(*_, **__):
            raise _DummyRequests.RequestException("requests library not available")

    requests = _DummyRequests()
import time
from typing import List, Dict, Any


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
            raise RuntimeError(f"캔들 데이터를 가져오지 못했습니다: {exc}") from exc


def get_upbit_orderbook(symbol: str = "KRW-BTC", depth: int = 10) -> Dict[str, Any]:
    """Fetch orderbook snapshot from Upbit with depth information."""
    url = "https://api.upbit.com/v1/orderbook"
    params = {"markets": symbol}
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()[0]
        units = data.get("orderbook_units", [])[:depth]
        bids = [
            {"price": u["bid_price"], "volume": u["bid_size"]}
            for u in units
        ]
        asks = [
            {"price": u["ask_price"], "volume": u["ask_size"]}
            for u in units
        ]
        bid_volume = sum(u["bid_size"] for u in units)
        ask_volume = sum(u["ask_size"] for u in units)
        return {
            "bids": bids,
            "asks": asks,
            "bid_volume": bid_volume,
            "ask_volume": ask_volume,
        }
    except requests.RequestException as exc:
        raise RuntimeError(f"호가 정보를 가져오지 못했습니다: {exc}") from exc

