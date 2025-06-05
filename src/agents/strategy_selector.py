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
            "hold": 1.0,
        }

    def select(self, sentiment):
        """Select a strategy ID and parameters based on sentiment."""
        mapping = {
            "EXTREME_FEAR": "reversal",
            "FEAR": "swing",
            "NEUTRAL": "trend_follow",
            "GREED": "momentum",
            "EXTREME_GREED": "take_profit",
        }
        strategy_id = mapping.get(sentiment, "hold")
        params = {"risk": 0.03}

        self.current_strategy = (strategy_id, params)
        return self.current_strategy

    def update_scores(self, new_scores):
        """Update internal strategy weights from LearningAgent."""
        self.strategy_scores.update(new_scores)
