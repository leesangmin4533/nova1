class LearningAgent:
    """Agent that updates strategy weights based on performance."""

    def __init__(self):
        self.weights = {
            "reversal": 1.0,
            "swing": 1.0,
            "trend_follow": 1.0,
            "momentum": 1.0,
            "take_profit": 1.0,
            "hold": 1.0,
        }

    def update(self, trade_history):
        """Update strategy weights based on average profit."""
        stats = {}
        for strategy_id, profit in trade_history:
            stats.setdefault(strategy_id, []).append(profit)

        for strategy_id, profits in stats.items():
            avg_profit = sum(profits) / len(profits)
            self.weights[strategy_id] = avg_profit

        return self.weights
