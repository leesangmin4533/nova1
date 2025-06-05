"""Learning agent that updates strategy weights."""

from __future__ import annotations

from typing import Dict, Iterable, Mapping


class LearningAgent:
    """Agent that updates strategy weights based on performance."""

    def __init__(self) -> None:
        self.weights: Dict[str, float] = {}

    def update(self, trade_history: Iterable[Mapping[str, float]]) -> Dict[str, float]:
        """Update strategy weights based on past trade results."""
        for trade in trade_history:
            strat = trade.get("strategy")
            pnl = trade.get("pnl", 0.0)
            if strat is None:
                continue
            self.weights[strat] = self.weights.get(strat, 0.0) + pnl
        return self.weights
