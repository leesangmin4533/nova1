import pandas as pd


class MarketSentimentAgent:
    """Agent that classifies market sentiment into five levels."""

    LEVELS = ["EXTREME_FEAR", "FEAR", "NEUTRAL", "GREED", "EXTREME_GREED"]

    def __init__(self):
        self.state = "NEUTRAL"

    @staticmethod
    def rsi(series, period: int = 14):
        delta = series.diff()
        up = delta.clip(lower=0)
        down = -1 * delta.clip(upper=0)
        ma_up = up.rolling(window=period).mean()
        ma_down = down.rolling(window=period).mean()
        rs = ma_up / ma_down
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]

    def update(self, candle_data, order_book, trade_strength):
        """Update sentiment based on market data.

        Parameters
        ----------
        candle_data : list[dict]
            Each dict requires ``close`` and ``volume`` keys.
        order_book : dict
            Dict with ``bid_volume`` and ``ask_volume`` keys.
        trade_strength : float
            Placeholder for additional inputs.
        """

        df = pd.DataFrame(candle_data)
        if len(df) < 20:
            # not enough data, keep previous state
            return self.state

        rsi_val = self.rsi(df["close"])
        mean = df["close"].rolling(window=20).mean().iloc[-1]
        std = df["close"].rolling(window=20).std().iloc[-1]
        upper = mean + 2 * std
        lower = mean - 2 * std
        price = df["close"].iloc[-1]

        bid = order_book.get("bid_volume", 1)
        ask = order_book.get("ask_volume", 1)
        order_ratio = bid / max(ask, 1)

        if rsi_val > 80 or price > upper:
            self.state = "EXTREME_GREED"
        elif rsi_val > 70 or order_ratio > 1.5:
            self.state = "GREED"
        elif rsi_val < 20 or price < lower:
            self.state = "EXTREME_FEAR"
        elif rsi_val < 30 or order_ratio < 0.67:
            self.state = "FEAR"
        else:
            self.state = "NEUTRAL"
        return self.state
