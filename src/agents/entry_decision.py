class EntryDecisionAgent:
    """Determine trade entry signals using simple moving average crossover."""

    def __init__(self, short_window=5, long_window=10):
        self.short_window = short_window
        self.long_window = long_window
        self.prev_short = None
        self.prev_long = None

    def evaluate(self, strategy, chart_data, order_status):
        """Return BUY, SELL, or HOLD signal based on moving average crossover."""
        if not chart_data or len(chart_data) < self.long_window:
            return "HOLD"

        short_ma = sum(chart_data[-self.short_window:]) / self.short_window
        long_ma = sum(chart_data[-self.long_window:]) / self.long_window

        signal = "HOLD"
        prev_short = self.prev_short
        prev_long = self.prev_long
        if prev_short is not None and prev_long is not None:
            if prev_short <= prev_long and short_ma > long_ma:
                signal = "BUY"
            elif prev_short >= prev_long and short_ma < long_ma:
                signal = "SELL"

        self.prev_short = short_ma
        self.prev_long = long_ma
        return signal
