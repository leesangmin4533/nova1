import time


class LearningAgent:
    """Agent that updates strategy weights based on performance."""

    def __init__(self):
        self.weights = {}
        self.history = []

    def record_trade(self, strategy: str, return_rate: float) -> None:
        """Store trade result for later evaluation."""
        self.history.append(
            {
                "strategy": strategy,
                "return": return_rate,
                "timestamp": time.time(),
            }
        )

    def update(self, trade_history=None):
        """Update strategy weights using recent one week of trades."""

        if trade_history is None:
            trade_history = self.history

        one_week_ago = time.time() - 7 * 24 * 3600
        recent = [t for t in trade_history if t.get("timestamp", 0) >= one_week_ago]

        alpha = 0.3
        for trade in recent:
            name = trade.get("strategy")
            ret = trade.get("return", 0)
            old = self.weights.get(name, 1.0)
            self.weights[name] = old + alpha * ret

        # remove strategies with consistently negative weights
        for name, weight in list(self.weights.items()):
            if weight < -1:
                del self.weights[name]

        return self.weights

    def adjust_from_signal(self, strategy: str, score_percent: float, confidence: float | None) -> None:
        """Lightweight online adjustment using condition score and confidence."""
        conf = confidence if confidence is not None else 1.0
        weight = self.weights.get(strategy, 1.0)
        weight += 0.01 * (score_percent / 100.0) * conf
        self.weights[strategy] = weight
