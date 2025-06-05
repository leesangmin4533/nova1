class LearningAgent:
    """Agent that updates strategy weights based on performance."""

    def __init__(self):
        self.weights = {}

    def update(self, trade_history):
        """Update strategy weights based on trade history."""
        totals = {}
        counts = {}
        for trade in trade_history:
            name = trade.get("strategy")
            ret = trade.get("return", 0)
            totals[name] = totals.get(name, 0) + ret
            counts[name] = counts.get(name, 0) + 1

        self.weights = {
            name: totals[name] / counts[name]
            for name in totals
            if counts[name] > 0
        }
        return self.weights
