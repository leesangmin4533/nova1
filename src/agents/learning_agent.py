"""Agent that updates strategy weights based on performance."""

from typing import Dict

from nova_strategy import adjust_weights


class LearningAgent:
    def __init__(self):
        # example initial weights for strategy conditions
        self.weights: Dict[str, float] = {}

    def update(self, failure_stats: Dict[str, Dict[str, int]]) -> Dict[str, float]:
        """Update strategy condition weights based on failure statistics."""
        self.weights = adjust_weights(self.weights, failure_stats)
        return self.weights
