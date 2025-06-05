import requests


class MarketSentimentAgent:
    """Agent that classifies market sentiment into five levels using Upbit data."""

    LEVELS = ["EXTREME_FEAR", "FEAR", "NEUTRAL", "GREED", "EXTREME_GREED"]

    def __init__(self):
        self.state = "NEUTRAL"

    def update(self, candle_data=None, order_book=None, trade_strength=None):
        """Update sentiment based on market data fetched from Upbit."""
        if candle_data is None:
            try:
                resp = requests.get(
                    "https://api.upbit.com/v1/candles/minutes/1",
                    params={"market": "KRW-BTC", "count": 1},
                    timeout=5,
                )
                resp.raise_for_status()
                candle_data = resp.json()[0]
            except Exception as exc:  # network or parsing errors
                print(f"Failed to fetch Upbit data: {exc}")
                candle_data = None

        if candle_data:
            open_price = candle_data.get("opening_price", 0)
            trade_price = candle_data.get("trade_price", 0)
            change_rate = (trade_price - open_price) / open_price if open_price else 0
            if change_rate > 0.01:
                self.state = self.LEVELS[4]
            elif change_rate > 0:
                self.state = self.LEVELS[3]
            elif change_rate < -0.01:
                self.state = self.LEVELS[0]
            elif change_rate < 0:
                self.state = self.LEVELS[1]
            else:
                self.state = self.LEVELS[2]
        else:
            self.state = self.LEVELS[2]

        return self.state
