from typing import Dict, Tuple, Any


class StrategySelector:
    """Select trading strategy based on market sentiment."""

    def __init__(self):
        self.current_strategy: Tuple[str, Dict[str, Any]] = ("hold", {})
        self.scores: Dict[str, float] = {
            "reversal": 0.5,
            "swing": 0.6,
            "trend_follow": 0.7,
            "momentum": 0.55,
            "take_profit": 0.65,
            "hold": 0.5,
        }

    def select(self, sentiment: str) -> Tuple[str, Dict[str, Any]]:
        """Select a strategy ID and parameters based on sentiment and scores."""
        mapping = {
            "EXTREME_FEAR": [("reversal", {"lookback": 20}), ("swing", {"risk": 0.02})],
            "FEAR": [("swing", {"risk": 0.02})],
            "NEUTRAL": [("trend_follow", {"risk": 0.03})],
            "GREED": [("momentum", {"risk": 0.04}), ("trend_follow", {"risk": 0.03})],
            "EXTREME_GREED": [("take_profit", {"risk": 0.05})],
        }
        candidates = mapping.get(sentiment, [("hold", {})])
        # choose candidate with highest score
        best = max(candidates, key=lambda c: self.scores.get(c[0], 0))
        self.current_strategy = best
        return self.current_strategy
