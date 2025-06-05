class StrategySelector:
    """Select trading strategy based on market sentiment."""

    def __init__(self):
        self.current_strategy = None
        # basic score table for each strategy (0~1)
        self.strategy_scores = {
            "reversal": 0.5,
            "swing": 0.5,
            "trend_follow": 0.5,
            "momentum": 0.5,
            "take_profit": 0.5,
            "hold": 0.5,
        }

    def select(self, sentiment):
        """Select a strategy ID and parameters based on sentiment."""
        mapping = {
            "EXTREME_FEAR": ("reversal", {"lookback": 20}),
            "FEAR": ("swing", {"risk": 0.02}),
            "NEUTRAL": ("trend_follow", {"risk": 0.03}),
            "GREED": ("momentum", {"risk": 0.04}),
            "EXTREME_GREED": ("take_profit", {"risk": 0.05}),
        }

        base_strategy = mapping.get(sentiment, ("hold", {}))
        strat_id, params = base_strategy
        score = self.strategy_scores.get(strat_id, 0.5)
        params = dict(params)
        params["score"] = score
        self.current_strategy = (strat_id, params)
        return self.current_strategy
