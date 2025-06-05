"""Offline learning agent for strategy performance."""

from __future__ import annotations

from typing import Dict, List


class LearningAgent:
    """Agent that updates strategy weights based on performance."""

    def __init__(self) -> None:
        self.weights: Dict[str, float] = {}

    def update(self, trade_history: List[Dict]) -> Dict[str, float]:
        """Update strategy weights based on average returns."""
        totals: Dict[str, float] = {}
        counts: Dict[str, int] = {}
        for record in trade_history:
            strat = record.get("strategy_id")
            ret = record.get("return", 0.0)
            totals[strat] = totals.get(strat, 0.0) + ret
            counts[strat] = counts.get(strat, 0) + 1
        for strat in totals:
            self.weights[strat] = totals[strat] / counts[strat]
        return self.weights
