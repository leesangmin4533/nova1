"""Market sentiment classification agent."""

from statistics import mean, stdev


class MarketSentimentAgent:
    """Classify market sentiment into five discrete levels."""

    LEVELS = ["EXTREME_FEAR", "FEAR", "NEUTRAL", "GREED", "EXTREME_GREED"]

    def __init__(self):
        self.state = "NEUTRAL"

    def _rsi(self, closes, period=14):
        if len(closes) < period + 1:
            return 50.0
        gains = []
        losses = []
        for i in range(1, period + 1):
            diff = closes[-i] - closes[-i - 1]
            if diff >= 0:
                gains.append(diff)
            else:
                losses.append(abs(diff))
        avg_gain = sum(gains) / period if gains else 0.0
        avg_loss = sum(losses) / period if losses else 1e-9
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def update(self, candle_data, order_book, trade_strength):
        """Update sentiment based on market data."""
        closes = [c["close"] for c in candle_data]
        volumes = [c["volume"] for c in candle_data]

        rsi = self._rsi(closes)
        vol_change = 0.0
        if len(volumes) >= 2 and volumes[-2] > 0:
            vol_change = (volumes[-1] - volumes[-2]) / volumes[-2]

        bid = order_book.get("bid_volume", 0.0)
        ask = order_book.get("ask_volume", 1e-9)
        order_ratio = bid / ask

        lookback_prices = closes[-20:] if len(closes) >= 20 else closes
        avg_price = mean(lookback_prices)
        if len(lookback_prices) > 1:
            std_price = stdev(lookback_prices)
        else:
            std_price = 0.0
        upper = avg_price + 2 * std_price
        lower = avg_price - 2 * std_price
        bb_signal = 1 if closes[-1] > upper else -1 if closes[-1] < lower else 0

        score = (
            vol_change * 0.2
            + (rsi - 50) / 50 * 0.3
            + (order_ratio - 1) * 0.3
            + bb_signal * 0.2
        )

        if score <= -0.6:
            self.state = self.LEVELS[0]
        elif score <= -0.2:
            self.state = self.LEVELS[1]
        elif score < 0.2:
            self.state = self.LEVELS[2]
        elif score < 0.6:
            self.state = self.LEVELS[3]
        else:
            self.state = self.LEVELS[4]

        return self.state
