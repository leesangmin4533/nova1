class EntryDecisionAgent:
    """Determine trade entry signals."""

    def __init__(self):
        pass

    def evaluate(self, strategy, chart_data, order_status):
        """Return BUY, SELL, or HOLD signal based on the strategy."""
        name = strategy[0] if isinstance(strategy, tuple) else strategy
        if not chart_data:
            return "HOLD"

        recent_close = chart_data[-1]
        avg5 = sum(chart_data[-5:]) / 5

        if name == "momentum" and recent_close > avg5:
            return "BUY"
        if name == "reversal" and recent_close < avg5:
            return "BUY"

        if name == "take_profit" and order_status and order_status.get("has_position"):
            if order_status.get("return_rate", 0) >= 0.05:
                return "SELL"

        return "HOLD"
