from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class LearningAgent:
    weights: Dict[str, float] = field(default_factory=dict)

    def update(self, performance: Dict[str, float]) -> None:
        for strategy, score in performance.items():
            weight = self.weights.get(strategy, 1.0)
            self.weights[strategy] = weight + score
