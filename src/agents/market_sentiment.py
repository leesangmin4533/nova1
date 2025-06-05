import requests


class MarketSentimentAgent:
    """Agent that classifies market sentiment into five levels."""

    LEVELS = ["EXTREME_FEAR", "FEAR", "NEUTRAL", "GREED", "EXTREME_GREED"]

    def __init__(self):
        self.state = "NEUTRAL"

    def update(self, candle_data, order_book, trade_strength):
        """Update sentiment based on market data."""
        # TODO: implement actual indicators
        self.state = self.LEVELS[2]
        return self.state

    @staticmethod
    def get_current_price(ticker="KRW-BTC"):
        """Return the latest trade price from Upbit API."""
        url = f"https://api.upbit.com/v1/ticker?markets={ticker}"
        try:
            resp = requests.get(url, timeout=5)
            data = resp.json()
            return data[0].get("trade_price") if data else None
        except Exception:
            return None
