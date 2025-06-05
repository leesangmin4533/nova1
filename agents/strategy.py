from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from .sentiment import Sentiment


@dataclass
class Strategy:
    id: str
    parameters: Dict[str, float]


@dataclass
class StrategySelector:
    strategies: Dict[Sentiment, Strategy]
    last_sentiment: Sentiment | None = None
    current_strategy: Strategy | None = None

    def select(self, sentiment: Sentiment) -> Strategy:
        if sentiment != self.last_sentiment:
            self.current_strategy = self.strategies.get(sentiment)
            self.last_sentiment = sentiment
        return self.current_strategy
