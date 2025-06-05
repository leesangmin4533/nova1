from __future__ import annotations

from typing import Dict, Tuple


class StrategySelector:
    """Select trading strategy based on market sentiment."""

    def __init__(self) -> None:
        self.current_strategy: Tuple[str, Dict] | None = None
        self.weights: Dict[str, float] = {
            "reversal": 1.0,
            "swing": 1.0,
            "trend_follow": 1.0,
            "momentum": 1.0,
            "take_profit": 1.0,
            "hold": 1.0,
        }

    def select(self, sentiment: str) -> Tuple[str, Dict]:
        """Select a strategy ID and parameters based on sentiment."""
        mapping = {
            "EXTREME_FEAR": ("reversal", {"lookback": 20}),
            "FEAR": ("swing", {"risk": 0.02}),
            "NEUTRAL": ("trend_follow", {"risk": 0.03}),
            "GREED": ("momentum", {"risk": 0.04}),
            "EXTREME_GREED": ("take_profit", {"risk": 0.05}),
        }
        strategy, params = mapping.get(sentiment, ("hold", {}))
        weight = self.weights.get(strategy, 1.0)
        params = {**params, "weight": weight}
        self.current_strategy = (strategy, params)
        return self.current_strategy
