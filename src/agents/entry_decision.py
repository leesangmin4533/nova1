from collections import deque


class EntryDecisionAgent:
    """Determine trade entry signals for scalping strategies."""

    def __init__(self):
        self.close_history = deque(maxlen=50)

    def _moving_average(self, data, length):
        if len(data) < length:
            return None
        return sum(list(data)[-length:]) / length

    def _rsi(self, closes, period=14):
        if len(closes) < period + 1:
            return 50
        gains = []
        losses = []
        closes = list(closes)
        for i in range(1, period + 1):
            delta = closes[-i] - closes[-i - 1]
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

    def evaluate(self, strategy, chart_data, order_status):
        """Return BUY, SELL, or HOLD signal."""
        if chart_data is None:
            return "HOLD"

        price = chart_data.get("close")
        if price is None:
            return "HOLD"
        self.close_history.append(price)

        short_ma = self._moving_average(self.close_history, 5)
        long_ma = self._moving_average(self.close_history, 20)
        rsi = self._rsi(self.close_history)

        if short_ma is None or long_ma is None:
            return "HOLD"

        if short_ma > long_ma and rsi > 55:
            return "BUY"
        if short_ma < long_ma and rsi < 45:
            return "SELL"
        return "HOLD"
