from __future__ import annotations

import asyncio
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .data.pipeline import MarketData


class Sentiment(Enum):
    EXTREME_FEAR = "EXTREME_FEAR"
    FEAR = "FEAR"
    NEUTRAL = "NEUTRAL"
    GREED = "GREED"
    EXTREME_GREED = "EXTREME_GREED"


def calculate_rsi(data: list[float], period: int = 14) -> float:
    if len(data) < period + 1:
        return 50.0
    gains = [max(0, data[i] - data[i - 1]) for i in range(1, period + 1)]
    losses = [max(0, data[i - 1] - data[i]) for i in range(1, period + 1)]
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - 100 / (1 + rs)


@dataclass
class MarketSentimentAgent:
    interval: float = 60.0
    data_history: list[float] | None = None
    sentiment: Optional[Sentiment] = None

    def __post_init__(self) -> None:
        if self.data_history is None:
            self.data_history = []

    async def run(self, stream: asyncio.Queue[MarketData]) -> None:
        while True:
            market_data = await stream.get()
            self.data_history.append(market_data.price)
            rsi = calculate_rsi(self.data_history)
            if rsi < 30:
                self.sentiment = Sentiment.EXTREME_FEAR
            elif rsi < 45:
                self.sentiment = Sentiment.FEAR
            elif rsi < 55:
                self.sentiment = Sentiment.NEUTRAL
            elif rsi < 70:
                self.sentiment = Sentiment.GREED
            else:
                self.sentiment = Sentiment.EXTREME_GREED
            stream.task_done()
            await asyncio.sleep(self.interval)
