"""Agent that updates strategy weights based on performance."""

from typing import Dict, Any, Optional

from nova_strategy import adjust_weights


class LearningAgent:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize weights from configuration if provided."""
        if config and "scoring_weights" in config:
            self.weights: Dict[str, float] = {
                k: v.get("weight", 0.0)
                for k, v in config["scoring_weights"].items()
                if isinstance(v, dict)
            }
        else:
            # example initial weights for strategy conditions
            self.weights: Dict[str, float] = {}

    def update(self, failure_stats: Dict[str, Dict[str, int]]) -> Dict[str, float]:
        """Update strategy condition weights based on failure statistics."""
        self.weights = adjust_weights(self.weights, failure_stats)
        return self.weights
