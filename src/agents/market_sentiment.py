class MarketSentimentAgent:
    """Agent that classifies market sentiment into five levels."""

    LEVELS = ["EXTREME_FEAR", "FEAR", "NEUTRAL", "GREED", "EXTREME_GREED"]

    def __init__(self):
        self.state = "NEUTRAL"

    def _rsi(self, closes, period=14):
        """Return the Relative Strength Index for a sequence of closes."""
        if len(closes) < period + 1:
            return 50.0
        gains = []
        losses = []
        for i in range(-period, 0):
            change = closes[i] - closes[i - 1]
            if change >= 0:
                gains.append(change)
            else:
                losses.append(-change)
        avg_gain = sum(gains) / period if gains else 0
        avg_loss = sum(losses) / period if losses else 0
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def _bollinger(self, closes, period=20, num_std=2):
        """Return Bollinger Band upper and lower values."""
        if not closes:
            return 0.0, 0.0
        sample = closes[-period:]
        sma = sum(sample) / len(sample)
        mean = sma
        variance = sum((p - mean) ** 2 for p in sample) / len(sample)
        std = variance ** 0.5
        upper = sma + num_std * std
        lower = sma - num_std * std
        return upper, lower

    def update(self, candle_data, order_book, trade_strength):
        """Update sentiment based on market data.

        Parameters
        ----------
        candle_data : list of dict
            Each dict should contain `close` and `volume` keys.
        order_book : dict
            Should contain `bid_volume` and `ask_volume` keys.
        trade_strength : float
            Recent trade strength or execution ratio. Values above 1 indicate
            aggressive buying and below 1 indicate selling pressure.
        """
        closes = [c['close'] for c in candle_data] if candle_data else []
        volumes = [c.get('volume', 0) for c in candle_data] if candle_data else []
        if len(closes) < 2:
            self.state = self.LEVELS[2]
            return self.state

        rsi = self._rsi(closes)
        upper, lower = self._bollinger(closes)
        price = closes[-1]
        vol_change = 0.0
        if len(volumes) >= 2 and volumes[-2] != 0:
            vol_change = (volumes[-1] - volumes[-2]) / volumes[-2]
        bid = order_book.get('bid_volume', 0) if order_book else 0
        ask = order_book.get('ask_volume', 0) if order_book else 0
        book_ratio = (bid / ask) if ask else float('inf')
        strength = trade_strength if trade_strength is not None else 1.0

        score = 0
        if rsi > 70:
            score += 1
        elif rsi < 30:
            score -= 1

        if price > upper:
            score += 1
        elif price < lower:
            score -= 1

        if vol_change > 0:
            score += 1
        elif vol_change < 0:
            score -= 1

        if book_ratio > 1.1:
            score += 1
        elif book_ratio < 0.9:
            score -= 1

        if strength > 1.05:
            score += 1
        elif strength < 0.95:
            score -= 1

        if score <= -3:
            idx = 0
        elif score == -2 or score == -1:
            idx = 1
        elif score == 0:
            idx = 2
        elif score == 1 or score == 2:
            idx = 3
        else:
            idx = 4

        self.state = self.LEVELS[idx]
        return self.state
