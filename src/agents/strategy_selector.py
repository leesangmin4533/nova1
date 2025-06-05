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
        self.win_rates: Dict[str, float] = {
            "reversal": 0.5,
            "swing": 0.55,
            "trend_follow": 0.6,
            "momentum": 0.52,
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
        # choose candidate with highest combined score
        def value(c):
            sid = c[0]
            score = self.scores.get(sid, 0)
            win = self.win_rates.get(sid, 0)
            return 0.5 * score + 0.5 * win

        best = max(candidates, key=value)
        self.current_strategy = best
        return self.current_strategy
