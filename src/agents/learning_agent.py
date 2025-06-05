class LearningAgent:
    """Agent that updates strategy weights based on performance."""

    def __init__(self):
        self.weights = {}

    def update(self, trade_history):
        """Update strategy weights based on trade history."""
        perf = {}
        for trade in trade_history:
            strat = trade.get("strategy")
            pnl = trade.get("pnl", 0.0)
            perf.setdefault(strat, []).append(pnl)

        for strat, pnls in perf.items():
            avg = sum(pnls) / len(pnls) if pnls else 0.0
            self.weights[strat] = avg

        return self.weights
