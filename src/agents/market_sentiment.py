import statistics
from collections import deque


class MarketSentimentAgent:
    """Agent that classifies market sentiment into five levels for scalping."""

    LEVELS = ["EXTREME_FEAR", "FEAR", "NEUTRAL", "GREED", "EXTREME_GREED"]

    def __init__(self):
        self.state = "NEUTRAL"
        self.prices = deque(maxlen=20)
        self.volumes = deque(maxlen=20)

    def _rsi(self, closes, period=14):
        if len(closes) < period + 1:
            return 50
        gains = []
        losses = []
        for i in range(-period, 0):
            delta = closes[i] - closes[i - 1]
            if delta >= 0:
                gains.append(delta)
            else:
                losses.append(-delta)
        avg_gain = sum(gains) / period if gains else 0
        avg_loss = sum(losses) / period if losses else 0
        if avg_loss == 0:
            return 100
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def _bollinger_break(self, closes, period=20, std_dev=2):
        if len(closes) < period:
            return 0
        sma = statistics.mean(closes[-period:])
        std = statistics.stdev(closes[-period:])
        upper = sma + std_dev * std
        lower = sma - std_dev * std
        last_price = closes[-1]
        if last_price > upper:
            return 1
        if last_price < lower:
            return -1
        return 0

    def update(self, candle_data, order_book, trade_strength):
        """Update sentiment based on market data."""
        if candle_data:
            close = candle_data[-1].get("close")
            volume = candle_data[-1].get("volume")
            if close is not None:
                self.prices.append(close)
            if volume is not None:
                self.volumes.append(volume)

        closes = list(self.prices)
        rsi = self._rsi(closes)
        volume_change = 0.0
        if len(self.volumes) > 1 and self.volumes[-2] > 0:
            volume_change = (self.volumes[-1] - self.volumes[-2]) / self.volumes[-2]

        book_ratio = 0.0
        if order_book:
            bid = order_book.get("bid", 0)
            ask = order_book.get("ask", 0)
            total = bid + ask
            if total > 0:
                book_ratio = (bid - ask) / total

        bb_break = self._bollinger_break(closes)

        score = rsi / 100 + volume_change + book_ratio + bb_break

        if score < -1:
            self.state = self.LEVELS[0]
        elif score < -0.5:
            self.state = self.LEVELS[1]
        elif score < 0.5:
            self.state = self.LEVELS[2]
        elif score < 1:
            self.state = self.LEVELS[3]
        else:
            self.state = self.LEVELS[4]

        return self.state
