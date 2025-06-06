class EntryDecisionAgent:
    """Determine trade entry signals."""

    def __init__(self):
        pass

    def evaluate(self, strategy, chart_data, order_status):
        """Return BUY, SELL, or HOLD signal based on the strategy."""
        name = strategy[0] if isinstance(strategy, tuple) else strategy
        if not chart_data or len(chart_data) < 20:
            return "HOLD"

        recent_close = chart_data[-1]
        ma5 = sum(chart_data[-5:]) / 5
        ma20 = sum(chart_data[-20:]) / 20

        rsi = self._calc_rsi(chart_data)

        golden_cross = ma5 > ma20 and chart_data[-6] <= sum(chart_data[-25:-5]) / 20

        if name in ["momentum", "trend_follow"]:
            if golden_cross and rsi > 55:
                return "BUY"
        if name == "reversal" and recent_close < ma5:
            return "BUY"

        if name == "take_profit" and order_status and order_status.get("has_position"):
            if order_status.get("return_rate", 0) >= 0.05:
                return "SELL"

        return "HOLD"

    def _calc_rsi(self, closes, period=14):
        if len(closes) < period + 1:
            return 50.0
        gains = []
        losses = []
        for i in range(1, period + 1):
            diff = closes[-i] - closes[-i - 1]
            if diff > 0:
                gains.append(diff)
            else:
                losses.append(abs(diff))
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
