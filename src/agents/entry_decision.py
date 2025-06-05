class EntryDecisionAgent:
    """Determine trade entry signals."""

    def __init__(self):
        pass

    def evaluate(self, strategy, chart_data, order_status):
        """Return BUY, SELL, or HOLD signal."""
        strat_id, params = strategy
        closes = [c["close"] for c in chart_data]

        def sma(data, length):
            if len(data) < length:
                return None
            return sum(data[-length:]) / length

        if strat_id == "trend_follow" and len(closes) >= 20:
            short = sma(closes, 5)
            long = sma(closes, 20)
            prev_short = sma(closes[:-1], 5)
            prev_long = sma(closes[:-1], 20)
            rsi = params.get("rsi", 50)
            if prev_short and prev_long:
                if prev_short < prev_long and short >= long and rsi > 55:
                    return "BUY"
                if prev_short > prev_long and short <= long and rsi < 45:
                    return "SELL"

        return "HOLD"
