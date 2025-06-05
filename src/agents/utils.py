import requests
import time
from typing import List


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

