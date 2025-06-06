class StrategySelector:
    """Select trading strategy based on market sentiment."""

    def __init__(self):
        self.current_strategy = None
        self.strategy_scores = {
            "reversal": 1.0,
            "swing": 1.0,
            "trend_follow": 1.0,
            "momentum": 1.0,
            "take_profit": 1.0,
        }

    def update_scores(self, weights):
        """Update internal strategy scores from learning agent."""
        if not weights:
            return
        for name, score in weights.items():
            self.strategy_scores[name] = score

    def select(self, sentiment):
        """Select a strategy ID and parameters based on sentiment."""
        # Placeholder mapping
        mapping = {
            "EXTREME_FEAR": ("reversal", {"lookback": 20}),
            "FEAR": ("swing", {"risk": 0.02}),
            "NEUTRAL": ("trend_follow", {"risk": 0.03}),
            "GREED": ("momentum", {"risk": 0.04}),
            "EXTREME_GREED": ("take_profit", {"risk": 0.05}),
        }
        base = mapping.get(sentiment, ("hold", {}))
        name = base[0]
        score = self.strategy_scores.get(name, 1.0)
        params = dict(base[1])
        params["weight"] = score
        self.current_strategy = (name, params)
        return self.current_strategy
