class StrategySelector:
    """Select trading strategy based on market sentiment for scalping."""

    def __init__(self):
        self.current_strategy = None

    def select(self, sentiment):
        """Select a strategy ID and parameters based on sentiment."""
        mapping = {
            "EXTREME_FEAR": ("scalp_reversal", {"lookback": 20, "risk": 0.01}),
            "FEAR": ("scalp_pullback", {"risk": 0.015}),
            "NEUTRAL": ("scalp_trend", {"risk": 0.02}),
            "GREED": ("scalp_momentum", {"risk": 0.025}),
            "EXTREME_GREED": ("scalp_take_profit", {"risk": 0.03}),
        }
        self.current_strategy = mapping.get(sentiment, ("hold", {}))
        return self.current_strategy
