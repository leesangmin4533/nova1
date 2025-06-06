class LearningAgent:
    """Agent that updates strategy weights based on performance."""

    def __init__(self):
        self.weights = {}

    def update(self, trade_history):
        """Update strategy weights using EWMA of recent positive returns."""

        alpha = 0.3
        for trade in trade_history:
            name = trade.get("strategy")
            ret = trade.get("return", 0)
            if ret <= 0:
                continue
            old = self.weights.get(name, 0.0)
            self.weights[name] = alpha * ret + (1 - alpha) * old

        return self.weights
