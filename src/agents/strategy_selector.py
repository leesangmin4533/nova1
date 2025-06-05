from __future__ import annotations

"""Strategy selector based on market sentiment."""

from typing import Dict, Tuple


class StrategySelector:
    """Select trading strategy based on market sentiment."""

    def __init__(self) -> None:
        self.current_strategy: Tuple[str, dict] | None = None
        self.last_sentiment: str | None = None
        # simple score table, can be updated by LearningAgent
        self.strategy_scores: Dict[str, float] = {
            "reversal": 1.0,
            "swing": 1.0,
            "trend_follow": 1.0,
            "momentum": 1.0,
            "take_profit": 1.0,
            "hold": 1.0,
        }

    def select(self, sentiment: str) -> Tuple[str, dict]:
        """Select a strategy ID and parameters based on sentiment."""

        if sentiment == self.last_sentiment and self.current_strategy is not None:
            return self.current_strategy

        self.last_sentiment = sentiment

        mapping = {
            "EXTREME_FEAR": ("reversal", {"lookback": 20}),
            "FEAR": ("swing", {"risk": 0.02}),
            "NEUTRAL": ("trend_follow", {"risk": 0.03}),
            "GREED": ("momentum", {"risk": 0.04}),
            "EXTREME_GREED": ("take_profit", {"risk": 0.05}),
        }

        strat, params = mapping.get(sentiment, ("hold", {}))
        params = dict(params)
        params["score"] = self.strategy_scores.get(strat, 1.0)
        self.current_strategy = (strat, params)
        return self.current_strategy

    def update_score(self, strategy: str, score: float) -> None:
        """Update stored score for a strategy."""
        self.strategy_scores[strategy] = score
